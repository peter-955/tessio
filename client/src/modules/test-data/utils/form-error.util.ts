import type { ReactNode } from "react";

export const toFormErrorText = (error: ReactNode): string | undefined => {
  return typeof error === "string" ? error : undefined;
};
