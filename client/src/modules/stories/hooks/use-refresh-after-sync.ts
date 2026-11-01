"use client";

import { GET_SPRINT_KEY } from "@/modules/sprints/hooks/queries/use-get-sprint";
import { GET_SPRINTS_KEY } from "@/modules/sprints/hooks/queries/use-get-sprints";
import { useQueryClient } from "@tanstack/react-query";
import { useEffect, useRef } from "react";
import { IN_PROGRESS_SYNC_STATUSES } from "../typing/constants/sync.constant";
import type { ProjectSyncStatus } from "../typing/types/story.type";
import { GET_STORIES_KEY } from "./queries/use-get-stories";
import { GET_STORY_KEY } from "./queries/use-get-story";

const REFRESHED_QUERY_KEYS = [GET_SPRINTS_KEY, GET_SPRINT_KEY, GET_STORIES_KEY, GET_STORY_KEY];

export const useRefreshAfterSync = (status: ProjectSyncStatus | undefined): void => {
  const queryClient = useQueryClient();
  const previousStatus = useRef(status);

  useEffect(() => {
    const lastStatus = previousStatus.current;
    previousStatus.current = status;

    if (
      lastStatus === undefined ||
      !IN_PROGRESS_SYNC_STATUSES.includes(lastStatus) ||
      status !== "succeeded"
    ) {
      return;
    }

    REFRESHED_QUERY_KEYS.forEach((queryKey) => {
      void queryClient.invalidateQueries({ queryKey: [queryKey] });
    });
  }, [queryClient, status]);
};
