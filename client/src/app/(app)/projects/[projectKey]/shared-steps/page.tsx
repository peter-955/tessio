import { SharedStepsPage } from "@/modules/shared-steps/shared-steps";
import type { Metadata } from "next";
import type { FC } from "react";

export const metadata: Metadata = { title: "Shared steps" };

const SharedStepsRoute: FC = () => {
  return <SharedStepsPage />;
};

export default SharedStepsRoute;
