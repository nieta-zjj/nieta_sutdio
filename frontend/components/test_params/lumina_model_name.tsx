"use client";

import React from "react";
import { Input } from "@heroui/react";

import { BaseParamComponent } from "./BaseParam";
import { TextParamProps, ParamValueType } from "./types";

/**
 * Lumina模型名称参数组件
 */
export const LuminaModelNameParam: React.FC<Partial<TextParamProps>> = (props) => {
  const {
    value = "",
    onChange = () => {},
    onVariableChange = () => {},
    isVariable = false,
    placeholder = "输入Lumina模型名称",
    ...rest
  } = props;

  // 渲染输入框
  const renderInput = (
    currentValue: ParamValueType,
    onValueChange: (value: ParamValueType) => void
  ) => {
    return (
      <Input
        className="w-full"
        placeholder={placeholder}
        value={currentValue?.toString() || ""}
        onChange={(e) => onValueChange(e.target.value)}
      />
    );
  };

  return (
    <BaseParamComponent
      defaultValue=""
      isVariable={isVariable}
      label="模型"
      renderInput={renderInput}
      value={value}
      onChange={onChange}
      onVariableChange={onVariableChange}
      {...rest}
    />
  );
};
