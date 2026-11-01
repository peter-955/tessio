import { useTranslation } from "react-i18next";
import { Language } from "../typing/enums/language.enum";
import { isLanguage, storeLanguage } from "../utils/language.util";

interface Result {
  language: Language;
  changeLanguage: (language: Language) => void;
}

export const useLanguage = (): Result => {
  const { i18n } = useTranslation();

  const changeLanguage = (language: Language): void => {
    storeLanguage(language);
    void i18n.changeLanguage(language);
  };

  return {
    language: isLanguage(i18n.language) ? i18n.language : Language.ENGLISH,
    changeLanguage,
  };
};
