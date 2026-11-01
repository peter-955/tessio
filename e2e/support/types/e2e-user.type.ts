export interface E2eUser {
  name: string;
  email: string;
  password: string;
}

export interface E2eUserWithTotpKey extends E2eUser {
  totpKey: string;
}

export interface TwoFactorSetupResult {
  totpKey: string;
  recoveryCodes: string[];
}
