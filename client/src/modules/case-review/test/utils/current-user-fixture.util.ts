import type { CurrentUser } from "@/modules/auth/typing/types/current-user.type";
import { QC_USER_ID } from "@/modules/test-cases/test/utils/test-case-fixture.util";

export const buildCurrentUser = (overrides: Partial<CurrentUser> = {}): CurrentUser => {
  return {
    id: QC_USER_ID,
    email: "quinn@example.test",
    name: "Quinn Tester",
    workspaceRole: "member",
    nextStep: "signed_in",
    language: "en",
    colorScheme: "auto",
    avatarFileId: null,
    avatarUrl: null,
    isTwoFactorSetUp: true,
    ...overrides,
  };
};
