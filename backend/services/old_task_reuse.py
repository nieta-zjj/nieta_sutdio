"""
旧任务复用服务
处理特定用户的旧格式任务数据复用功能
"""

import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

# 特定用户ID，需要特殊处理的旧格式数据
OLD_FORMAT_USER_ID = "33a5e309-4569-452e-88be-7155bc87488f"


def convert_old_variables_to_new_format(variables_map: Dict[str, Any]) -> Dict[str, Any]:
    """
    将旧的variables_map格式转换为新的任务配置格式

    Args:
        variables_map: 旧格式的变量映射数据

    Returns:
        新格式的任务配置数据
    """
    try:
        logger.info("开始转换旧格式变量数据")

        # 初始化新格式数据结构
        new_config = {
            "prompts": [],
            "ratio": None,
            "seed": None,
            "use_polish": None,
            "is_lumina": None,
            "lumina_model_name": None,
            "lumina_cfg": None,
            "lumina_step": None,
            "priority": 1
        }

        # 用于记录是否检测到lumina特征
        has_lumina_elementum = False

        # 遍历变量映射
        for var_key, var_data in variables_map.items():
            if not isinstance(var_data, dict):
                continue

            var_name = var_data.get("name", "")
            var_type = var_data.get("type", "")
            var_values = var_data.get("values", [])

            logger.info(f"处理变量: {var_key}, 名称: {var_name}, 类型: {var_type}, 值数量: {len(var_values)}")

            if var_type == "prompt":
                # 转换prompt类型变量
                converted_prompt = convert_prompt_variable(var_key, var_name, var_values)
                if converted_prompt:
                    new_config["prompts"].append(converted_prompt)

            elif var_type == "ratio":
                # 转换ratio类型变量
                converted_ratio = convert_ratio_variable(var_key, var_name, var_values)
                if converted_ratio:
                    new_config["ratio"] = converted_ratio

        # 检查是否需要设置is_lumina为true的特殊逻辑
        # 如果prompts中存在type为"elementum"且name为"lumina1"的item，则设置is_lumina为true
        for var_key, var_data in variables_map.items():
            if isinstance(var_data, dict):
                var_values = var_data.get("values", [])
                for value_item in var_values:
                    if (isinstance(value_item, dict) and
                        value_item.get("type") == "elementum" and
                        value_item.get("name") == "lumina1"):
                        has_lumina_elementum = True
                        logger.info(f"检测到lumina1 elementum特征，设置is_lumina为true")
                        break
                if has_lumina_elementum:
                    break

        # 设置默认参数值
        new_config["seed"] = {
            "type": "seed",
            "value": 1,
            "is_variable": False,
            "format": "int"
        }

        new_config["use_polish"] = {
            "type": "use_polish",
            "value": False,
            "is_variable": False,
            "format": "bool"
        }

        new_config["is_lumina"] = {
            "type": "is_lumina",
            "value": has_lumina_elementum,  # 根据检测结果设置
            "is_variable": False,
            "format": "bool"
        }

        new_config["lumina_model_name"] = {
            "type": "lumina_model_name",
            "value": None,
            "is_variable": False,
            "format": "string"
        }

        new_config["lumina_cfg"] = {
            "type": "lumina_cfg",
            "value": 5.5,
            "is_variable": False,
            "format": "float"
        }

        new_config["lumina_step"] = {
            "type": "lumina_step",
            "value": 30,
            "is_variable": False,
            "format": "int"
        }

        logger.info(f"转换完成，生成了 {len(new_config['prompts'])} 个提示词，is_lumina: {has_lumina_elementum}")
        return new_config

    except Exception as e:
        logger.error(f"转换旧格式变量数据失败: {str(e)}")
        raise


