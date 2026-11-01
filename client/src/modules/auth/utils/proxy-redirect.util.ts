import { buildSignInPath, isPublicAuthPath } from "./auth-path.util";

export const resolveProxyRedirectPath = (
  pathname: string,
  search: string,
  hasSessionCookie: boolean,
): string | null => {
  if (hasSessionCookie || isPublicAuthPath(pathname)) {
    return null;
  }

  return buildSignInPath({ nextPath: `${pathname}${search}` });
};
