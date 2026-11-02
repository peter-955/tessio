"use client";

import { DSBadge, DSGroup, DSText } from "@/components/design-system";
import type { FC } from "react";
import { useTranslation } from "react-i18next";
import type { ProjectRole } from "../../typing/types/ai-harness.type";

interface Props {
  roles: readonly ProjectRole[];
}

export const RoleBadges: FC<Props> = ({ roles }) => {
  const { t } = useTranslation("aiHarness");

  if (roles.length === 0) {
    return (
      <DSText size="sm" color="muted" component="span">
        {t("mcp.noRoles")}
      </DSText>
    );
  }

  return (
    <DSGroup gap={1} isWrapping>
      {roles.map((role) => {
        return <DSBadge key={role}>{t(`roles.${role}`)}</DSBadge>;
      })}
    </DSGroup>
  );
};
