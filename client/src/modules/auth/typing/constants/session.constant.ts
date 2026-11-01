import { FORGOT_PASSWORD_PATH, SIGN_IN_PATH } from "./auth-route.constant";

export const SESSION_COOKIE_NAME = "tessio_session";

export const PUBLIC_AUTH_PATHS: readonly string[] = [SIGN_IN_PATH, FORGOT_PASSWORD_PATH];

export const PUBLIC_AUTH_PATH_PREFIXES: readonly string[] = ["/invite/", "/reset-password/"];

export const DEFAULT_NEXT_PATH = "/";
