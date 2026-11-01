import "i18next";
import type { LocaleResources } from "./typing/types/locale.type";

declare module "i18next" {
  interface CustomTypeOptions {
    defaultNS: "common";
    resources: LocaleResources;
  }
}
