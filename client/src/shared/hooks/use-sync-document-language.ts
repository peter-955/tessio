import { useEffect } from "react";

export const useSyncDocumentLanguage = (language: string): void => {
  useEffect(() => {
    document.documentElement.lang = language;
  }, [language]);
};
