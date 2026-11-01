import { StoriesPage } from "@/modules/stories/stories";
import { parseStoryFilters } from "@/modules/stories/utils/story-filters.util";
import type { Metadata } from "next";
import type { FC } from "react";

export const metadata: Metadata = { title: "Stories" };

const StoriesRoute: FC<PageProps<"/projects/[projectKey]/stories">> = async ({ searchParams }) => {
  return <StoriesPage initialFilters={parseStoryFilters(await searchParams)} />;
};

export default StoriesRoute;
