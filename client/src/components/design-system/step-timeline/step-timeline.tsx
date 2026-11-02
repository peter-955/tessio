"use client";

import { Timeline } from "@mantine/core";
import type { FC, ReactNode } from "react";
import { DSIcon } from "../icon/icon";
import {
  DS_STEP_TIMELINE_BULLET_SIZE,
  DS_STEP_TIMELINE_EXPECTED_ICON,
  DS_STEP_TIMELINE_ICON_SIZE,
  DS_STEP_TIMELINE_LINE_WIDTH,
  DS_STEP_TIMELINE_NUMBER_COLOR,
  DS_STEP_TIMELINE_STATUS_STYLES,
} from "./step-timeline.constant";
import styles from "./step-timeline.module.scss";
import type { DSStepTimelineLabels, DSStepTimelineStep } from "./step-timeline.type";

interface Props {
  steps: DSStepTimelineStep[];
  labels: DSStepTimelineLabels;
  ariaLabel?: string;
}

const checkHasContent = (value: ReactNode): boolean => {
  return value !== null && value !== undefined && value !== "";
};

const renderBullet = (step: DSStepTimelineStep): ReactNode => {
  if (step.status === undefined) {
    return (
      <span className={styles.number} aria-hidden="true">
        {step.order}
      </span>
    );
  }

  return (
    <DSIcon
      name={DS_STEP_TIMELINE_STATUS_STYLES[step.status].icon}
      size={DS_STEP_TIMELINE_ICON_SIZE}
    />
  );
};

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
        const isNumbered = step.status === undefined;
        const hasAction = checkHasContent(step.action);
        const hasExpected = checkHasContent(step.expected);
        const hasActualResult =
          checkHasContent(step.actualResult) && labels.actualResult !== undefined;
        const hasError = checkHasContent(step.error) && labels.error !== undefined;
        const hasBody =
          hasExpected ||
          hasActualResult ||
          hasError ||
          step.details !== undefined ||
          step.media !== undefined;
        const color = isNumbered
          ? DS_STEP_TIMELINE_NUMBER_COLOR
          : DS_STEP_TIMELINE_STATUS_STYLES[step.status ?? "pending"].color;
        const orderClassName =
          isNumbered && hasAction ? `${styles.order} ${styles.hiddenLabel}` : styles.order;

        return (
          <Timeline.Item
            key={step.key}
            role="listitem"
            color={color}
            className={styles.item}
            bullet={renderBullet(step)}
            title={
              <span className={styles.title}>
                <span className={styles.heading}>
                  <span id={step.titleId} className={orderClassName}>
                    {labels.step(step.order)}
                  </span>
                  {hasAction && <span className={styles.action}>{step.action}</span>}
                  {step.statusLabel !== undefined && (
                    <span className={styles.statusLabel}>{step.statusLabel}</span>
                  )}
                </span>
                {step.headerAction !== undefined && (
                  <span className={styles.headerAction}>{step.headerAction}</span>
                )}
              </span>
            }
          >
            {hasBody && (
              <div className={styles.body}>
                {hasExpected && (
                  <div className={`${styles.field} ${styles.expected}`}>
                    <span className={styles.fieldLabel}>
                      <DSIcon
                        name={DS_STEP_TIMELINE_EXPECTED_ICON}
                        size={DS_STEP_TIMELINE_ICON_SIZE}
                      />
                      {labels.expected}
                    </span>
                    <div className={styles.fieldValue}>{step.expected}</div>
                  </div>
                )}
                {hasActualResult && (
                  <div className={styles.field}>
                    <span className={styles.fieldLabel}>{labels.actualResult}</span>
                    <p className={styles.fieldValue}>{step.actualResult}</p>
                  </div>
                )}
                {hasError && (
                  <div className={`${styles.field} ${styles.error}`}>
                    <span className={styles.fieldLabel}>{labels.error}</span>
                    <p className={styles.fieldValue}>{step.error}</p>
                  </div>
                )}
                {step.details !== undefined && <div className={styles.media}>{step.details}</div>}
                {step.media !== undefined && <div className={styles.media}>{step.media}</div>}
              </div>
            )}
          </Timeline.Item>
        );
      })}
    </Timeline>
  );
};
