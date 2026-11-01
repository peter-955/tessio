import type { CurrentUser } from "../../typing/types/current-user.type";
import type { SignInStep } from "../../typing/types/sign-in-step.type";

export const createCurrentUser = (nextStep: SignInStep): CurrentUser => {
  return {
    id: "8f9c2f43-5d5e-4f7e-9b54-0e8f5f1d2a10",
    email: "ada@example.test",
    name: "Ada Lovelace",
    workspaceRole: "member",
    nextStep,
  } as CurrentUser;
};
