import { cookies } from "next/headers";
import { LANGUAGE_COOKIE_NAME } from "../typing/constants/language.constant";
import { Language } from "../typing/enums/language.enum";
import { isLanguage } from "./language.util";

export const readLanguageFromCookies = async (): Promise<Language> => {
  const cookieStore = await cookies();
  const storedLanguage = cookieStore.get(LANGUAGE_COOKIE_NAME)?.value;

  return isLanguage(storedLanguage) ? storedLanguage : Language.ENGLISH;
};
