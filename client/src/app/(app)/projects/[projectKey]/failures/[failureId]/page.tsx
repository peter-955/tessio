import { FailureDetailPage } from "@/modules/failures/failure-detail";
import type { Metadata } from "next";
import type { FC } from "react";

export const metadata: Metadata = { title: "Failure" };

const FailureRoute: FC<PageProps<"/projects/[projectKey]/failures/[failureId]">> = async ({
  params,
}) => {
  const { failureId } = await params;

  return <FailureDetailPage failureId={failureId} />;
};

export default FailureRoute;
