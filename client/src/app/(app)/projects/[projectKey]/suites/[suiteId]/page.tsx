import { SuiteDetailPage } from "@/modules/suites/suite-detail";
import type { Metadata } from "next";
import type { FC } from "react";

export const metadata: Metadata = { title: "Suite" };

const SuiteRoute: FC<PageProps<"/projects/[projectKey]/suites/[suiteId]">> = async ({ params }) => {
  const { suiteId } = await params;

  return <SuiteDetailPage suiteId={suiteId} />;
};

export default SuiteRoute;
