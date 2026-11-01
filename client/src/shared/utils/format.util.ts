import type { DurationParts } from "../typing/types/duration.type";

export const splitDuration = (durationInMilliseconds: number): DurationParts => {
  const totalSeconds = Math.round(durationInMilliseconds / 1000);

  return { minutes: Math.floor(totalSeconds / 60), seconds: totalSeconds % 60 };
};
