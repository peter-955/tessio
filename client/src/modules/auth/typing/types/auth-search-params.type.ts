import type { SignInReason } from "../enums/sign-in-reason.enum";

export interface AuthSearchParams {
  nextPath: string;
  reason: SignInReason | null;
}
