"use client";

import { useLanguage } from "@/shared/hooks/use-language";
import type { Language } from "@/shared/typing/enums/language.enum";
import { usePatchMe } from "./mutations/use-patch-me";

export const useSaveLanguage = (): ((language: Language) => void) => {
  const { changeLanguage } = useLanguage();
  const { mutate: patchMe } = usePatchMe();

  return (language: Language): void => {
    changeLanguage(language);
    patchMe({ language });
  };
};
