import { GapInboxPage } from "@/modules/gaps/gap-inbox";
import type { Metadata } from "next";
import type { FC } from "react";

export const metadata: Metadata = { title: "My gaps" };

const GapsRoute: FC = () => {
  return <GapInboxPage />;
};

export default GapsRoute;
