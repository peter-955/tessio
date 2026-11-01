import type { CurrentUser } from "@/modules/auth/typing/types/current-user.type";
import { CURRENT_USER_ID } from "../utils/failure-fixture.util";

export const currentUserMock = {
  useCurrentUser: (): CurrentUser => {
    return {
      id: CURRENT_USER_ID,
      email: "quinn@example.test",
      name: "Quinn Qc",
      workspaceRole: "member",
      nextStep: "signed_in",
      language: "en",
      colorScheme: "auto",
      avatarFileId: null,
      avatarUrl: null,
      isTwoFactorSetUp: true,
    };
  },
};
