import { SharedStepDetailPage } from "@/modules/shared-steps/shared-step-detail";
import type { Metadata } from "next";
import type { FC } from "react";

export const metadata: Metadata = { title: "Shared step" };

const SharedStepRoute: FC<PageProps<"/projects/[projectKey]/shared-steps/[key]">> = async ({
  params,
}) => {
  const { key } = await params;

  return <SharedStepDetailPage sharedStepKey={key} />;
};

export default SharedStepRoute;
