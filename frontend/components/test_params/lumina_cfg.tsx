"use client";

import React from "react";
import { Input, Slider } from "@heroui/react";

import { BaseParamComponent } from "./BaseParam";
import { NumberParamProps, ParamValueType } from "./types";

/**
 * Lumina CFG参数组件
 */
export const LuminaCfgParam: React.FC<Partial<NumberParamProps>> = (props) => {
  const {
    value = 5.5,
    onChange = () => {},
    onVariableChange = () => {},
    isVariable = false,
    min = 0,
    max = 10,
    step = 0.1,
    showSlider = true,
    ...rest
  } = props;

  // 渲染输入控件（滑块+数字输入框）
  const renderInput = (
    currentValue: ParamValueType,
    onValueChange: (value: ParamValueType) => void
  ) => {
    // 确保值是数字
    const numValue =
      typeof currentValue === "number" ? currentValue : parseFloat(String(currentValue || "5.5"));

    return (
      <div className="flex items-center gap-2 w-full">
        {showSlider && (
          <div className="flex-grow">
            <Slider
              maxValue={max}
              minValue={min}
              size="sm"
              step={step}
              value={numValue}
              onChange={(value: number | number[]) => {
                // Slider可能返回单个值或数组，确保我们获取到单个值
                const newValue = Array.isArray(value) ? value[0] : value;

                onValueChange(newValue);
              }}
            />
          </div>
        )}
        <div className="w-16">
          <Input
            className="w-full"
            max={max}
            min={min}
            size="sm"
            step={step}
            type="number"
            value={numValue.toString()}
            onChange={(e) => {
              const value = parseFloat(e.target.value);

              if (!isNaN(value) && value >= min && value <= max) {
                onValueChange(value);
              }
            }}
          />
        </div>
      </div>
    );
  };

  return (
    <BaseParamComponent
      defaultValue={5.5}
      isVariable={isVariable}
      label="cfg"
      renderInput={renderInput}
      value={value}
      onChange={onChange}
      onVariableChange={onVariableChange}
      {...rest}
    />
  );
};
