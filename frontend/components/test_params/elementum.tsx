"use client";

import React from "react";

import { BaseParamComponent } from "./BaseParam";
import { VTokenParamProps, ParamValueType } from "./types";

import { VTokenSelector } from "@/components/vtoken";
import { SearchSelectItem } from "@/types/search";

// 元素完整信息接口
interface ElementInfo {
  name: string;
  uuid: string;
  header_img?: string;
}

/**
 * 元素参数组件
 */
export const ElementumParam: React.FC<
  Partial<VTokenParamProps> & {
    onSelectElement?: (info: ElementInfo) => void;
  }
> = (props) => {
  const {
    value = "",
    onChange = () => {},
    onVariableChange = () => {},
    isVariable = false,
    name = "",
    uuid = "", // eslint-disable-line @typescript-eslint/no-unused-vars -- 需要的 props 接口的一部分
    header_img = "",
    onSelectElement,
    ...rest
  } = props;

  // 渲染选择器
  const renderInput = (
    currentValue: ParamValueType,
    onValueChange: (value: ParamValueType) => void
  ) => {
    return (
      <VTokenSelector
        header_img={header_img}
        name={name}
        type="element"
        onChange={(value) => {
          // 如果用户清除了选择，则清除所有相关字段
          if (!value) {
            onValueChange("");
            // 通知父组件清除元素相关信息
            onSelectElement?.({ name: "", uuid: "", header_img: "" });
          }
        }}
        onSelectItem={(item: SearchSelectItem) => {
          // 设置uuid作为值
          onValueChange(item.uuid);

          // 通知父组件更新元素完整信息
          const info = {
            name: item.name,
            uuid: item.uuid,
            header_img: item.header_img,
          };

          onSelectElement?.(info);
        }}
      />
    );
  };

  return (
    <BaseParamComponent
      defaultValue=""
      isVariable={isVariable}
      label="元素"
      renderInput={renderInput}
      value={value}
      onChange={onChange}
      onVariableChange={onVariableChange}
      {...rest}
    />
  );
};
