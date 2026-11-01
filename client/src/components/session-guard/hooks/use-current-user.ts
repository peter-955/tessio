"use client";

import type { CurrentUser } from "@/modules/auth/typing/types/current-user.type";
import { use } from "react";
import { SessionGuardContext } from "../session-guard.context";

export const useCurrentUser = (): CurrentUser => {
  const currentUser = use(SessionGuardContext);

  if (currentUser === null) {
    throw new Error("useCurrentUser must be used inside SessionGuard.");
  }

  return currentUser;
};
