import type { ReactNode } from "react";

export interface DSSortableListItem {
  key: string;
  content: ReactNode;
}

export interface DSSortableListLabels {
  list: string;
  handle: (index: number) => string;
  instructions: string;
  moved: (index: number, total: number) => string;
}
