import { NewTestCasePage } from "@/modules/test-cases/new-test-case";
import { parseInitialStoryKey } from "@/modules/test-cases/utils/initial-story-key.util";
import type { Metadata } from "next";
import type { FC } from "react";

export const metadata: Metadata = { title: "New test case" };

const NewTestCaseRoute: FC<PageProps<"/projects/[projectKey]/test-cases/new">> = async ({
  searchParams,
}) => {
  const { story } = await searchParams;

  return <NewTestCasePage initialStoryKey={parseInitialStoryKey(story)} />;
};

export default NewTestCaseRoute;
