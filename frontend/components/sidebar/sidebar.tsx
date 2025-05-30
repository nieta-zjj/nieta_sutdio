"use client";

import {
  Accordion,
  AccordionItem,
  type ListboxProps,
  type ListboxSectionProps,
  type Selection,
} from "@heroui/react";
import React from "react";
import { Listbox, Tooltip, ListboxItem } from "@heroui/react";
import { Icon } from "@iconify/react";
import { cn } from "@heroui/react";

import { SidebarItemType } from "./types";

export type SidebarItem = {
  key: string;
  title: string;
  icon?: string;
  href?: string;
  type?: SidebarItemType.Nest;
  startContent?: React.ReactNode;
  endContent?: React.ReactNode;
  items?: SidebarItem[];
  className?: string;
};

export type SidebarProps = Omit<ListboxProps<SidebarItem>, "children"> & {
  items: SidebarItem[];
  isCompact?: boolean;
  hideEndContent?: boolean;
  iconClassName?: string;
  sectionClasses?: ListboxSectionProps["classNames"];
  classNames?: ListboxProps["classNames"];
  defaultSelectedKey: string;
  onSelect?: (key: string) => void;
};

const Sidebar = React.forwardRef<HTMLElement, SidebarProps>(
  (
    {
      items,
      isCompact,
      defaultSelectedKey,
      onSelect,
      hideEndContent,
      sectionClasses: _sectionClassesProp = {},
      itemClasses: itemClassesProp = {},
      iconClassName,
      classNames,
      className,
      onSelectionChange: _onSelectionChange,
      ...props
    },
    ref
  ) => {
    // 常量定义
    const ICON_BASE_CLASSES = "text-default-500 group-data-[selected=true]:text-foreground";
    const TEXT_BASE_CLASSES =
      "text-small font-medium text-default-500 group-data-[selected=true]:text-foreground";

    const [selectedKeys, setSelectedKeys] = React.useState<Selection>(
      new Set([defaultSelectedKey])
    );

    const itemClasses = {
      ...itemClassesProp,
      base: cn(itemClassesProp?.base, {
        "w-11 h-11 gap-0 p-0": isCompact,
      }),
    };

    const renderNestItem = React.useCallback(
      (item: SidebarItem) => {
        const isNestType =
          item.items && item.items?.length > 0 && item?.type === SidebarItemType.Nest;

        if (isNestType) {
          // Is a nest type item , so we need to remove the href
          delete item.href;
        }

        return (
          <ListboxItem
            {...item}
            key={item.key}
            classNames={{
              base: cn(
                {
                  "h-auto p-0": !isCompact && isNestType,
                },
                {
                  "inline-block w-11": isCompact && isNestType,
                }
              ),
            }}
            endContent={
              isCompact || isNestType || hideEndContent ? null : (item.endContent ?? null)
            }
            startContent={
              isCompact || isNestType ? null : item.icon ? (
                <Icon
                  className={cn(ICON_BASE_CLASSES, iconClassName)}
                  icon={item.icon}
                  width={24}
                />
              ) : (
                (item.startContent ?? null)
              )
            }
            title={isCompact || isNestType ? null : item.title}
          >
            {!isCompact && isNestType ? (
              <Accordion className="px-0" itemClasses={{ base: "px-0" }}>
                <AccordionItem
                  key={item.key}
                  classNames={{
                    base: "px-0",
                    title: "px-0 py-0",
                    trigger: "px-0 py-0",
                    content: "py-0 px-0",
                  }}
                  title={
                    item.icon ? (
                      <div className="flex items-center gap-2">
                        <Icon
                          className={cn(ICON_BASE_CLASSES, iconClassName)}
                          icon={item.icon}
                          width={24}
                        />
                        <span className={TEXT_BASE_CLASSES}>{item.title}</span>
                      </div>
                    ) : (
                      (item.startContent ?? null)
                    )
                  }
                >
                  <Listbox
                    className="mt-0.5"
                    classNames={{
                      list: "border-l border-default-200 ml-3 pl-3",
                    }}
                    items={item.items || []}
                    variant="flat"
                  >
                    {(item.items || []).map((nestedItem) => (
                      <ListboxItem
                        {...nestedItem}
                        key={nestedItem.key}
                        endContent={hideEndContent ? null : (nestedItem.endContent ?? null)}
                        startContent={
                          nestedItem.icon ? (
                            <Icon
                              className={cn(ICON_BASE_CLASSES, iconClassName)}
                              icon={nestedItem.icon}
                              width={24}
                            />
                          ) : (
                            (nestedItem.startContent ?? null)
                          )
                        }
                        textValue={nestedItem.title}
                        title={<span className={TEXT_BASE_CLASSES}>{nestedItem.title}</span>}
                      />
                    ))}
                  </Listbox>
                </AccordionItem>
              </Accordion>
            ) : null}
          </ListboxItem>
        );
      },
      [isCompact, hideEndContent, iconClassName]
    );

    const renderItem = React.useCallback(
      (item: SidebarItem) => {
        const isNestType =
          item.items && item.items?.length > 0 && item?.type === SidebarItemType.Nest;

        if (isNestType) {
          return renderNestItem(item);
        }

        return (
          <ListboxItem
            {...item}
            key={item.key}
            classNames={{
              base: cn(itemClasses?.base, {
                "h-11 gap-0 p-0": isCompact,
              }),
            }}
            endContent={isCompact || hideEndContent ? null : (item.endContent ?? null)}
            startContent={
              isCompact ? (
                <Tooltip content={item.title} placement="right">
                  <div className="flex h-full w-full items-center justify-center rounded-small">
                    {item.icon ? (
                      <Icon
                        className={cn(ICON_BASE_CLASSES, iconClassName)}
                        icon={item.icon}
                        width={24}
                      />
                    ) : (
                      (item.startContent ?? null)
                    )}
                  </div>
                </Tooltip>
              ) : item.icon ? (
                <Icon
                  className={cn(ICON_BASE_CLASSES, iconClassName)}
                  icon={item.icon}
                  width={24}
                />
              ) : (
                (item.startContent ?? null)
              )
            }
            textValue={item.title}
            title={isCompact ? null : <span className={TEXT_BASE_CLASSES}>{item.title}</span>}
          >
            {isCompact ? (
              <Tooltip content={item.title} placement="right">
                <div className="flex h-full w-full items-center justify-center rounded-small">
                  {item.icon ? (
                    <Icon
                      className={cn(ICON_BASE_CLASSES, iconClassName)}
                      icon={item.icon}
                      width={24}
                    />
                  ) : (
                    (item.startContent ?? null)
                  )}
                </div>
              </Tooltip>
            ) : null}
          </ListboxItem>
        );
      },
      [isCompact, hideEndContent, iconClassName, itemClasses?.base, renderNestItem]
    );

    return (
      <Listbox
        ref={ref}
        className={cn("w-full", className)}
        classNames={{
          ...classNames,
          list: cn("items-center", classNames?.list),
        }}
        items={items}
        selectedKeys={selectedKeys}
        selectionMode="single"
        variant="flat"
        onSelectionChange={(keys) => {
          const key = Array.from(keys)[0];

          setSelectedKeys(new Set([key as string]));
          onSelect?.(key as string);
        }}
        {...props}
      >
        {renderItem}
      </Listbox>
    );
  }
);

Sidebar.displayName = "Sidebar";

export default Sidebar;
