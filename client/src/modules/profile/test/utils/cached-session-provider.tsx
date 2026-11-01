"use client";

import { SessionGuardContext } from "@/components/session-guard/session-guard.context";
import { GET_CURRENT_USER_KEY } from "@/modules/auth/hooks/queries/use-get-current-user";
import type { CurrentUser } from "@/modules/auth/typing/types/current-user.type";
import { useQuery } from "@tanstack/react-query";
import type { FC, ReactNode } from "react";

interface Props {
  children: ReactNode;
}

const waitForever = (): Promise<CurrentUser> => {
  return new Promise(() => {
    return;
  });
};

export const CachedSessionProvider: FC<Props> = ({ children }) => {
  const { data: currentUser } = useQuery({
    queryKey: [GET_CURRENT_USER_KEY],
    queryFn: waitForever,
    enabled: false,
  });

  if (currentUser === undefined) {
    return null;
  }

  return <SessionGuardContext value={currentUser}>{children}</SessionGuardContext>;
};
