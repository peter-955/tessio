import englishLabels from "@/lib/i18n/locales/en/labels.json";
import englishSuites from "@/lib/i18n/locales/en/suites.json";
import frenchLabels from "@/lib/i18n/locales/fr/labels.json";
import frenchSuites from "@/lib/i18n/locales/fr/suites.json";
import vietnameseLabels from "@/lib/i18n/locales/vi/labels.json";
import vietnameseSuites from "@/lib/i18n/locales/vi/suites.json";
import { describe, expect, it } from "vitest";

describe("suite locales", () => {
  it.each([
    ["en", englishSuites, englishLabels],
    ["fr", frenchSuites, frenchLabels],
    ["vi", vietnameseSuites, vietnameseLabels],
  ])("names labels in %s the way the labels pages do", (_language, suites, labels) => {
    expect(suites.filter.labels).toBe(labels.filter.label);
  });

  it("never says label in the French text", () => {
    const readTexts = (value: unknown): string[] => {
      if (typeof value === "string") {
        return [value];
      }

      return typeof value === "object" && value !== null
        ? Object.values(value).flatMap(readTexts)
        : [];
    };

    expect(readTexts(frenchSuites).filter((text) => /\blabels?\b/i.test(text))).toEqual([]);
  });
});
