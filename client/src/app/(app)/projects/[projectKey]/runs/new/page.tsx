import { NewManualRunPage } from "@/modules/manual-run/new-manual-run";
import { parseInitialStoryKey } from "@/modules/manual-run/utils/initial-story-key.util";
import type { Metadata } from "next";
import type { FC } from "react";

export const metadata: Metadata = { title: "New manual run" };

const NewManualRunRoute: FC<PageProps<"/projects/[projectKey]/runs/new">> = async ({
  searchParams,
}) => {
  const { story } = await searchParams;

  return <NewManualRunPage initialStoryKey={parseInitialStoryKey(story)} />;
};

export default NewManualRunRoute;
