import type { DSSelectOption } from "@/components/design-system";
import { Language } from "@/shared/typing/enums/language.enum";

export const PROFILE_PATH = "/profile";

export const AVATAR_OUTPUT_SIZE_IN_PIXELS = 512;

export const AVATAR_OUTPUT_QUALITY = 0.9;

export const MAX_USER_NAME_LENGTH = 100;

export const LANGUAGE_NAME_OPTIONS: DSSelectOption<Language>[] = [
  { value: Language.ENGLISH, label: "English" },
  { value: Language.FRENCH, label: "Français" },
  { value: Language.VIETNAMESE, label: "Tiếng Việt" },
];
