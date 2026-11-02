import { PlansPage } from "@/modules/plans/plans";
import type { Metadata } from "next";
import type { FC } from "react";

export const metadata: Metadata = { title: "Plans" };

const PlansRoute: FC = () => {
  return <PlansPage />;
};

export default PlansRoute;
