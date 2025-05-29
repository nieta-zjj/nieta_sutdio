"""
子任务处理Actor模块

接收子任务ID，处理单个图像生成任务并返回结果
"""

import logging
import dramatiq
from dramatiq.middleware import CurrentMessage
from typing import Dict, Any, Optional, List, Tuple
import traceback
from datetime import datetime
import json
import time
import random
import asyncio
import math
import os
import httpx

from backend.core.config import settings
from backend.models.db.dramatiq_base import DramatiqBaseModel
from backend.models.db.subtasks import Subtask, SubtaskStatus
from backend.core.app import initialize_app

# 禁用 httpx 的 info 级别日志
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


class ImageClient:
    """
    图像生成客户端

    实现图像生成服务的调用
    """
    def __init__(self):
        """初始化图像生成服务"""
        # 使用环境变量中的NIETA_XTOKEN
        self.x_token = os.environ.get("NIETA_XTOKEN", "")
        if not self.x_token:
            logger.warning("环境变量中未设置NIETA_XTOKEN，请确保设置正确的API令牌")
            raise ValueError("环境变量中未设置NIETA_XTOKEN")

        # API端点
        self.api_url = "https://api.talesofai.cn/v3/make_image"
        self.task_status_url = "https://api.talesofai.cn/v1/artifact/task/{task_uuid}"

        # Lumina API端点
        self.lumina_api_url = "https://ops.api.talesofai.cn/v3/make_image"
        self.lumina_task_status_url = "https://ops.api.talesofai.cn/v1/artifact/task/{task_uuid}"

        # 轮询配置
        self.max_polling_attempts = int(os.getenv("IMAGE_MAX_POLLING_ATTEMPTS", "30"))  # 最大轮询次数
        self.polling_interval = float(os.getenv("IMAGE_POLLING_INTERVAL", "2.0"))  # 轮询间隔（秒）

        # Lumina轮询配置
        self.lumina_max_polling_attempts = int(os.getenv("LUMINA_MAX_POLLING_ATTEMPTS", "50"))  # Lumina最大轮询次数
        self.lumina_polling_interval = float(os.getenv("LUMINA_POLLING_INTERVAL", "3.0"))  # Lumina轮询间隔（秒）

        # 默认请求头
        self.default_headers = {
            "Content-Type": "application/json",
            "x-platform": "nieta-app/web",
            "X-Token": self.x_token
        }

    async def generate_image(self,
                            prompts: List[Dict[str, Any]],
                            width: int,
                            height: int,
                            seed: int = None,
                            use_polish: bool = False,
                            is_lumina: bool = False,
                            lumina_model_name: str = None,
                            lumina_cfg: float = None,
                            lumina_step: int = None) -> Dict[str, Any]:
        """
        生成图像

        Args:
            prompts: 提示词列表
            width: 图像宽度
            height: 图像高度
            seed: 随机种子
            is_lumina: 是否使用Lumina模型
            lumina_model_name: Lumina模型名称
            lumina_cfg: Lumina配置参数
            lumina_step: Lumina步数

        Returns:
            生成结果
        """

        # 生成随机种子（如果未提供）
        if seed is None or seed == 0:
            seed = random.randint(1, 2147483647)

        # 选择API端点
        api_url = self.lumina_api_url if is_lumina else self.api_url
        task_status_url = self.lumina_task_status_url if is_lumina else self.task_status_url

        final_prompts = []
        for prompt in prompts:
            if prompt['type'] == 'freetext':
                final_prompt = {
                    "type": "freetext",
                    "value": prompt['value'],
                    "weight": prompt['weight']
                }
            else:
                final_prompt = {
                    "type": prompt['type'],
                    "value": prompt['value'],
                    "uuid": prompt['uuid'],
                    "weight": prompt['weight'],
                    "name": prompt['name'],
                    "img_url": prompt['img_url'],
                    "domain": "",
                    "parent": "",
                    "label": None,
                    "sort_index": 0,
                    "status": "IN_USE",
                    "polymorphi_values": {},
                    "sub_type": None
                }
            final_prompts.append(final_prompt)

        if is_lumina:
            final_prompts.append({
                    "type": 'elementum',
                    "value": 'b5edccfe-46a2-4a14-a8ff-f4d430343805',
                    "uuid": 'b5edccfe-46a2-4a14-a8ff-f4d430343805',
                    "weight": 1.0,
                    "name": "lumina1",
                    "img_url": "https://oss.talesofai.cn/picture_s/1y7f53e6itfn_0.jpeg",
                    "domain": "",
                    "parent": "",
                    "label": None,
                    "sort_index": 0,
                    "status": "IN_USE",
                    "polymorphi_values": {},
                    "sub_type": None
            })

        # 构建请求载荷
        payload = {
            "storyId": "",
            "jobType": "universal",
            "width": width,
            "height": height,
            "rawPrompt": final_prompts,
            "seed": seed,
            "meta": {"entrance": "PICTURE,PURE"},
            "context_model_series": None,
            "negative_freetext": "",
            "advanced_translator": use_polish
        }

        # 如果是Lumina任务，添加Lumina特定参数
        if is_lumina:
            client_args = {}
            if lumina_model_name:
                client_args["ckpt_name"] = lumina_model_name
            if lumina_cfg is not None:
                client_args["cfg"] = lumina_cfg
            if lumina_step is not None:
                client_args["steps"] = lumina_step

            if client_args:
                payload["client_args"] = client_args

        try:
            # 调用API获取UUID
            task_info = f"宽度={width}, 高度={height}, 种子={seed}"
            start_time = time.time()

            async with httpx.AsyncClient(timeout=300.0) as client:  # 5分钟超时
                response = await client.post(
                    api_url,
                    json=payload,
                    headers=self.default_headers
                )

                # 检查响应状态
                if response.status_code == 451:
                    logger.warning(f"图像生成API返回451状态，内容不合规 {task_info}")
                    return {
                        "success": False,
                        "error": "文本不合规",
                        "is_censored": True
                    }

                # 检查其他错误状态码
                if response.status_code != 200:
                    logger.error(f"图像生成API返回错误状态码: {response.status_code} {task_info}")
                    return {
                        "success": False,
                        "error": f"API请求失败，状态码: {response.status_code}"
                    }

                # 200状态码，获取UUID
                content = response.text.strip()
                elapsed_time = time.time() - start_time
                logger.debug(f"图像生成API请求成功 {task_info}, 耗时: {elapsed_time:.2f}秒")

                # 去掉引号并获取UUID字符串
                task_uuid = content.replace('"', '')

            if not task_uuid:
                return {"success": False, "error": "API返回的任务UUID为空"}

            # 轮询任务状态
            max_attempts = self.lumina_max_polling_attempts if is_lumina else self.max_polling_attempts
            polling_interval = self.lumina_polling_interval if is_lumina else self.polling_interval
            status_url = task_status_url.format(task_uuid=task_uuid)

            for attempt in range(1, max_attempts + 1):
                try:
                    async with httpx.AsyncClient(timeout=30.0) as client:
                        response = await client.get(
                            status_url,
                            headers=self.default_headers
                        )

                        response.raise_for_status()
                        result = response.json()

                        # 检查任务状态
                        task_status = result.get("task_status")

                        if task_status == "SUCCESS":
                            # 提取图像URL
                            artifacts = result.get("artifacts", [])
                            if artifacts and len(artifacts) > 0:
                                image_url = artifacts[0].get("url")
                                if image_url:
                                    return {
                                        "success": True,
                                        "data": {
                                            "image_url": image_url,
                                            "seed": seed,
                                            "is_lumina": is_lumina,
                                            "width": width,
                                            "height": height
                                        }
                                    }
                            return {"success": False, "error": "无法从结果中提取图像URL"}

                        elif task_status == "FAILURE":
                            error_msg = result.get("error", "未知错误")
                            return {"success": False, "error": error_msg, "task_status": "FAILURE"}
                        elif task_status == "ILLEGAL_IMAGE":
                            return {"success": False, "error": "图片不合规", "task_status": "ILLEGAL_IMAGE"}
                        elif task_status == "TIMEOUT":
                            return {"success": False, "error": "任务超时", "task_status": "TIMEOUT"}
                        elif task_status in ["SUCCESS", "FAILURE", "ILLEGAL_IMAGE", "TIMEOUT"]:
                            # 这些状态已处理，不应到达这里
                            break

                        # 如果不是最后一次尝试，则等待下一次轮询
                        if attempt < max_attempts:
                            await asyncio.sleep(polling_interval)

                except Exception as e:
                    # 对于网络错误等临时性错误，只有在最后一次尝试时才抛出异常
                    if attempt >= max_attempts:
                        logger.error(f"轮询任务状态失败，已达到最大轮询次数: {max_attempts}")
                        raise e
                    else:
                        # 网络错误等临时性问题，记录警告并继续轮询
                        logger.warning(f"轮询请求异常: {str(e)}, 尝试次数: {attempt}/{max_attempts}, 将继续重试")
                        await asyncio.sleep(polling_interval)

            # 如果循环正常结束但仍未返回结果，返回PENDING状态
            return {"success": False, "error": "轮询超时但任务仍在处理中", "task_status": "PENDING"}

        except Exception as e:
            logger.error(traceback.format_exc())
            return {
                "success": False,
                "error": str(e)
            }

    async def calculate_dimensions(self, ratio: str) -> Tuple[int, int]:
        """
        根据比例计算宽高，确保总像素数接近 1024²

        Args:
            ratio: 比例字符串，如"1:1"、"4:3"等

        Returns:
            宽度和高度
        """
        target_pixels = 1024 * 1024

        parts = ratio.split(":")
        if len(parts) == 2:
            try:
                width_ratio = float(parts[0])
                height_ratio = float(parts[1])
                x = math.sqrt(target_pixels / (width_ratio * height_ratio))
                width = width_ratio * x
                height = height_ratio * x
                width = round(width / 8) * 8
                height = round(height / 8) * 8
                return int(width), int(height)
            except Exception as e:
                logger.warning(f"计算比例 {ratio} 的尺寸时出错: {str(e)}")

        return 1024, 1024

