"use client";

import React from "react";
import { Switch } from "@heroui/react";

import { BaseParamComponent } from "./BaseParam";
import { BooleanParamProps, ParamValueType } from "./types";

/**
 * 润色参数组件
 */
export const UsePolishParam: React.FC<Partial<BooleanParamProps>> = (props) => {
  const {
    value = false,
    onChange = () => {},
    onVariableChange = () => {},
    isVariable = false,
    ...rest
  } = props;

  // 渲染开关
  const renderInput = (
    currentValue: ParamValueType,
    onValueChange: (value: ParamValueType) => void
  ) => {
    // 确保值是布尔型
    const boolValue = !!currentValue;

    return (
      <Switch
        className="min-h-[40px]"
        isSelected={boolValue}
        onValueChange={(checked) => onValueChange(checked)}
      />
    );
  };

  return (
    <BaseParamComponent
      defaultValue={false}
      isVariable={isVariable}
      label="润色"
      renderInput={renderInput}
      value={value}
      onChange={onChange}
      onVariableChange={onVariableChange}
      {...rest}
    />
  );
};
