import { describe, expect, it } from "vitest";
import { formatUnreadCount } from "./unread-count.util";

describe("formatUnreadCount", () => {
  it.each([
    [0, "0"],
    [99, "99"],
    [100, "99+"],
  ])("formats %i as %s", (count, expected) => {
    expect(formatUnreadCount(count)).toBe(expected);
  });
});
