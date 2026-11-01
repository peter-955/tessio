import type { components } from "@/lib/api/openapi.type";

export type SignInRequest = components["schemas"]["SignInRequest"];

export type SignInResponse = components["schemas"]["SignInResponse"];

export type TwoFactorCodeRequest = components["schemas"]["TwoFactorCodeRequest"];

export type TwoFactorSetupResponse = components["schemas"]["TwoFactorSetupResponse"];

export type RecoveryCodesResponse = components["schemas"]["RecoveryCodesResponse"];

export type ForgotPasswordRequest = components["schemas"]["ForgotPasswordRequest"];

export type ResetPasswordRequest = components["schemas"]["ResetPasswordRequest"];

export interface AcceptInviteVariables {
  token: string;
  password: string;
}
