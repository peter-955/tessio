import { describe, expect, it } from "vitest";
import { resolveProxyRedirectPath } from "./proxy-redirect.util";

describe("resolveProxyRedirectPath", () => {
  it("sends a cookieless request to sign in and keeps the path and query as next", () => {
    expect(resolveProxyRedirectPath("/projects/SHOP/runs", "?x=1", false)).toBe(
      "/sign-in?next=%2Fprojects%2FSHOP%2Fruns%3Fx%3D1",
    );
  });

  it("sends the cookieless home page to sign in without next", () => {
    expect(resolveProxyRedirectPath("/", "", false)).toBe("/sign-in");
  });

  it.each(["/sign-in", "/forgot-password", "/invite/token-value", "/reset-password/token-value"])(
    "lets the public page %s through without a cookie",
    (pathname) => {
      expect(resolveProxyRedirectPath(pathname, "", false)).toBeNull();
    },
  );

  it.each(["/two-factor", "/two-factor/setup"])(
    "redirects %s without the half-session cookie",
    (pathname) => {
      expect(resolveProxyRedirectPath(pathname, "", false)).toBe(
        `/sign-in?next=${encodeURIComponent(pathname)}`,
      );
    },
  );

  it("lets every page through when the session cookie is present", () => {
    expect(resolveProxyRedirectPath("/projects/SHOP/runs", "?x=1", true)).toBeNull();
    expect(resolveProxyRedirectPath("/two-factor", "", true)).toBeNull();
  });
});
