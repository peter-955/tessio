import { LANGUAGE_COOKIE_NAME } from "@/shared/typing/constants/language.constant";
import { Language } from "@/shared/typing/enums/language.enum";
import { isLanguage } from "@/shared/utils/language.util";

export const readLanguageFromDocument = (): Language => {
  if (typeof document === "undefined") {
    return Language.ENGLISH;
  }

  const languageCookie = document.cookie
    .split(";")
    .map((cookie) => {
      return cookie.trim();
    })
    .find((cookie) => {
      return cookie.startsWith(`${LANGUAGE_COOKIE_NAME}=`);
    });
  const storedLanguage = languageCookie?.slice(LANGUAGE_COOKIE_NAME.length + 1);

  return isLanguage(storedLanguage) ? storedLanguage : Language.ENGLISH;
};

export const subscribeToNothing = (): (() => void) => {
  return () => {
    return;
  };
};
