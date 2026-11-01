import type { DSButton } from "@/components/design-system";
import type { ComponentProps } from "react";
import type { TestStatus } from "./story.type";

export type ActionableTestStatus = Exclude<TestStatus, "in_test">;

export type SignOffTestStatus = Extract<TestStatus, "passed" | "failed">;

export type TestStatusActionLabel =
  "markReadyForTest" | "markNotStarted" | "markPassed" | "markFailed";

export interface TestStatusAction {
  label: TestStatusActionLabel;
  buttonType: NonNullable<ComponentProps<typeof DSButton>["type"]>;
}
