import { InsightsPage } from "@/modules/insights/insights";
import type { Metadata } from "next";
import type { FC } from "react";

export const metadata: Metadata = { title: "Insights" };

const InsightsRoute: FC = () => {
  return <InsightsPage />;
};

export default InsightsRoute;
