import { WorkspaceSettingsPage } from "@/modules/settings/workspace-settings";
import type { Metadata } from "next";
import type { FC } from "react";

export const metadata: Metadata = { title: "Workspace settings" };

const SettingsRoute: FC = () => {
  return <WorkspaceSettingsPage />;
};

export default SettingsRoute;
