"use client";

import type { FC } from "react";
import { useFormatDay } from "../../../hooks/use-format-day";

interface Props {
  timestamp: string | null;
}

export const AdfDate: FC<Props> = ({ timestamp }) => {
  const formatDay = useFormatDay();
  const milliseconds = Number(timestamp);

  if (timestamp === null || !Number.isFinite(milliseconds)) {
    return null;
  }

  return <time dateTime={new Date(milliseconds).toISOString()}>{formatDay(milliseconds)}</time>;
};
