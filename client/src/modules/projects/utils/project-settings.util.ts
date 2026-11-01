import type { Project } from "@/components/project-context/typing/types/project.type";
import type { AllowedFileTypesValues } from "../typing/types/allowed-file-types-values.type";
import type { DefaultEnvironmentValues } from "../typing/types/default-environment-values.type";
import type { GeneralSettingsValues } from "../typing/types/general-settings-values.type";

export const buildGeneralSettingsValues = (project: Project): GeneralSettingsValues => {
  return {
    name: project.name,
    description: project.description ?? "",
    jiraBoardId: String(project.jiraBoardId),
  };
};

export const buildDefaultEnvironmentValues = (project: Project): DefaultEnvironmentValues => {
  return { defaultEnvironmentId: project.defaultEnvironmentId ?? null };
};

export const buildAllowedFileTypesValues = (project: Project): AllowedFileTypesValues => {
  return { allowedFileTypes: [...project.allowedFileTypes] };
};
