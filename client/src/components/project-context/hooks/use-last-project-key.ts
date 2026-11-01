"use client";

import { useSyncExternalStore } from "react";
import {
  readLastProjectKey,
  removeLastProjectKey,
  storeLastProjectKey,
  subscribeToLastProjectKey,
} from "../utils/last-project-key.util";

interface Result {
  lastProjectKey: string | null;
  rememberProjectKey: (projectKey: string) => void;
  forgetProjectKey: (projectKey: string) => void;
}

const readServerLastProjectKey = (): string | null => {
  return null;
};

export const useLastProjectKey = (): Result => {
  const lastProjectKey = useSyncExternalStore(
    subscribeToLastProjectKey,
    readLastProjectKey,
    readServerLastProjectKey,
  );

  return {
    lastProjectKey,
    rememberProjectKey: storeLastProjectKey,
    forgetProjectKey: removeLastProjectKey,
  };
};
