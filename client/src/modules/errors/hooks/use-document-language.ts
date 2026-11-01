"use client";

import { Language } from "@/shared/typing/enums/language.enum";
import { useSyncExternalStore } from "react";
import { readLanguageFromDocument, subscribeToNothing } from "../utils/document-language.util";

const readServerLanguage = (): Language => {
  return Language.ENGLISH;
};

export const useDocumentLanguage = (): Language => {
  return useSyncExternalStore(subscribeToNothing, readLanguageFromDocument, readServerLanguage);
};
