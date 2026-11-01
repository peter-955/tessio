import { MAIN_CONTENT_ID } from "@/components/app-shell/typing/constants/app-shell.constant";
import { DSLogo, DSStack } from "@/components/design-system";
import type { FC } from "react";
import styles from "./layout.module.scss";

const AuthLayout: FC<LayoutProps<"/">> = ({ children }) => {
  return (
    <main id={MAIN_CONTENT_ID} className={styles.main}>
      <DSStack gap={5} align="center" className={styles.content}>
        <DSLogo size={40} hasWordmark />
        {children}
      </DSStack>
    </main>
  );
};

export default AuthLayout;
