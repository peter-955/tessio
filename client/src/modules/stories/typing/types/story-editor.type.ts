import type { components } from "@/lib/api/openapi.type";

export type StoryRequest = components["schemas"]["StoryRequest"];

export interface CriterionDraft {
  id: string;
  text: string;
}

export interface StoryEditorValues {
  title: string;
  description: string;
  criteria: CriterionDraft[];
}
