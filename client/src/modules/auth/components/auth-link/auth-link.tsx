import Link from "next/link";
import type { FC, ReactNode } from "react";
import styles from "./auth-link.module.scss";

interface Props {
  href: string;
  children: ReactNode;
}

export const AuthLink: FC<Props> = ({ href, children }) => {
  return (
    <Link href={href} className={styles.link}>
      {children}
    </Link>
  );
};
