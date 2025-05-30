"use client";

import React, { ReactNode } from "react";
import { Button } from "@heroui/react";
import { Icon } from "@iconify/react";

import { ParamValueType } from "./types";

interface VariableValuesListProps {
  values: ParamValueType[];
  onChange: (values: ParamValueType[]) => void;
  renderInput: (
    value: ParamValueType,
    index: number,
    onChange: (value: ParamValueType) => void
  ) => ReactNode;
  defaultValue?: ParamValueType;
}

/**
 * 变量值列表组件
 * 用于显示和管理参数的多个变量值
 */
export const VariableValuesList: React.FC<VariableValuesListProps> = ({
  values,
  onChange,
  renderInput,
  defaultValue = "",
}) => {
  // 添加新值
  const addValue = () => {
    const newValues = [...values, defaultValue];

    onChange(newValues);
  };

  // 更新值
  const updateValue = (index: number, newValue: ParamValueType) => {
    // 验证索引的有效性
    if (!Number.isInteger(index) || index < 0 || index >= values.length) {
      return;
    }

    const newValues = values.map((value, i) => (i === index ? newValue : value));

    onChange(newValues);
  };

  // 删除值
  const removeValue = (index: number) => {
    if (values.length <= 1) return; // 至少保留一个值

    // 验证索引的有效性
    if (!Number.isInteger(index) || index < 0 || index >= values.length) {
      return;
    }

    const newValues = values.filter((_, i) => i !== index);

    onChange(newValues);
  };

  // 移动值的位置
  const moveValue = (index: number, direction: "up" | "down") => {
    // 验证索引的有效性
    if (!Number.isInteger(index) || index < 0 || index >= values.length) {
      return;
    }

    if (
      (direction === "up" && index === 0) ||
      (direction === "down" && index === values.length - 1)
    ) {
      return;
    }

    const targetIndex = direction === "up" ? index - 1 : index + 1;

    // 验证目标索引的有效性
    if (targetIndex < 0 || targetIndex >= values.length) {
      return;
    }

    // 安全地获取值
    const currentValue = values.at(index);
    const targetValue = values.at(targetIndex);

    if (currentValue === undefined || targetValue === undefined) {
      return;
    }

    const newValues = values.map((value, i) => {
      if (i === index) return targetValue;
      if (i === targetIndex) return currentValue;

      return value;
    });

    onChange(newValues);
  };

  // 复制值
  const duplicateValue = (index: number) => {
    // 验证索引的有效性
    if (!Number.isInteger(index) || index < 0 || index >= values.length) {
      return;
    }

    const valueAtIndex = values.at(index);

    if (valueAtIndex === undefined) {
      return;
    }

    const newValues = [...values.slice(0, index + 1), valueAtIndex, ...values.slice(index + 1)];

    onChange(newValues);
  };

  return (
    <div className="mt-2 mb-1 space-y-1">
      <div className="flex justify-between items-center">
        <span className="text-xs text-default-500">变量值列表</span>
        <Button
          color="primary"
          size="sm"
          startContent={<Icon icon="solar:add-circle-linear" width={14} />}
          variant="flat"
          onPress={addValue}
        >
          添加值
        </Button>
      </div>

      {values.map((value, index) => (
        <div key={index} className="flex items-center gap-2 p-1 border rounded-md">
          <div className="flex-grow">
            {renderInput(value, index, (newValue) => updateValue(index, newValue))}
          </div>

          <div className="flex gap-1">
            <Button
              isIconOnly
              isDisabled={index === 0}
              size="sm"
              variant="light"
              onPress={() => moveValue(index, "up")}
            >
              <Icon icon="solar:alt-arrow-up-linear" width={16} />
            </Button>
            <Button
              isIconOnly
              isDisabled={index === values.length - 1}
              size="sm"
              variant="light"
              onPress={() => moveValue(index, "down")}
            >
              <Icon icon="solar:alt-arrow-down-linear" width={16} />
            </Button>
            <Button isIconOnly size="sm" variant="light" onPress={() => duplicateValue(index)}>
              <Icon icon="solar:copy-linear" width={16} />
            </Button>
            <Button
              isIconOnly
              color="danger"
              isDisabled={values.length <= 1}
              size="sm"
              variant="light"
              onPress={() => removeValue(index)}
            >
              <Icon icon="solar:trash-bin-trash-linear" width={16} />
            </Button>
          </div>
        </div>
      ))}
    </div>
  );
};
