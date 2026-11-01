import {
  NEXT_SEARCH_PARAM,
  REASON_SEARCH_PARAM,
  SIGN_IN_PATH,
  TWO_FACTOR_PATH,
  TWO_FACTOR_SETUP_PATH,
} from "../typing/constants/auth-route.constant";
import {
  DEFAULT_NEXT_PATH,
  PUBLIC_AUTH_PATH_PREFIXES,
  PUBLIC_AUTH_PATHS,
} from "../typing/constants/session.constant";
import { SignInReason } from "../typing/enums/sign-in-reason.enum";
import type { SignInPathOptions } from "../typing/types/sign-in-path-options.type";
import type { SignInStep } from "../typing/types/sign-in-step.type";

const LAST_CONTROL_CHARACTER_CODE = 31;
const DELETE_CHARACTER_CODE = 127;

const hasControlCharacter = (value: string): boolean => {
  return [...value].some((character) => {
    const characterCode = character.charCodeAt(0);
    return characterCode <= LAST_CONTROL_CHARACTER_CODE || characterCode === DELETE_CHARACTER_CODE;
  });
};

const buildPathWithNext = (path: string, nextPath: string): string => {
  if (nextPath === DEFAULT_NEXT_PATH) {
    return path;
  }

  const searchParams = new URLSearchParams({ [NEXT_SEARCH_PARAM]: nextPath });

  return `${path}?${searchParams.toString()}`;
};

export const resolveNextPath = (value: string | null): string => {
  if (
    value === null ||
    !value.startsWith("/") ||
    value.startsWith("//") ||
    value.startsWith("/\\") ||
    hasControlCharacter(value)
  ) {
    return DEFAULT_NEXT_PATH;
  }

  return value;
};

export const resolveSignInReason = (value: string | null): SignInReason | null => {
  const reasons: readonly string[] = Object.values(SignInReason);
  if (value === null || !reasons.includes(value)) {
    return null;
  }

  return value as SignInReason;
};

export const buildSignInPath = ({ nextPath, reason = null }: SignInPathOptions): string => {
  const searchParams = new URLSearchParams();
  if (nextPath !== DEFAULT_NEXT_PATH) {
    searchParams.set(NEXT_SEARCH_PARAM, nextPath);
  }
  if (reason !== null) {
    searchParams.set(REASON_SEARCH_PARAM, reason);
  }

  const query = searchParams.toString();

  return query === "" ? SIGN_IN_PATH : `${SIGN_IN_PATH}?${query}`;
};

export const buildSignInStepPath = (step: SignInStep, nextPath: string): string => {
  switch (step) {
    case "two_factor_setup_required":
      return buildPathWithNext(TWO_FACTOR_SETUP_PATH, nextPath);
    case "two_factor_required":
      return buildPathWithNext(TWO_FACTOR_PATH, nextPath);
    case "signed_in":
      return nextPath;
  }
};

export const buildCurrentPath = (pathname: string, query: string): string => {
  return query === "" ? pathname : `${pathname}?${query}`;
};

export const isPublicAuthPath = (pathname: string): boolean => {
  return (
    PUBLIC_AUTH_PATHS.includes(pathname) ||
    PUBLIC_AUTH_PATH_PREFIXES.some((prefix) => {
      return pathname.startsWith(prefix);
    })
  );
};
