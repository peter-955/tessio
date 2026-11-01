import type { CurrentUser } from "@/modules/auth/typing/types/current-user.type";
import { CURRENT_USER_ID } from "../utils/gap.fixture";

export const currentUserMock = {
  useCurrentUser: (): CurrentUser => {
    return {
      id: CURRENT_USER_ID,
      email: "dana@example.test",
      name: "Dana Dev",
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
