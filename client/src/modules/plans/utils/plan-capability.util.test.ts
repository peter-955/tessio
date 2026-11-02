import { describe, expect, it } from "vitest";
import {
  PM_CAPABILITIES,
  QC_CAPABILITIES,
  VIEWER_CAPABILITIES,
  buildProject,
} from "../test/utils/project-fixture.util";
import {
  checkCanClosePlan,
  checkCanCreatePlan,
  checkCanEditPlan,
  checkCanSignOffPlan,
} from "./plan-capability.util";

const OPEN = { status: "open" } as const;
const SIGNED_OFF = { status: "signed_off" } as const;
const CLOSED = { status: "closed" } as const;

describe("plan capability utils", () => {
  it("lets a QC create, edit, sign off and close an open plan", () => {
    const project = buildProject({ capabilities: QC_CAPABILITIES });

    expect(checkCanCreatePlan(project)).toBe(true);
    expect(checkCanEditPlan(project, OPEN)).toBe(true);
    expect(checkCanSignOffPlan(project, OPEN)).toBe(true);
    expect(checkCanClosePlan(project, OPEN)).toBe(true);
  });

  it("lets a PM edit and close but not sign off", () => {
    const project = buildProject({ capabilities: PM_CAPABILITIES });

    expect(checkCanEditPlan(project, OPEN)).toBe(true);
    expect(checkCanClosePlan(project, OPEN)).toBe(true);
    expect(checkCanSignOffPlan(project, OPEN)).toBe(false);
  });

  it("gives a viewer no write action", () => {
    const project = buildProject({ capabilities: VIEWER_CAPABILITIES });

    expect(checkCanCreatePlan(project)).toBe(false);
    expect(checkCanEditPlan(project, OPEN)).toBe(false);
    expect(checkCanSignOffPlan(project, OPEN)).toBe(false);
    expect(checkCanClosePlan(project, OPEN)).toBe(false);
  });

  it("allows only closing a signed-off plan, and nothing on a closed one", () => {
    const project = buildProject({ capabilities: QC_CAPABILITIES });

    expect(checkCanEditPlan(project, SIGNED_OFF)).toBe(false);
    expect(checkCanSignOffPlan(project, SIGNED_OFF)).toBe(false);
    expect(checkCanClosePlan(project, SIGNED_OFF)).toBe(true);
    expect(checkCanClosePlan(project, CLOSED)).toBe(false);
  });

  it("makes plans read-only in an archived project", () => {
    const project = buildProject({ capabilities: QC_CAPABILITIES, isArchived: true });

    expect(checkCanCreatePlan(project)).toBe(false);
    expect(checkCanSignOffPlan(project, OPEN)).toBe(false);
    expect(checkCanClosePlan(project, OPEN)).toBe(false);
  });
});
