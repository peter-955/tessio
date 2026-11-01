"use client";

import { useLastProjectKey } from "@/components/project-context/hooks/use-last-project-key";
import { useParams } from "next/navigation";

export const useActiveProjectKey = (): string | null => {
  const { projectKey } = useParams<{ projectKey?: string }>();
  const { lastProjectKey } = useLastProjectKey();

  return typeof projectKey === "string" ? projectKey : lastProjectKey;
};
