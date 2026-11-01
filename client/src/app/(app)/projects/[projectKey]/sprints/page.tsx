import { SprintsPage } from "@/modules/sprints/sprints";
import type { Metadata } from "next";
import type { FC } from "react";

export const metadata: Metadata = { title: "Sprints" };

const SprintsRoute: FC = () => {
  return <SprintsPage />;
};

export default SprintsRoute;
