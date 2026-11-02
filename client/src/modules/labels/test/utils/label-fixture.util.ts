import type { CaseLabel, Label } from "../../typing/types/label.type";

export const SMOKE_LABEL_ID = "c1000000-0000-4000-8000-000000000001";

export const CHECKOUT_LABEL_ID = "c1000000-0000-4000-8000-000000000002";

export const buildLabel = (overrides: Partial<Label> = {}): Label => {
  return {
    id: SMOKE_LABEL_ID,
    name: "smoke",
    color: "green",
    caseCount: 3,
    createdAt: "2026-10-20T09:00:00Z",
    ...overrides,
  };
};

export const toCaseLabel = (label: Label): CaseLabel => {
  return { id: label.id, name: label.name, color: label.color };
};
