import { describe, expect, it } from "vitest";
import {
  buildNewManualRunPath,
  buildRecordManualRunPath,
  buildRunDetailPath,
  buildStoryTestCasesPath,
} from "./manual-run-path.util";
import { buildRerunCommand } from "./rerun-command.util";

describe("manual run paths", () => {
  it("builds the new, record, detail and story test-case paths", () => {
    expect(buildNewManualRunPath("SHOP")).toBe("/projects/SHOP/runs/new");
    expect(buildNewManualRunPath("SHOP", "SHOP-1")).toBe("/projects/SHOP/runs/new?story=SHOP-1");
    expect(buildRunDetailPath("SHOP", "run-1")).toBe("/projects/SHOP/runs/run-1");
    expect(buildRecordManualRunPath("SHOP", "run-1")).toBe("/projects/SHOP/runs/run-1/record");
    expect(buildStoryTestCasesPath("SHOP", "SHOP-1")).toBe(
      "/projects/SHOP/stories/SHOP-1?tab=test-cases",
    );
  });

  it("builds the plugin re-run command", () => {
    expect(buildRerunCommand("run-1")).toBe("/tessio:rerun-failed run-1");
  });
});