def update_subtask_status(subtask_id: str, status: str, error: str = None, result: str = None) -> bool:
    """
    更新子任务状态

    Args:
        subtask_id: 子任务ID
        status: 状态
        error: 错误信息
        result: 结果URL

    Returns:
        是否更新成功
    """
    # 初始化数据库连接
    DramatiqBaseModel.initialize_database()

    # 同时初始化BaseModel的数据库连接，因为Subtask模型继承自BaseModel
    try:
        from backend.core.app import initialize_app
        initialize_app()
    except Exception as base_init_error:
        logger.error(f"更新子任务状态时初始化BaseModel数据库连接失败: {str(base_init_error)}")
        raise

    # 获取子任务
    subtask = Subtask.get_or_none(Subtask.id == subtask_id)
    if not subtask:
        logger.error(f"子任务不存在: {subtask_id}")
        return False

    # 更新状态
    subtask.status = status
    subtask.updated_at = datetime.now()

    # 如果是开始处理，更新开始时间
    if status == SubtaskStatus.PROCESSING.value:
        subtask.started_at = datetime.now()

    # 如果是完成或失败，更新完成时间和其他信息
    if status in [SubtaskStatus.COMPLETED.value, SubtaskStatus.FAILED.value]:
        subtask.completed_at = datetime.now()

        if error:
            subtask.error = error

        if result:
            subtask.result = result

    # 保存更新
    subtask.save()
    return True


