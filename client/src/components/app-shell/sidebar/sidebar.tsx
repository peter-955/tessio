"use client";

import { DSLogo } from "@/components/design-system";
import Link from "next/link";
import type { FC } from "react";
import { ProjectNavigation } from "./project-navigation/project-navigation";
import styles from "./sidebar.module.scss";
import { WorkspaceNavigation } from "./workspace-navigation/workspace-navigation";

interface Props {
  onNavigate?: () => void;
}

export const Sidebar: FC<Props> = ({ onNavigate }) => {
  return (
    <div className={styles.sidebar}>
      <Link href="/" className={styles.brand} onClick={onNavigate}>
        <DSLogo hasWordmark />
      </Link>
      <ProjectNavigation onNavigate={onNavigate} />
      <WorkspaceNavigation onNavigate={onNavigate} />
    </div>
  );
};
