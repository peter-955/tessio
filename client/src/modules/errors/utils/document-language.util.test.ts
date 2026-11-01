import { LANGUAGE_COOKIE_NAME } from "@/shared/typing/constants/language.constant";
import { Language } from "@/shared/typing/enums/language.enum";
import { afterEach, describe, expect, it } from "vitest";
import { readLanguageFromDocument } from "./document-language.util";

const setLanguageCookie = (value: string): void => {
  document.cookie = `${LANGUAGE_COOKIE_NAME}=${value}; path=/`;
};

afterEach(() => {
  document.cookie = `${LANGUAGE_COOKIE_NAME}=; path=/; max-age=0`;
});

describe("readLanguageFromDocument", () => {
  it("reads the language cookie", () => {
    document.cookie = "another=value; path=/";
    setLanguageCookie(Language.VIETNAMESE);

    expect(readLanguageFromDocument()).toBe(Language.VIETNAMESE);
  });

  it("falls back to English without a valid cookie", () => {
    expect(readLanguageFromDocument()).toBe(Language.ENGLISH);

    setLanguageCookie("de");

    expect(readLanguageFromDocument()).toBe(Language.ENGLISH);
  });
});
