import type { DSAlertColor, DSAlertStyle } from "./alert.type";

export const DS_ALERT_STYLES: Record<DSAlertColor, DSAlertStyle> = {
  info: { icon: "infoCircle", mantineColor: "tessio", textColor: undefined },
  success: { icon: "circleCheck", mantineColor: "green", textColor: "var(--color-green-text)" },
  warning: { icon: "alert", mantineColor: "yellow", textColor: "var(--color-yellow-text)" },
  danger: { icon: "alertCircle", mantineColor: "red", textColor: "var(--color-red-text)" },
};

export const DS_ALERT_URGENT_COLORS: ReadonlySet<DSAlertColor> = new Set(["warning", "danger"]);
