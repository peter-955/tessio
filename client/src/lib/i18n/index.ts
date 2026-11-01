import { Language } from "@/shared/typing/enums/language.enum";
import { createInstance, type i18n as I18nInstance } from "i18next";
import { initReactI18next } from "react-i18next";
import { en } from "./locales/en";
import { fr } from "./locales/fr";
import { vi } from "./locales/vi";

export const createI18nInstance = (language: Language): I18nInstance => {
  const instance = createInstance();

  void instance.use(initReactI18next).init({
    resources: {
      [Language.ENGLISH]: en,
      [Language.FRENCH]: fr,
      [Language.VIETNAMESE]: vi,
    },
    lng: language,
    fallbackLng: Language.ENGLISH,
    defaultNS: "common",
    interpolation: { escapeValue: false },
    initAsync: false,
  });

  return instance;
};
