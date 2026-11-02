"use client";

import { useState } from "react";
import type { RunSecrets } from "../typing/types/run-secrets.type";
import { usePostResolveData } from "./mutations/use-post-resolve-data";

export const useRunSecrets = (
  projectKey: string,
  runId: string,
  canReveal: boolean,
): RunSecrets => {
  const [revealedValues, setRevealedValues] = useState<Record<string, string>>({});
  const [revealingKeys, setRevealingKeys] = useState<readonly string[]>([]);
  const { mutateAsync: resolveData } = usePostResolveData(projectKey, runId);

  const reveal = async (key: string): Promise<void> => {
    setRevealingKeys((currentKeys) => [...currentKeys, key]);
    try {
      const { values } = await resolveData({ keys: [key] });
      setRevealedValues((currentValues) => ({ ...currentValues, ...values }));
    } catch {
      return;
    } finally {
      setRevealingKeys((currentKeys) => {
        return currentKeys.filter((currentKey) => currentKey !== key);
      });
    }
  };

  const hide = (key: string): void => {
    setRevealedValues((currentValues) => {
      return Object.fromEntries(
        Object.entries(currentValues).filter(([currentKey]) => currentKey !== key),
      );
    });
  };

  return {
    revealedValues,
    secretReveal: {
      canReveal,
      isRevealing: (key) => {
        return revealingKeys.includes(key);
      },
      onReveal: (key) => {
        void reveal(key);
      },
      onHide: hide,
    },
    hideAll: () => {
      setRevealedValues({});
    },
  };
};
