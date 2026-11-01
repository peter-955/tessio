"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { SECRET_REVEAL_DURATION_IN_MILLISECONDS } from "../typing/constants/test-data.constant";
import type { RevealedSecrets } from "../typing/types/revealed-secrets.type";
import { usePostRevealSecret } from "./mutations/use-post-reveal-secret";

const withoutKey = <Value>(record: Record<string, Value>, key: string): Record<string, Value> => {
  return Object.fromEntries(Object.entries(record).filter(([entryKey]) => entryKey !== key));
};

export const useRevealedSecrets = (projectKey: string): RevealedSecrets => {
  const [revealedValueById, setRevealedValueById] = useState<Record<string, string>>({});
  const [revealingItemIds, setRevealingItemIds] = useState<readonly string[]>([]);
  const hideTimeoutByIdRef = useRef(new Map<string, ReturnType<typeof setTimeout>>());
  const isMountedRef = useRef(false);
  const { mutateAsync: requestReveal, reset: resetRevealRequest } = usePostRevealSecret(projectKey);

  const clearHideTimeout = useCallback((itemId: string): void => {
    const hideTimeout = hideTimeoutByIdRef.current.get(itemId);
    if (hideTimeout !== undefined) {
      clearTimeout(hideTimeout);
      hideTimeoutByIdRef.current.delete(itemId);
    }
  }, []);

  const hide = useCallback(
    (itemId: string): void => {
      clearHideTimeout(itemId);
      setRevealedValueById((currentValueById) => {
        return itemId in currentValueById ? withoutKey(currentValueById, itemId) : currentValueById;
      });
    },
    [clearHideTimeout],
  );

  const reveal = useCallback(
    async (itemId: string): Promise<void> => {
      setRevealingItemIds((currentItemIds) => [...currentItemIds, itemId]);

      try {
        const { value } = await requestReveal(itemId);
        resetRevealRequest();
        if (!isMountedRef.current) {
          return;
        }

        clearHideTimeout(itemId);
        hideTimeoutByIdRef.current.set(
          itemId,
          setTimeout(() => {
            hide(itemId);
          }, SECRET_REVEAL_DURATION_IN_MILLISECONDS),
        );
        setRevealedValueById((currentValueById) => ({ ...currentValueById, [itemId]: value }));
      } catch {
        return;
      } finally {
        if (isMountedRef.current) {
          setRevealingItemIds((currentItemIds) => {
            return currentItemIds.filter((currentItemId) => currentItemId !== itemId);
          });
        }
      }
    },
    [clearHideTimeout, hide, requestReveal, resetRevealRequest],
  );

  const isRevealing = useCallback(
    (itemId: string): boolean => {
      return revealingItemIds.includes(itemId);
    },
    [revealingItemIds],
  );

  useEffect(() => {
    isMountedRef.current = true;
    const hideTimeoutById = hideTimeoutByIdRef.current;

    return (): void => {
      isMountedRef.current = false;
      hideTimeoutById.forEach((hideTimeout) => {
        clearTimeout(hideTimeout);
      });
      hideTimeoutById.clear();
    };
  }, []);

  return { revealedValueById, reveal, hide, isRevealing };
};
