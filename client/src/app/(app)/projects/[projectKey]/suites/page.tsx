import { SuitesPage } from "@/modules/suites/suites";
import type { Metadata } from "next";
import type { FC } from "react";

export const metadata: Metadata = { title: "Suites" };

const SuitesRoute: FC = () => {
  return <SuitesPage />;
};

export default SuitesRoute;
