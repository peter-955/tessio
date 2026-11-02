import { PlanDetailPage } from "@/modules/plans/plan-detail";
import type { Metadata } from "next";
import type { FC } from "react";

export const metadata: Metadata = { title: "Plan" };

const PlanRoute: FC<PageProps<"/projects/[projectKey]/plans/[planId]">> = async ({ params }) => {
  const { planId } = await params;

  return <PlanDetailPage planId={planId} />;
};

export default PlanRoute;
