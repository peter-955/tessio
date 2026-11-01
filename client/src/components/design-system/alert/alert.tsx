import { Alert } from "@mantine/core";
import type { FC, ReactNode } from "react";
import { DSIcon } from "../icon/icon";
import { DS_ALERT_STYLES, DS_ALERT_URGENT_COLORS } from "./alert.constant";
import styles from "./alert.module.scss";
import type { DSAlertCloseControl, DSAlertColor } from "./alert.type";

type Props = DSAlertCloseControl & {
  color: DSAlertColor;
  title?: string;
  children: ReactNode;
  action?: ReactNode;
};

export const DSAlert: FC<Props> = ({ color, title, children, action, onClose, closeLabel }) => {
  const { icon, mantineColor, textColor } = DS_ALERT_STYLES[color];

  return (
    <Alert
      variant="light"
      radius="md"
      color={mantineColor}
      title={title}
      icon={<DSIcon name={icon} size={20} />}
      role={DS_ALERT_URGENT_COLORS.has(color) ? "alert" : "status"}
      withCloseButton={onClose !== undefined}
      closeButtonLabel={closeLabel}
      onClose={onClose}
      classNames={{ message: styles.message }}
      styles={{ title: { color: textColor }, icon: { color: textColor } }}
    >
      {children}
      {action && <div className={styles.action}>{action}</div>}
    </Alert>
  );
};