def convert_prompt_variable(var_key: str, var_name: str, var_values: List[Dict]) -> Dict[str, Any]:
    """
    转换prompt类型变量为新格式

    Args:
        var_key: 变量键名
        var_name: 变量名称
        var_values: 变量值列表

    Returns:
        新格式的prompt配置
    """
    try:
        # 过滤掉空值
        valid_values = [v for v in var_values if v.get("value", "").strip()]

        if not valid_values:
            logger.warning(f"变量 {var_key} 没有有效值，跳过")
            return None

        if len(valid_values) == 1:
            # 单个值，不是变量
            return {
                "type": "freetext",
                "value": valid_values[0]["value"],
                "weight": 1.0,
                "is_variable": False
            }
        else:
            # 多个值，作为变量处理
            variable_values = []
            for val in valid_values:
                variable_values.append({
                    "type": "freetext",
                    "value": val["value"],
                    "weight": 1.0
                })

            return {
                "type": "freetext",
                "value": "",
                "weight": 1.0,
                "is_variable": True,
                "variable_name": var_name or f"变量{var_key}",
                "variable_id": var_key,
                "variable_values": variable_values
            }

    except Exception as e:
        logger.error(f"转换prompt变量 {var_key} 失败: {str(e)}")
        return None


def convert_ratio_variable(var_key: str, var_name: str, var_values: List[Dict]) -> Dict[str, Any]:
    """
    转换ratio类型变量为新格式

    Args:
        var_key: 变量键名
        var_name: 变量名称
        var_values: 变量值列表

    Returns:
        新格式的ratio配置
    """
    try:
        # 过滤掉空值
        valid_values = [v for v in var_values if v.get("value", "").strip()]

        if not valid_values:
            logger.warning(f"比例变量 {var_key} 没有有效值，使用默认值")
            return {
                "type": "ratio",
                "value": "1:1",
                "is_variable": False,
                "format": "string"
            }

        if len(valid_values) == 1:
            # 单个值，不是变量
            return {
                "type": "ratio",
                "value": valid_values[0]["value"],
                "is_variable": False,
                "format": "string"
            }
        else:
            # 多个值，作为变量处理
            variable_values = []
            for val in valid_values:
                variable_values.append(val["value"])

            return {
                "type": "ratio",
                "value": valid_values[0]["value"],  # 使用第一个值作为默认值
                "is_variable": True,
                "variable_name": var_name or f"比例变量{var_key}",
                "variable_id": var_key,
                "variable_values": variable_values,
                "format": "string"
            }

    except Exception as e:
        logger.error(f"转换ratio变量 {var_key} 失败: {str(e)}")
        return {
            "type": "ratio",
            "value": "1:1",
            "is_variable": False,
            "format": "string"
        }


def is_old_format_user(user_id: str) -> bool:
    """
    检查是否为需要特殊处理的旧格式用户

    Args:
        user_id: 用户ID

    Returns:
        是否为旧格式用户
    """
    return str(user_id) == OLD_FORMAT_USER_ID


def generate_old_task_reuse_config(task) -> Dict[str, Any]:
    """
    为旧格式任务生成复用配置

    Args:
        task: 任务对象

    Returns:
        复用配置数据
    """
    try:
        logger.info(f"为旧格式任务 {task.id} 生成复用配置")

        # 检查是否有variables_map数据
        variables_map = getattr(task, 'variables_map', None)
        if not variables_map:
            logger.warning(f"任务 {task.id} 没有variables_map数据")
            variables_map = {}

        # 转换为新格式
        converted_config = convert_old_variables_to_new_format(variables_map)

        # 构建复用配置数据
        reuse_config = {
            "task_id": str(task.id),
            "task_name": task.name,
            "name": f"复用-{task.name}",  # 前端显示用的新任务名
            "prompts": converted_config["prompts"],
            "ratio": converted_config["ratio"],
            "seed": converted_config["seed"],
            "use_polish": converted_config["use_polish"],
            "is_lumina": converted_config["is_lumina"],
            "lumina_model_name": converted_config["lumina_model_name"],
            "lumina_cfg": converted_config["lumina_cfg"],
            "lumina_step": converted_config["lumina_step"],
            "priority": converted_config["priority"],
            "created_at": task.created_at,
            "original_username": task.user.username if task.user else "未知用户",
            "is_old_format": True  # 标识这是从旧格式转换的数据
        }

        logger.info(f"旧格式任务 {task.id} 复用配置生成成功")
        return reuse_config

    except Exception as e:
        logger.error(f"生成旧格式任务复用配置失败: {str(e)}")
        raise