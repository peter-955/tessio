import type { DSChartDatum, DSChartSeries } from "@/components/design-system";
import {
  CATEGORY_KEY,
  EXECUTOR_COLORS,
  OTHER_EXECUTOR_COLOR,
} from "../typing/constants/insights.constant";
import type { InsightTrends, TrendPoint } from "../typing/types/insights.type";
import { toDays, toPercent } from "./insight-number.util";

type LabelPoint = (point: TrendPoint) => string;

export const labelTrendPoint = (point: TrendPoint, formatDay: (day: string) => string): string => {
  if (point.sprint !== null) {
    return point.sprint.name;
  }

  return formatDay(point.day ?? point.firstDay);
};

export const buildPassRateData = (points: TrendPoint[], labelPoint: LabelPoint): DSChartDatum[] => {
  return points.map((point) => {
    return { [CATEGORY_KEY]: labelPoint(point), passRate: toPercent(point.passRate) };
  });
};

export const buildExecutorData = (
  points: TrendPoint[],
  executors: string[],
  labelPoint: LabelPoint,
): DSChartDatum[] => {
  return points.map((point) => {
    const datum: DSChartDatum = { [CATEGORY_KEY]: labelPoint(point) };
    executors.forEach((executor) => {
      datum[executor] = 0;
    });
    point.runsByExecutor.forEach((entry) => {
      datum[entry.executor] = entry.count;
    });

    return datum;
  });
};

export const buildExecutorSeries = (
  executors: string[],
  labelExecutor: (executor: string) => string,
): DSChartSeries[] => {
  return executors.map((executor) => {
    return {
      key: executor,
      label: labelExecutor(executor),
      color: EXECUTOR_COLORS[executor] ?? OTHER_EXECUTOR_COLOR,
    };
  });
};

export const buildFailureData = (points: TrendPoint[], labelPoint: LabelPoint): DSChartDatum[] => {
  return points.map((point) => {
    return {
      [CATEGORY_KEY]: labelPoint(point),
      opened: point.failuresOpened,
      fixed: point.failuresFixed,
    };
  });
};

export const buildGapAgeData = (points: TrendPoint[], labelPoint: LabelPoint): DSChartDatum[] => {
  return points.map((point) => {
    return {
      [CATEGORY_KEY]: labelPoint(point),
      medianOpenAge: toDays(point.medianOpenGapAgeSeconds),
      meanAnswer: toDays(point.meanGapAnswerSeconds),
    };
  });
};

export const checkTrendsHaveData = (trends: InsightTrends): boolean => {
  return trends.points.some((point) => {
    return (
      point.runCount > 0 ||
      point.passedCount + point.failedCount + point.blockedCount + point.skippedCount > 0 ||
      point.failuresOpened > 0 ||
      point.failuresFixed > 0 ||
      point.gapsOpened > 0 ||
      point.gapsAnswered > 0 ||
      point.openGapCount > 0
    );
  });
};
