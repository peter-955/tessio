import { describe, expect, it } from "vitest";
import {
  ADMIN_ID,
  createWorkspaceUser,
  MEMBER_ID,
  OWNER_ID,
} from "../test/utils/workspace-user.fixture";
import type { UserActor, WorkspaceRole } from "../typing/types/workspace-user.type";
import {
  checkCanChangeRole,
  checkCanManageUser,
  checkIsWorkspaceAdmin,
} from "./user-permission.util";

type TargetKind = "self" | "owner" | "admin" | "member";

const ACTOR_IDS: Record<WorkspaceRole, string> = {
  owner: OWNER_ID,
  admin: ADMIN_ID,
  member: MEMBER_ID,
};

const OTHER_ADMIN_ID = "5d4a1e96-4f7c-4b0e-9d5c-0a6f2b8c4e05";

const OTHER_MEMBER_ID = "6e5b2fa7-5a8d-4c1f-8e6d-1b7a3c9d5f06";

const buildActor = (role: WorkspaceRole): UserActor => {
  return { id: ACTOR_IDS[role], workspaceRole: role };
};

const buildTarget = (
  actor: UserActor,
  kind: TargetKind,
): ReturnType<typeof createWorkspaceUser> => {
  if (kind === "self") {
    return createWorkspaceUser({ id: actor.id, workspaceRole: actor.workspaceRole });
  }
  if (kind === "owner") {
    return createWorkspaceUser({ id: OWNER_ID, workspaceRole: "owner" });
  }
  if (kind === "admin") {
    return createWorkspaceUser({ id: OTHER_ADMIN_ID, workspaceRole: "admin" });
  }

  return createWorkspaceUser({ id: OTHER_MEMBER_ID, workspaceRole: "member" });
};

describe("checkIsWorkspaceAdmin", () => {
  it.each([
    ["owner", true],
    ["admin", true],
    ["member", false],
  ] as const)("returns %s → %s", (role, expected) => {
    expect(checkIsWorkspaceAdmin(role)).toBe(expected);
  });
});

describe("checkCanManageUser and checkCanChangeRole", () => {
  it.each([
    ["owner", "self", false, false],
    ["owner", "owner", false, false],
    ["owner", "admin", true, true],
    ["owner", "member", true, true],
    ["admin", "self", false, false],
    ["admin", "owner", false, false],
    ["admin", "admin", false, false],
    ["admin", "member", true, false],
    ["member", "self", false, false],
    ["member", "owner", false, false],
    ["member", "admin", false, false],
    ["member", "member", false, false],
  ] as const)(
    "%s acting on %s: manage %s, change role %s",
    (actorRole, targetKind, canManage, canChangeRole) => {
      const actor = buildActor(actorRole);
      const target = buildTarget(actor, targetKind);

      expect(checkCanManageUser(actor, target)).toBe(canManage);
      expect(checkCanChangeRole(actor, target)).toBe(canChangeRole);
    },
  );
});
