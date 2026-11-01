import { describe, expect, it } from "vitest";
import { formatRelativeTime } from "./relative-time.util";

const NOW = new Date("2026-11-01T12:00:00Z");

describe("formatRelativeTime", () => {
  it.each([
    ["en", "2026-11-01T11:59:30Z", "now"],
    ["en", "2026-11-01T11:55:00Z", "5 minutes ago"],
    ["en", "2026-11-01T09:00:00Z", "3 hours ago"],
    ["en", "2026-10-30T12:00:00Z", "2 days ago"],
    ["en", "2026-11-01T12:05:00Z", "now"],
    ["fr", "2026-11-01T11:59:30Z", "maintenant"],
    ["fr", "2026-11-01T11:55:00Z", "il y a 5 minutes"],
    ["fr", "2026-11-01T09:00:00Z", "il y a 3 heures"],
    ["fr", "2026-10-30T12:00:00Z", "avant-hier"],
    ["fr", "2026-11-01T12:05:00Z", "maintenant"],
  ])("formats a %s date at %s as %s", (language, isoDate, expected) => {
    expect(formatRelativeTime(isoDate, NOW, language)).toBe(expected);
  });

  it.each(["en", "fr"])("returns null for a date 8 days old in %s", (language) => {
    expect(formatRelativeTime("2026-10-24T12:00:00Z", NOW, language)).toBeNull();
  });

  it("returns null for an invalid date", () => {
    expect(formatRelativeTime("not a date", NOW, "en")).toBeNull();
  });
});
