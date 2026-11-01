import type { E2eUser, E2eUserWithTotpKey } from "../types/e2e-user.type.ts";

export const OWNER: E2eUserWithTotpKey = {
  name: "Olivia Owner",
  email: "owner@tessio.test",
  password: "Owner e2e password 2026",
  totpKey: "JBSWY3DPEHPK3PXPJBSWY3DPEHPK3PXP",
};

export const QC: E2eUser = {
  name: "Quinn Tester",
  email: "quinn.qc@tessio.test",
  password: "Quinn e2e password 2026",
};

export const DEV: E2eUser = {
  name: "Devon Builder",
  email: "devon.dev@tessio.test",
  password: "Devon e2e password 2026",
};
