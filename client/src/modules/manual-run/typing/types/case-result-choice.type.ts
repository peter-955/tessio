import type { USE_SUGGESTED_CHOICE } from "../constants/result-status.constant";
import type { ResultStatus } from "./manual-run.type";

export type CaseResultChoice = ResultStatus | typeof USE_SUGGESTED_CHOICE;
