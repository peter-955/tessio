import { FailuresPage } from "@/modules/failures/failures";
import { parseFailureFilters } from "@/modules/failures/utils/failure-filters.util";
import type { Metadata } from "next";
import type { FC } from "react";

export const metadata: Metadata = { title: "Failures" };

const FailuresRoute: FC<PageProps<"/projects/[projectKey]/failures">> = async ({
  searchParams,
}) => {
  return <FailuresPage initialFilters={parseFailureFilters(await searchParams)} />;
};

export default FailuresRoute;
