import { AppShell } from "@/components/app-shell/app-shell";
import { SessionGuard } from "@/components/session-guard/session-guard";
import { SavedPreferencesSync } from "@/modules/profile/components/saved-preferences-sync/saved-preferences-sync";
import type { FC } from "react";

const AppLayout: FC<LayoutProps<"/">> = ({ children }) => {
  return (
    <SessionGuard>
      <SavedPreferencesSync />
      <AppShell>{children}</AppShell>
    </SessionGuard>
  );
};

export default AppLayout;
