"use client";

import { useQueryClient } from "@tanstack/react-query";
import { useEffect, useEffectEvent } from "react";
import { LIVE_EVENT_QUERY_KEYS } from "../typing/constants/live-event-query-keys.constant";
import {
  LIVE_EVENTS_INITIAL_RETRY_DELAY_IN_MILLISECONDS,
  LIVE_EVENTS_MAXIMUM_RETRY_DELAY_IN_MILLISECONDS,
  LIVE_EVENTS_READY_EVENT,
  LIVE_EVENTS_RETRY_JITTER_RATIO,
  LIVE_EVENTS_URL,
} from "../typing/constants/live-event.constant";

interface Options {
  isEnabled: boolean;
  onStreamClosed: () => void;
}

interface EventSubscription {
  type: string;
  listener: () => void;
}

const ERROR_EVENT = "error";
const ONLINE_EVENT = "online";

const computeRetryDelay = (attemptCount: number): number => {
  const baseDelay = Math.min(
    LIVE_EVENTS_MAXIMUM_RETRY_DELAY_IN_MILLISECONDS,
    LIVE_EVENTS_INITIAL_RETRY_DELAY_IN_MILLISECONDS * 2 ** attemptCount,
  );

  return baseDelay * (1 + Math.random() * LIVE_EVENTS_RETRY_JITTER_RATIO);
};

export const useLiveEvents = ({ isEnabled, onStreamClosed }: Options): void => {
  const queryClient = useQueryClient();
  const handleStreamClosed = useEffectEvent((): void => {
    onStreamClosed();
  });

  useEffect(() => {
    if (!isEnabled) {
      return;
    }

    let eventSource: EventSource | null = null;
    let retryTimer: ReturnType<typeof setTimeout> | null = null;
    let attemptCount = 0;
    let isReconnecting = false;

    const handleReady = (): void => {
      attemptCount = 0;
      if (isReconnecting) {
        isReconnecting = false;
        void queryClient.invalidateQueries();
      }
    };

    const clearRetryTimer = (): void => {
      if (retryTimer !== null) {
        clearTimeout(retryTimer);
        retryTimer = null;
      }
    };

    const closeEventSource = (): void => {
      if (eventSource === null) {
        return;
      }
      subscriptions.forEach(({ type, listener }) => {
        eventSource?.removeEventListener(type, listener);
      });
      eventSource.close();
      eventSource = null;
    };

    const connect = (): void => {
      clearRetryTimer();
      closeEventSource();
      const nextEventSource = new EventSource(LIVE_EVENTS_URL);
      subscriptions.forEach(({ type, listener }) => {
        nextEventSource.addEventListener(type, listener);
      });
      eventSource = nextEventSource;
    };

    const scheduleReconnect = (): void => {
      clearRetryTimer();
      const delay = computeRetryDelay(attemptCount);
      attemptCount += 1;
      retryTimer = setTimeout(connect, delay);
    };

    const handleError = (): void => {
      closeEventSource();
      isReconnecting = true;
      handleStreamClosed();
      scheduleReconnect();
    };

    const handleOnline = (): void => {
      if (eventSource === null) {
        connect();
      }
    };

    const eventTypeSubscriptions = Object.entries(LIVE_EVENT_QUERY_KEYS).map(
      ([type, queryKeys]): EventSubscription => {
        return {
          type,
          listener: (): void => {
            queryKeys.forEach((queryKey) => {
              void queryClient.invalidateQueries({ queryKey: [queryKey] });
            });
          },
        };
      },
    );
    const subscriptions: readonly EventSubscription[] = [
      { type: LIVE_EVENTS_READY_EVENT, listener: handleReady },
      { type: ERROR_EVENT, listener: handleError },
      ...eventTypeSubscriptions,
    ];

    window.addEventListener(ONLINE_EVENT, handleOnline);
    connect();

    return (): void => {
      window.removeEventListener(ONLINE_EVENT, handleOnline);
      clearRetryTimer();
      closeEventSource();
    };
  }, [isEnabled, queryClient]);
};
