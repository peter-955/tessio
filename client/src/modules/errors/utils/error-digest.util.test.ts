import { describe, expect, it } from "vitest";
import { readErrorDigest } from "./error-digest.util";

describe("readErrorDigest", () => {
  it("reads a string digest only", () => {
    expect(readErrorDigest(Object.assign(new Error("Boom"), { digest: "4021337" }))).toBe(
      "4021337",
    );
    expect(readErrorDigest({ digest: 42 })).toBeNull();
    expect(readErrorDigest(new Error("Boom"))).toBeNull();
    expect(readErrorDigest("Boom")).toBeNull();
    expect(readErrorDigest(null)).toBeNull();
  });
});
