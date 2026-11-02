"use client";

import type { CaseReferences } from "@/components/case-sheet/typing/types/case-sheet.type";
import { buildCaseReferences } from "@/components/case-sheet/utils/case-references.util";
import { useCurrentProject } from "@/components/project-context/hooks/use-current-project";
import { useGetEnvironments } from "@/shared/hooks/queries/use-get-environments";
import type { TestFile } from "../typing/types/test-case.type";
import { buildCaseDataValues, buildTestFileReferences } from "../utils/case-sheet-data.util";
import { useGetEffectiveTestData } from "./queries/use-get-effective-test-data";

const NO_REVEALED_VALUES: Readonly<Record<string, string>> = {};

export const useCaseEditorReferences = (files: readonly TestFile[]): CaseReferences => {
  const project = useCurrentProject();
  const { data: environments = [] } = useGetEnvironments(project.key);
  const environment =
    environments.find((candidate) => candidate.id === project.defaultEnvironmentId) ??
    environments[0];
  const { data: items = [] } = useGetEffectiveTestData(project.key, environment?.id ?? null);

  return buildCaseReferences(
    buildCaseDataValues(items),
    buildTestFileReferences(files),
    NO_REVEALED_VALUES,
    environment?.name ?? null,
  );
};
