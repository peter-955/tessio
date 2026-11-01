import { existsSync, readFileSync, writeFileSync } from "node:fs";
import { E2E_PATHS } from "../constants/e2e-environment.constant.ts";
import type { RunState } from "../types/run-state.type.ts";

export const readRunState = (): Partial<RunState> => {
  if (!existsSync(E2E_PATHS.runState)) {
    return {};
  }
  const runState: Partial<RunState> = JSON.parse(readFileSync(E2E_PATHS.runState, "utf8"));
  return runState;
};

export const mergeRunState = (update: Partial<RunState>): void => {
  writeFileSync(E2E_PATHS.runState, JSON.stringify({ ...readRunState(), ...update }, null, 2));
};

export const requireRunValue = <Key extends keyof RunState>(key: Key): RunState[Key] => {
  const value = readRunState()[key];
  if (value === undefined) {
    throw new Error(`The run state has no ${key}; run the earlier specs first`);
  }
  return value;
};
