"use client";

import { Timeline } from "@mantine/core";
import type { FC } from "react";
import { DSIcon } from "../icon/icon";
import {
  DS_STEP_TIMELINE_BULLET_SIZE,
  DS_STEP_TIMELINE_ICON_SIZE,
  DS_STEP_TIMELINE_LINE_WIDTH,
  DS_STEP_TIMELINE_STATUS_STYLES,
} from "./step-timeline.constant";
import styles from "./step-timeline.module.scss";
import type { DSStepTimelineLabels, DSStepTimelineStep } from "./step-timeline.type";

interface Props {
  steps: DSStepTimelineStep[];
  labels: DSStepTimelineLabels;
  ariaLabel: string;
}

export const DSStepTimeline: FC<Props> = ({ steps, labels, ariaLabel }) => {
  return (
    <Timeline
      active={-1}
      bulletSize={DS_STEP_TIMELINE_BULLET_SIZE}
      lineWidth={DS_STEP_TIMELINE_LINE_WIDTH}
      role="list"
      aria-label={ariaLabel}
      className={styles.timeline}
    >
      {steps.map((step) => {
        const { color, icon } = DS_STEP_TIMELINE_STATUS_STYLES[step.status];

        return (
          <Timeline.Item
            key={step.key}
            role="listitem"
            color={color}
            className={styles.item}
            bullet={<DSIcon name={icon} size={DS_STEP_TIMELINE_ICON_SIZE} />}
            title={
              <span className={styles.title}>
                <span className={styles.order}>{labels.step(step.order)}</span>
                <span className={styles.action}>{step.action}</span>
                <span className={styles.statusLabel}>{step.statusLabel}</span>
              </span>
            }
          >
            <div className={styles.body}>
              {step.expected !== null && (
                <div className={styles.field}>
                  <span className={styles.fieldLabel}>{labels.expected}</span>
                  <p className={`${styles.fieldValue} ${styles.mutedValue}`}>{step.expected}</p>
                </div>
              )}
              {step.actualResult !== null && (
                <div className={styles.field}>
                  <span className={styles.fieldLabel}>{labels.actualResult}</span>
                  <p className={styles.fieldValue}>{step.actualResult}</p>
                </div>
              )}
              {step.error !== null && (
                <div className={`${styles.field} ${styles.error}`}>
                  <span className={styles.fieldLabel}>{labels.error}</span>
                  <p className={styles.fieldValue}>{step.error}</p>
                </div>
              )}
              {step.media !== undefined && <div className={styles.media}>{step.media}</div>}
            </div>
          </Timeline.Item>
        );
      })}
    </Timeline>
  );
};
