import { SESSION_COOKIE_NAME } from "@/modules/auth/typing/constants/session.constant";
import { resolveProxyRedirectPath } from "@/modules/auth/utils/proxy-redirect.util";
import { NextResponse, type NextRequest } from "next/server";

export const proxy = (request: NextRequest): NextResponse => {
  const { pathname, search } = request.nextUrl;
  const redirectPath = resolveProxyRedirectPath(
    pathname,
    search,
    request.cookies.has(SESSION_COOKIE_NAME),
  );

  if (redirectPath === null) {
    return NextResponse.next();
  }

  return NextResponse.redirect(new URL(redirectPath, request.url));
};

export const config = {
  matcher: ["/((?!api|mcp|_next/static|_next/image|.*\\..*).*)"],
};
