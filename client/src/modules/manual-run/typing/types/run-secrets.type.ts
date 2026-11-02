import type { CaseSecretReveal } from "@/components/case-sheet/typing/types/case-sheet.type";

export interface RunSecrets {
  revealedValues: Readonly<Record<string, string>>;
  secretReveal: CaseSecretReveal;
  hideAll: () => void;
}
