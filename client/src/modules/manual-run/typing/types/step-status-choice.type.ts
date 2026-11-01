import type { NOT_REPORTED_CHOICE } from "../constants/result-status.constant";
import type { ResultStatus } from "./manual-run.type";

export type StepStatusChoice = ResultStatus | typeof NOT_REPORTED_CHOICE;
