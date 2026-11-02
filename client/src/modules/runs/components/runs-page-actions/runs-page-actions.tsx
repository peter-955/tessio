"use client";

import { DSGroup } from "@/components/design-system";
import { ImportJunitButton } from "@/modules/junit-import/components/import-junit-button/import-junit-button";
import { NewManualRunButtonLink } from "@/modules/manual-run/components/new-manual-run-button-link/new-manual-run-button-link";
import type { FC } from "react";

export const RunsPageActions: FC = () => {
  return (
    <DSGroup gap={2} isWrapping>
      <ImportJunitButton />
      <NewManualRunButtonLink />
    </DSGroup>
  );
};
