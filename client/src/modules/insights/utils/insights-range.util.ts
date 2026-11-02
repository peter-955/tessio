import {
  DEFAULT_RANGE_DAYS,
  ISO_DAY_LENGTH,
  MAX_RANGE_DAYS,
  MILLISECONDS_PER_DAY,
} from "../typing/constants/insights.constant";
import { RangeProblem } from "../typing/enums/range-problem.enum";
import type { InsightsRange } from "../typing/types/insights-range.type";

interface SprintDates {
  startAt: string | null;
  endAt: string | null;
}

const parseIsoDay = (day: string): number => {
  return Date.parse(`${day}T00:00:00Z`);
};

export const formatIsoDay = (date: Date): string => {
  return date.toISOString().slice(0, ISO_DAY_LENGTH);
};

export const shiftIsoDay = (day: string, dayCount: number): string => {
  return formatIsoDay(new Date(parseIsoDay(day) + dayCount * MILLISECONDS_PER_DAY));
};

export const buildDefaultRange = (today: Date): InsightsRange => {
  const to = formatIsoDay(today);

  return { from: shiftIsoDay(to, 1 - DEFAULT_RANGE_DAYS), to };
};

export const countRangeDays = (range: InsightsRange): number => {
  return Math.round((parseIsoDay(range.to) - parseIsoDay(range.from)) / MILLISECONDS_PER_DAY) + 1;
};

export const findRangeProblem = (range: InsightsRange): RangeProblem | null => {
  if (range.from > range.to) {
    return RangeProblem.ORDER;
  }
  if (countRangeDays(range) > MAX_RANGE_DAYS) {
    return RangeProblem.TOO_LONG;
  }

  return null;
};

export const buildSprintRange = (sprint: SprintDates, today: Date): InsightsRange | null => {
  if (sprint.startAt === null) {
    return null;
  }

  const from = formatIsoDay(new Date(sprint.startAt));
  const end = sprint.endAt === null ? formatIsoDay(today) : formatIsoDay(new Date(sprint.endAt));
  const to = end < from ? from : end;
  const latestTo = shiftIsoDay(from, MAX_RANGE_DAYS - 1);

  return { from, to: to > latestTo ? latestTo : to };
};
