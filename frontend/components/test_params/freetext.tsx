"use client";

import React from "react";
import { Input } from "@heroui/react";

import { BaseParamComponent } from "./BaseParam";
import { TextParamProps } from "./types";

/**
 * 自由文本参数组件
 */
export const FreetextParam: React.FC<TextParamProps> = (props) => {
  const { value = "", onChange, placeholder = "输入提示词内容", ...rest } = props;

  // 渲染输入框
  const renderInput = (currentValue: any, onValueChange: (value: any) => void) => {
    return (
      <Input
        className="w-full"
        placeholder={placeholder}
        size="sm"
        value={currentValue?.toString() || ""}
        onChange={(e) => onValueChange(e.target.value)}
      />
    );
  };

  return (
    <BaseParamComponent
      defaultValue=""
      label="文本"
      renderInput={renderInput}
      value={value}
      onChange={onChange}
      {...rest}
    />
  );
};
