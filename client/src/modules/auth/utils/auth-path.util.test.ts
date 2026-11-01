import { describe, expect, it } from "vitest";
import { SignInReason } from "../typing/enums/sign-in-reason.enum";
import {
  buildCurrentPath,
  buildSignInPath,
  buildSignInStepPath,
  isPublicAuthPath,
  resolveNextPath,
  resolveSignInReason,
} from "./auth-path.util";

describe("resolveNextPath", () => {
  it.each([
    ["/projects/SHOP/runs", "/projects/SHOP/runs"],
    ["/projects/SHOP/runs?status=failed#top", "/projects/SHOP/runs?status=failed#top"],
    ["/", "/"],
  ])("keeps the same-origin path %s", (value, expected) => {
    expect(resolveNextPath(value)).toBe(expected);
  });

  it.each([
    ["null", null],
    ["an empty value", ""],
    ["a protocol-relative URL", "//evil.com"],
    ["an absolute URL", "https://x"],
    ["a backslash URL", "/\\evil"],
    ["a relative path", "runs"],
    ["a javascript URL", "javascript:alert(1)"],
    ["a path with a tab", "/\t/evil.com"],
    ["a path with a newline", "/\n/evil.com"],
  ])("falls back to / for %s", (_description, value) => {
    expect(resolveNextPath(value)).toBe("/");
  });
});

describe("resolveSignInReason", () => {
  it("accepts the known reasons and rejects others", () => {
    expect(resolveSignInReason("expired")).toBe(SignInReason.EXPIRED);
    expect(resolveSignInReason("password_reset")).toBe(SignInReason.PASSWORD_RESET);
    expect(resolveSignInReason("other")).toBeNull();
    expect(resolveSignInReason(null)).toBeNull();
  });
});

describe("buildSignInPath", () => {
  it("omits next when it is the home page", () => {
    expect(buildSignInPath({ nextPath: "/" })).toBe("/sign-in");
  });

  it("encodes next and adds the reason", () => {
    expect(
      buildSignInPath({ nextPath: "/projects/SHOP/runs?x=1&y=2", reason: SignInReason.EXPIRED }),
    ).toBe("/sign-in?next=%2Fprojects%2FSHOP%2Fruns%3Fx%3D1%26y%3D2&reason=expired");
  });

  it("adds only the reason for the home page", () => {
    expect(buildSignInPath({ nextPath: "/", reason: SignInReason.PASSWORD_RESET })).toBe(
      "/sign-in?reason=password_reset",
    );
  });
});

describe("buildSignInStepPath", () => {
  it("routes each step and keeps next", () => {
    expect(buildSignInStepPath("two_factor_setup_required", "/projects/SHOP/runs")).toBe(
      "/two-factor/setup?next=%2Fprojects%2FSHOP%2Fruns",
    );
    expect(buildSignInStepPath("two_factor_required", "/projects/SHOP/runs")).toBe(
      "/two-factor?next=%2Fprojects%2FSHOP%2Fruns",
    );
    expect(buildSignInStepPath("signed_in", "/projects/SHOP/runs")).toBe("/projects/SHOP/runs");
  });

  it("omits next for the home page", () => {
    expect(buildSignInStepPath("two_factor_required", "/")).toBe("/two-factor");
    expect(buildSignInStepPath("two_factor_setup_required", "/")).toBe("/two-factor/setup");
    expect(buildSignInStepPath("signed_in", "/")).toBe("/");
  });
});

describe("buildCurrentPath", () => {
  it("joins the pathname and the query", () => {
    expect(buildCurrentPath("/projects/SHOP/runs", "x=1")).toBe("/projects/SHOP/runs?x=1");
    expect(buildCurrentPath("/projects/SHOP/runs", "")).toBe("/projects/SHOP/runs");
  });
});

describe("isPublicAuthPath", () => {
  it.each(["/sign-in", "/forgot-password", "/invite/abc", "/reset-password/abc"])(
    "treats %s as public",
    (pathname) => {
      expect(isPublicAuthPath(pathname)).toBe(true);
    },
  );

  it.each([
    "/",
    "/projects/SHOP/runs",
    "/two-factor",
    "/two-factor/setup",
    "/sign-in-other",
    "/invite",
  ])("treats %s as protected", (pathname) => {
    expect(isPublicAuthPath(pathname)).toBe(false);
  });
});
