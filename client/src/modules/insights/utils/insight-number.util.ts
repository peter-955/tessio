import {
  CHART_DECIMALS,
  PERCENT_SCALE,
  SECONDS_PER_DAY,
  SECONDS_PER_HOUR,
  SECONDS_PER_MINUTE,
} from "../typing/constants/insights.constant";
import { DurationUnit } from "../typing/enums/duration-unit.enum";

const DECIMAL_BASE = 10;

interface Duration {
  unit: DurationUnit;
  value: number;
}

export const roundTo = (value: number, decimals: number = CHART_DECIMALS): number => {
  const factor = DECIMAL_BASE ** decimals;

  return Math.round(value * factor) / factor;
};

export const toPercent = (share: number | null): number | null => {
  return share === null ? null : roundTo(share * PERCENT_SCALE);
};

export const toDays = (seconds: number | null): number | null => {
  return seconds === null ? null : roundTo(seconds / SECONDS_PER_DAY);
};

export const pickDuration = (seconds: number): Duration => {
  if (seconds >= SECONDS_PER_DAY) {
    return { unit: DurationUnit.DAY, value: roundTo(seconds / SECONDS_PER_DAY) };
  }
  if (seconds >= SECONDS_PER_HOUR) {
    return { unit: DurationUnit.HOUR, value: roundTo(seconds / SECONDS_PER_HOUR) };
  }

  return {
    unit: DurationUnit.MINUTE,
    value: Math.max(0, Math.round(seconds / SECONDS_PER_MINUTE)),
  };
};
