import type { ReactNode } from "react";
import type { StoryDetailTab } from "../enums/story-detail-tab.enum";

export type StorySlotTab = Exclude<StoryDetailTab, StoryDetailTab.OVERVIEW>;

export type StoryDetailSlots = Partial<Record<StorySlotTab, ReactNode>>;
