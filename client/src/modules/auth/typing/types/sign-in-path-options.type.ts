import type { SignInReason } from "../enums/sign-in-reason.enum";

export interface SignInPathOptions {
  nextPath: string;
  reason?: SignInReason | null;
}
