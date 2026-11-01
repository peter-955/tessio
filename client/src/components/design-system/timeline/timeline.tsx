"use client";

import { Timeline } from "@mantine/core";
import type { FC } from "react";
import { DSIcon } from "../icon/icon";
import { DSText } from "../text/text";
import {
  DS_TIMELINE_BULLET_SIZE,
  DS_TIMELINE_ICON_SIZE,
  DS_TIMELINE_LINE_WIDTH,
} from "./timeline.constant";
import styles from "./timeline.module.scss";
import type { DSTimelineItem } from "./timeline.type";

interface Props {
  items: DSTimelineItem[];
  activeIndex?: number;
}

export const DSTimeline: FC<Props> = ({ items, activeIndex = -1 }) => {
  return (
    <Timeline
      active={activeIndex}
      bulletSize={DS_TIMELINE_BULLET_SIZE}
      lineWidth={DS_TIMELINE_LINE_WIDTH}
      role="list"
      classNames={{ itemTitle: styles.title }}
    >
      {items.map((item) => {
        return (
          <Timeline.Item
            key={item.key}
            role="listitem"
            title={item.title}
            color={item.color}
            bullet={
              item.icon ? <DSIcon name={item.icon} size={DS_TIMELINE_ICON_SIZE} /> : undefined
            }
          >
            {item.description && (
              <DSText size="sm" color="muted" component="div">
                {item.description}
              </DSText>
            )}
            {item.time && (
              <DSText size="xs" color="muted" className={styles.time}>
                {item.time}
              </DSText>
            )}
          </Timeline.Item>
        );
      })}
    </Timeline>
  );
};