async def process_subtask(subtask_id: str) -> Dict[str, Any]:
    """
    处理子任务

    Args:
        subtask_id: 子任务ID

    Returns:
        处理结果
    """
    # 初始化数据库连接
    DramatiqBaseModel.initialize_database()
    from backend.core.app import initialize_app
    initialize_app()

    # 获取子任务数据
    subtask = Subtask.get_or_none(Subtask.id == subtask_id)
    if not subtask:
        logger.error(f"子任务不存在: {subtask_id}")
        return {
            "status": "failed",
            "error": f"子任务不存在: {subtask_id}"
        }

    # 检查重试次数，如果超过10次直接失败
    if subtask.error_retry_count >= 10:
        logger.warning(f"[{subtask_id}] 重试次数已达到10次，标记任务为失败")
        update_subtask_status(
            subtask_id=subtask_id,
            status=SubtaskStatus.FAILED.value,
            error=subtask.error or "重试次数超过10次"
        )
        return {
            "status": "failed",
            "error": "重试次数超过10次"
        }

    # 更新子任务状态为处理中
    update_subtask_status(subtask_id, SubtaskStatus.PROCESSING.value)

    try:
        # 提取任务参数
        prompts = subtask.prompts
        ratio = subtask.ratio
        seed = subtask.seed
        use_polish = subtask.use_polish
        is_lumina = subtask.is_lumina
        lumina_model_name = subtask.lumina_model_name
        lumina_cfg = subtask.lumina_cfg
        lumina_step = subtask.lumina_step

        # 记录任务参数
        logger.debug(f"子任务参数: ratio={ratio}, seed={seed}, use_polish={use_polish}, is_lumina={is_lumina}")
        if is_lumina:
            logger.debug(f"Lumina参数: model={lumina_model_name}, cfg={lumina_cfg}, step={lumina_step}")

        # 创建图像客户端
        image_client = ImageClient()

        # 计算宽高
        width, height = await image_client.calculate_dimensions(ratio)

        logger.debug(f"开始生成图像: 子任务ID={subtask_id}, 宽度={width}, 高度={height}, 种子={seed}")

        # 生成图像
        result = await image_client.generate_image(
            prompts=prompts,
            width=width,
            height=height,
            seed=seed,
            use_polish=use_polish,
            is_lumina=is_lumina,
            lumina_model_name=lumina_model_name,
            lumina_cfg=lumina_cfg,
            lumina_step=lumina_step
        )

        if not result.get("success"):
            error_msg = result.get('error', '未知错误')
            is_censored = result.get('is_censored', False)
            task_status = result.get('task_status')

            if is_censored:
                # 451状态码，不触发重试
                logger.warning(f"[{subtask_id}] 图像生成触发内容审核(451): {error_msg}")
                update_subtask_status(
                    subtask_id=subtask_id,
                    status=SubtaskStatus.FAILED.value,
                    error="文本不合规"
                )
                return {
                    "status": "failed",
                    "error": "文本不合规"
                }
            elif task_status in ["TIMEOUT", "FAILURE"]:
                # TIMEOUT或FAILURE状态，触发重试
                current_retry_count = getattr(subtask, 'error_retry_count', 0)
                if task_status == "TIMEOUT":
                    error_msg = f"第{current_retry_count + 1}次重试TIMEOUT"

                logger.warning(f"[{subtask_id}] 图像生成失败，将进行重试: {error_msg}")
                update_subtask_status(
                    subtask_id=subtask_id,
                    status=SubtaskStatus.FAILED.value,
                    error=error_msg
                )
                raise Exception(error_msg)
            else:
                # 其他错误（如ILLEGAL_IMAGE），不触发重试
                logger.warning(f"[{subtask_id}] 图像生成失败，不进行重试: {error_msg}")
                update_subtask_status(
                    subtask_id=subtask_id,
                    status=SubtaskStatus.FAILED.value,
                    error=error_msg
                )
                return {
                    "status": "failed",
                    "error": error_msg
                }

        # 提取图像URL
        image_url = result.get("data", {}).get("image_url")
        if not image_url:
            raise Exception("无法从结果中获取图像URL")

        # 获取实际使用的种子（可能是随机生成的）
        actual_seed = result.get("data", {}).get("seed", seed)

        logger.debug(f"图像生成成功: 子任务ID={subtask_id}, 图像URL={image_url}, 种子={actual_seed}")

        # 更新子任务状态为已完成
        update_subtask_status(
            subtask_id=subtask_id,
            status=SubtaskStatus.COMPLETED.value,
            result=image_url
        )

        # 返回结果
        return {
            "status": "completed",
            "result": image_url,
            "seed": actual_seed
        }

    except Exception as e:
        # 所有其他异常都触发重试
        error_stack = traceback.format_exc()
        error_msg = f"图像生成失败: {str(e)}"
        logger.error(f"子任务 {subtask_id} {error_msg}\n{error_stack}")

        # 更新子任务状态为失败
        update_subtask_status(
            subtask_id=subtask_id,
            status=SubtaskStatus.FAILED.value,
            error=error_stack
        )

        # 触发重试
        raise Exception(error_msg)

