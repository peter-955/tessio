"use client";

import { useSearchParams } from "next/navigation";
import { NEXT_SEARCH_PARAM, REASON_SEARCH_PARAM } from "../typing/constants/auth-route.constant";
import type { AuthSearchParams } from "../typing/types/auth-search-params.type";
import { resolveNextPath, resolveSignInReason } from "../utils/auth-path.util";

export const useAuthSearchParams = (): AuthSearchParams => {
  const searchParams = useSearchParams();

  return {
    nextPath: resolveNextPath(searchParams.get(NEXT_SEARCH_PARAM)),
    reason: resolveSignInReason(searchParams.get(REASON_SEARCH_PARAM)),
  };
};
