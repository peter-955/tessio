import { AiHarnessPage } from "@/modules/ai-harness/ai-harness";
import type { Metadata } from "next";
import type { FC } from "react";

export const metadata: Metadata = { title: "AI Harness" };

const AiHarnessRoute: FC = () => {
  return <AiHarnessPage />;
};

export default AiHarnessRoute;
