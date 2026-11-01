import type { ReactNode } from "react";
import type { DSIconName } from "../typing/types/icon.type";

export type DSTimelineColor = "gray" | "tessio" | "green" | "red" | "yellow";

export interface DSTimelineItem {
  key: string;
  title: ReactNode;
  description?: ReactNode;
  time?: string;
  icon?: DSIconName;
  color?: DSTimelineColor;
}
