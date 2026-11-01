import {
  HOURS_PER_DAY,
  MILLISECONDS_PER_SECOND,
  MINUTES_PER_HOUR,
  RELATIVE_TIME_MAXIMUM_DAYS,
  SECONDS_PER_MINUTE,
} from "../typing/constants/notification.constant";

export const formatRelativeTime = (isoDate: string, now: Date, language: string): string | null => {
  const elapsedMilliseconds = now.getTime() - new Date(isoDate).getTime();
  if (Number.isNaN(elapsedMilliseconds)) {
    return null;
  }

  const formatter = new Intl.RelativeTimeFormat(language, { numeric: "auto" });
  const elapsedSeconds = Math.max(0, Math.floor(elapsedMilliseconds / MILLISECONDS_PER_SECOND));
  if (elapsedSeconds < SECONDS_PER_MINUTE) {
    return formatter.format(0, "second");
  }

  const elapsedMinutes = Math.floor(elapsedSeconds / SECONDS_PER_MINUTE);
  if (elapsedMinutes < MINUTES_PER_HOUR) {
    return formatter.format(-elapsedMinutes, "minute");
  }

  const elapsedHours = Math.floor(elapsedMinutes / MINUTES_PER_HOUR);
  if (elapsedHours < HOURS_PER_DAY) {
    return formatter.format(-elapsedHours, "hour");
  }

  const elapsedDays = Math.floor(elapsedHours / HOURS_PER_DAY);
  if (elapsedDays < RELATIVE_TIME_MAXIMUM_DAYS) {
    return formatter.format(-elapsedDays, "day");
  }

  return null;
};
