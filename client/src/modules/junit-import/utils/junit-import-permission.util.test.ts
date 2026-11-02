import {
  VIEWER_CAPABILITIES,
  buildProject,
} from "@/components/project-context/test/utils/project-fixture.util";
import { describe, expect, it } from "vitest";
import { checkCanImportJunit } from "./junit-import-permission.util";

describe("checkCanImportJunit", () => {
  it("needs run.start on an active project", () => {
    const capabilities = [...VIEWER_CAPABILITIES, "run.start" as const];

    expect(checkCanImportJunit(buildProject({ capabilities }))).toBe(true);
    expect(checkCanImportJunit(buildProject())).toBe(false);
    expect(checkCanImportJunit(buildProject({ capabilities, isArchived: true }))).toBe(false);
  });
});
