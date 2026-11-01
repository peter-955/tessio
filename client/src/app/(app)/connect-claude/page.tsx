import { ConnectClaudePage } from "@/modules/connect-claude/connect-claude";
import type { Metadata } from "next";
import type { FC } from "react";

export const metadata: Metadata = { title: "Connect Claude" };

const ConnectClaudeRoute: FC = () => {
  return <ConnectClaudePage />;
};

export default ConnectClaudeRoute;
