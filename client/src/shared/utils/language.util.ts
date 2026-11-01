import {
  LANGUAGE_COOKIE_MAX_AGE_IN_SECONDS,
  LANGUAGE_COOKIE_NAME,
} from "../typing/constants/language.constant";
import { Language } from "../typing/enums/language.enum";

export const isLanguage = (value: string | null | undefined): value is Language => {
  return Object.values(Language).some((language) => {
    return language === value;
  });
};

export const storeLanguage = (language: Language): void => {
  document.cookie = `${LANGUAGE_COOKIE_NAME}=${language}; path=/; max-age=${LANGUAGE_COOKIE_MAX_AGE_IN_SECONDS}; samesite=lax`;
};