@dramatiq.actor(
    queue_name=settings.SUBTASK_QUEUE,  # 使用子任务队列
    max_retries=settings.MAX_RETRIES,  # 最多重试3次
    time_limit=300000,  # 300秒，考虑到图像生成可能需要较长时间
)
def test_run_subtask(subtask_id: str):
    """
    处理单个子任务

    Args:
        subtask_id: 子任务ID
    """
    # 获取当前重试次数
    message = CurrentMessage.get_current_message()
    retry_count = message.options.get("retries", 0) if message else 0

    logger.info(f"[{subtask_id}] 子任务开始执行 (重试次数: {retry_count})")

    # 初始化数据库
    DramatiqBaseModel.initialize_database()
    initialize_app()

    if retry_count > 0:
        try:
            subtask = Subtask.get_or_none(Subtask.id == subtask_id)
            if subtask:
                subtask.error_retry_count = retry_count
                subtask.save()
                logger.debug(f"[{subtask_id}] 更新子任务重试计数: {retry_count}")
        except Exception as e:
            logger.error(f"[{subtask_id}] 更新重试计数失败: {str(e)}")

    # 使用事件循环运行异步处理函数
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        # 如果没有事件循环，创建一个新的
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    # 运行异步处理函数
    result = loop.run_until_complete(process_subtask(subtask_id))

    logger.debug(f"[{subtask_id}] 子任务执行完成: {result.get('status')}")

    return result

@dramatiq.actor(
    queue_name=settings.SUBTASK_OPS_QUEUE,  # 使用Lumina子任务队列
    max_retries=0,  # 最多重试3次
    time_limit=600000,  # 600秒，考虑到Lumina图像生成可能需要更长时间
)
def test_run_lumina_subtask(subtask_id: str):
    """
    处理Lumina子任务（与普通子任务相同，但使用不同的队列和超时设置）

    Args:
        subtask_id: 子任务ID
    """
    return test_run_subtask(subtask_id)


