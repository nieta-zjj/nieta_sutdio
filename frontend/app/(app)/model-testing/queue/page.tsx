"use client";

import React, { useState, useEffect } from "react";
import {
  Card,
  CardBody,
  CardHeader,
  Chip,
  Progress,
  Spinner,
  Button,
  Divider,
  Badge,
  ScrollShadow,
  Modal,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalFooter,
  useDisclosure
} from "@heroui/react";
import { Icon } from "@iconify/react";
import { getTasks, forceCompleteTask, forceCancelTask } from "@/utils/apiClient";
import { TaskListItem, APIResponse } from "@/types/task";
import { CustomProgress } from "@/components/ui/custom-progress";
import { toast } from "sonner";

export default function QueuePage() {
  const [queueTasks, setQueueTasks] = useState<TaskListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [total, setTotal] = useState(0);
  const [operatingTaskId, setOperatingTaskId] = useState<string | null>(null);
  const { isOpen, onOpen, onClose } = useDisclosure();
  const [confirmAction, setConfirmAction] = useState<{
    type: 'complete' | 'cancel';
    taskId: string;
    taskName: string;
  } | null>(null);

  // 格式化时间
  const formatTime = (timeStr: string) => {
    return new Date(timeStr).toLocaleString("zh-CN", {
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit"
    });
  };

  // 计算执行时间
  const getExecutionTime = (createdAt: string, completedAt?: string) => {
    const start = new Date(createdAt);
    const end = completedAt ? new Date(completedAt) : new Date();
    const diffMs = end.getTime() - start.getTime();

    const hours = Math.floor(diffMs / (1000 * 60 * 60));
    const minutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));
    const seconds = Math.floor((diffMs % (1000 * 60)) / 1000);

    if (hours > 0) {
      return `${hours}h ${minutes}m`;
    } else if (minutes > 0) {
      return `${minutes}m ${seconds}s`;
    } else {
      return `${seconds}s`;
    }
  };

  // 强制操作确认
  const handleForceAction = (type: 'complete' | 'cancel', taskId: string, taskName: string) => {
    setConfirmAction({ type, taskId, taskName });
    onOpen();
  };

  // 执行强制操作
  const executeForceAction = async () => {
    if (!confirmAction) return;

    try {
      setOperatingTaskId(confirmAction.taskId);

      if (confirmAction.type === 'complete') {
        await forceCompleteTask(confirmAction.taskId);
        toast.success(`任务 "${confirmAction.taskName}" 已强制完成`);
      } else {
        await forceCancelTask(confirmAction.taskId);
        toast.success(`任务 "${confirmAction.taskName}" 已强制取消`);
      }

      // 刷新任务列表
      await loadQueueTasks(true);
    } catch (error: any) {
      console.error("强制操作失败:", error);
      toast.error(`强制操作失败: ${error.message || "未知错误"}`);
    } finally {
      setOperatingTaskId(null);
      onClose();
      setConfirmAction(null);
    }
  };

  // 加载队列任务
  const loadQueueTasks = async (isRefresh = false) => {
    try {
      if (isRefresh) {
        setRefreshing(true);
      } else {
        setLoading(true);
      }

      // 获取正在执行和排队的任务
      const [processingRes, pendingRes] = await Promise.all([
        getTasks(1, 50, "processing", undefined, undefined),
        getTasks(1, 50, "pending", undefined, undefined)
      ]);

      const allTasks = [
        ...(processingRes.data.tasks || []),
        ...(pendingRes.data.tasks || [])
      ];

      // 按创建时间排序（最新的在前）
      allTasks.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());

      setQueueTasks(allTasks);
      setTotal(allTasks.length);
    } catch (error) {
      console.error("加载队列任务失败:", error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  // 手动刷新
  const handleRefresh = () => {
    loadQueueTasks(true);
  };

  // 初始加载和定时刷新
  useEffect(() => {
    loadQueueTasks();
    const interval = setInterval(() => loadQueueTasks(true), 15000); // 改为15秒
    return () => clearInterval(interval);
  }, []);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "processing":
        return "solar:play-circle-linear";
      case "pending":
        return "solar:clock-circle-linear";
      default:
        return "solar:question-circle-linear";
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "processing":
        return "text-primary";
      case "pending":
        return "text-warning";
      default:
        return "text-default-400";
    }
  };

  return (
    <div className="w-full px-6 py-6">
      <div className="w-full space-y-6">
        {/* 页面标题 */}
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <h2 className="text-xl font-medium mb-2">任务队列</h2>
            <p className="text-default-500 text-sm">实时显示正在执行和排队的任务（每15秒自动刷新）</p>
          </div>

          <div className="flex items-center gap-3 ml-6">
            <Button
              color="primary"
              variant="flat"
              size="sm"
              onPress={handleRefresh}
              isLoading={refreshing}
              startContent={!refreshing ? <Icon icon="solar:refresh-linear" /> : undefined}
            >
              {refreshing ? "刷新中..." : "刷新"}
            </Button>
          </div>
        </div>

        {/* 任务队列列表 */}
        <Card className="w-full">
          <CardBody className="p-4">
            {loading ? (
              <div className="flex items-center justify-center py-12">
                <Spinner label="加载队列中..." />
              </div>
            ) : queueTasks.length === 0 ? (
              <div className="text-center py-12 text-default-400">
                <Icon icon="solar:sleep-linear" className="w-16 h-16 mx-auto mb-4" />
                <p className="text-lg">当前没有排队或执行中的任务</p>
                <p className="text-sm">所有任务都已完成</p>
              </div>
            ) : (
              <ScrollShadow className="max-h-[70vh]">
                <div className="space-y-3">
                  {queueTasks.map((task, index) => (
                    <div key={task.id} className="relative">
                      {/* 时间线连接线 */}
                      {index < queueTasks.length - 1 && (
                        <div className="absolute left-5 top-14 w-0.5 h-6 bg-default-200 z-0" />
                      )}

                      <Card className="relative z-10 hover:shadow-md transition-shadow w-full">
                        <CardBody className="p-4">
                          <div className="flex items-start gap-4">
                            {/* 状态图标 */}
                            <div className={`flex-shrink-0 w-10 h-10 rounded-full bg-default-100 flex items-center justify-center ${getStatusColor(task.status)}`}>
                              <Icon
                                icon={getStatusIcon(task.status)}
                                className={`w-5 h-5 ${task.status === 'processing' ? 'animate-pulse' : ''}`}
                              />
                            </div>

                            {/* 任务信息 */}
                            <div className="flex-1 min-w-0">
                              <div className="flex items-start justify-between mb-2">
                                <div className="flex-1 pr-4">
                                  <h3 className="font-semibold text-lg truncate mb-1">{task.name}</h3>
                                  <div className="flex items-center gap-3 text-xs text-default-500">
                                    <span>
                                      <Icon icon="solar:user-linear" className="w-3 h-3 inline mr-1" />
                                      {task.username}
                                    </span>
                                    <span>
                                      <Icon icon="solar:calendar-linear" className="w-3 h-3 inline mr-1" />
                                      {formatTime(task.created_at)}
                                    </span>
                                    <span>
                                      <Icon icon="solar:clock-linear" className="w-3 h-3 inline mr-1" />
                                      {getExecutionTime(task.created_at, task.completed_at)}
                                    </span>
                                  </div>
                                </div>

                                {/* 强制操作按钮 */}
                                <div className="flex gap-2">
                                  <Button
                                    size="sm"
                                    variant="flat"
                                    color="success"
                                    isLoading={operatingTaskId === task.id}
                                    onPress={() => handleForceAction('complete', task.id, task.name)}
                                    startContent={<Icon icon="solar:check-circle-linear" className="w-4 h-4" />}
                                  >
                                    强制完成
                                  </Button>
                                  <Button
                                    size="sm"
                                    variant="flat"
                                    color="danger"
                                    isLoading={operatingTaskId === task.id}
                                    onPress={() => handleForceAction('cancel', task.id, task.name)}
                                    startContent={<Icon icon="solar:close-circle-linear" className="w-4 h-4" />}
                                  >
                                    强制取消
                                  </Button>
                                </div>
                              </div>

                              {/* 进度信息 */}
                              <div className="space-y-2">
                                <div className="flex items-center justify-between text-xs">
                                  <div className="flex items-center gap-2">
                                    <span className="text-default-600">
                                      进度:
                                    </span>
                                    {/* 显示格式：成功数(失败数)/总数 */}
                                    <span className="text-success-600 font-medium">
                                      {task.completed_images}
                                    </span>
                                    {task.failed_images > 0 && (
                                      <>
                                        <span className="text-default-400">(</span>
                                        <span className="text-danger-600 font-medium">
                                          {task.failed_images}
                                        </span>
                                        <span className="text-default-400">)</span>
                                      </>
                                    )}
                                    <span className="text-default-500">
                                      /{task.total_images} 张图片
                                    </span>
                                  </div>
                                  <span className="font-medium text-sm">{task.progress}%</span>
                                </div>
                                <CustomProgress
                                  total={task.total_images}
                                  completed={task.completed_images}
                                  failed={task.failed_images}
                                  size="sm"
                                  className="w-full"
                                />
                              </div>

                              {/* 任务ID - 完整显示并添加复制按钮 */}
                              <div className="mt-2 flex items-center">
                                <span className="text-xs text-default-400 font-mono">
                                  ID: {task.id}
                                </span>
                                <Button
                                  size="sm"
                                  variant="light"
                                  isIconOnly
                                  className="h-5 w-5 min-w-5 ml-2"
                                  onPress={() => {
                                    navigator.clipboard.writeText(task.id);
                                    toast.success("任务ID已复制到剪贴板");
                                  }}
                                  title="复制任务ID"
                                >
                                  <Icon icon="solar:copy-linear" className="w-3 h-3" />
                                </Button>
                              </div>
                            </div>
                          </div>
                        </CardBody>
                      </Card>
                    </div>
                  ))}
                </div>
              </ScrollShadow>
            )}
          </CardBody>
        </Card>
      </div>

      {/* 强制操作确认弹窗 */}
      <Modal isOpen={isOpen} onClose={onClose} size="md">
        <ModalContent>
          <ModalHeader>
            <div className="flex items-center gap-2">
              <Icon
                icon={confirmAction?.type === 'complete' ? "solar:check-circle-linear" : "solar:close-circle-linear"}
                className={`w-5 h-5 ${confirmAction?.type === 'complete' ? 'text-success' : 'text-danger'}`}
              />
              {confirmAction?.type === 'complete' ? '强制完成任务' : '强制取消任务'}
            </div>
          </ModalHeader>
          <ModalBody>
            <div className="space-y-3">
              <p className="text-default-600">
                您确定要{confirmAction?.type === 'complete' ? '强制完成' : '强制取消'}以下任务吗？
              </p>
              <div className="bg-default-100 p-3 rounded-lg">
                <p className="font-medium">{confirmAction?.taskName}</p>
                <p className="text-sm text-default-500 font-mono">ID: {confirmAction?.taskId}</p>
              </div>
              <div className={`p-3 rounded-lg ${confirmAction?.type === 'complete' ? 'bg-warning-50' : 'bg-danger-50'}`}>
                <p className={`text-sm ${confirmAction?.type === 'complete' ? 'text-warning-700' : 'text-danger-700'}`}>
                  {confirmAction?.type === 'complete'
                    ? '⚠️ 此操作将强制完成任务，未完成的子任务将被标记为失败，并清理Redis中的相关队列消息。'
                    : '⚠️ 此操作将强制取消任务，未完成的子任务将被标记为取消，并清理Redis中的相关队列消息。'
                  }
                </p>
              </div>
            </div>
          </ModalBody>
          <ModalFooter>
            <Button variant="light" onPress={onClose}>
              取消
            </Button>
            <Button
              color={confirmAction?.type === 'complete' ? 'warning' : 'danger'}
              onPress={executeForceAction}
              isLoading={operatingTaskId === confirmAction?.taskId}
            >
              确认{confirmAction?.type === 'complete' ? '强制完成' : '强制取消'}
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </div>
  );
}
