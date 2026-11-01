import type { ReassignGapBody } from "./gap.type";

export interface GapReference {
  projectKey: string;
  gapId: string;
}

export interface AnswerGapVariables extends GapReference {
  answer: string;
}

export interface ReassignGapVariables extends GapReference {
  body: ReassignGapBody;
}
