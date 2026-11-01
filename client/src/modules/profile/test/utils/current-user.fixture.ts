import type { CurrentUser } from "@/modules/auth/typing/types/current-user.type";

export const createSignedInUser = (changes: Partial<CurrentUser> = {}): CurrentUser => {
  return {
    id: "8f9c2f43-5d5e-4f7e-9b54-0e8f5f1d2a10",
    email: "ada@example.test",
    name: "Ada Lovelace",
    workspaceRole: "member",
    nextStep: "signed_in",
    language: "en",
    colorScheme: "light",
    avatarFileId: null,
    avatarUrl: null,
    isTwoFactorSetUp: true,
    ...changes,
  };
};
