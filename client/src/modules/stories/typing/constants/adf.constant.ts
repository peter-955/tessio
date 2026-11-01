import type { DSBadgeColor } from "@/components/design-system";
import type { AdfHeadingElement } from "../types/adf.type";

export const ADF_MAX_DEPTH = 40;

export const ADF_SAFE_PROTOCOLS: readonly string[] = ["http:", "https:", "mailto:"];

export const ADF_HEADING_ELEMENTS: Readonly<Record<number, AdfHeadingElement>> = {
  1: "h3",
  2: "h4",
  3: "h5",
  4: "h6",
  5: "h6",
  6: "h6",
};

export const ADF_DEFAULT_HEADING_ELEMENT: AdfHeadingElement = "h6";

export const ADF_LIST_ITEM_TYPES: readonly string[] = ["listItem", "taskItem"];

export const ADF_PANEL_TYPES: readonly string[] = ["info", "note", "success", "warning", "error"];

export const ADF_DEFAULT_PANEL_TYPE = "info";

export const ADF_TASK_DONE_STATE = "DONE";

export const ADF_STATUS_COLORS: Readonly<Record<string, DSBadgeColor>> = {
  neutral: "gray",
  purple: "tessio",
  blue: "tessio",
  red: "red",
  yellow: "yellow",
  green: "green",
};

export const ADF_MEDIA_TYPES: readonly string[] = [
  "mediaSingle",
  "mediaGroup",
  "media",
  "mediaInline",
];

export const ADF_CARD_TYPES: readonly string[] = ["inlineCard", "blockCard", "embedCard"];
