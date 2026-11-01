import type { AxeResults } from "axe-core";
import "vitest";

declare module "vitest" {
  interface Matchers<R extends void | Promise<void> = void | Promise<void>, T = unknown> {
    toHaveNoViolations: T extends AxeResults ? () => R : never;
  }
}
