import { DSIcon, type DSIconName } from "@/components/design-system";
import Link from "next/link";
import type { FC } from "react";
import styles from "./navigation-link.module.scss";

interface Props {
  href: string;
  icon: DSIconName;
  label: string;
  isActive: boolean;
  onNavigate?: () => void;
}

export const NavigationLink: FC<Props> = ({ href, icon, label, isActive, onNavigate }) => {
  return (
    <Link
      href={href}
      className={styles.link}
      aria-current={isActive ? "page" : undefined}
      onClick={onNavigate}
    >
      <DSIcon name={icon} />
      {label}
    </Link>
  );
};
