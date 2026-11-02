"use client";

import { useCurrentProject } from "@/components/project-context/hooks/use-current-project";
import { SharedStepReference } from "@/modules/shared-steps/components/shared-step-reference/shared-step-reference";
import type { FC } from "react";
import { useCaseEditorReferences } from "../../hooks/use-case-editor-references";
import type { TestFile } from "../../typing/types/test-case.type";

interface Props {
  sharedStepKey: string;
  files: readonly TestFile[];
}

export const CaseEditorSharedStep: FC<Props> = ({ sharedStepKey, files }) => {
  const project = useCurrentProject();
  const references = useCaseEditorReferences(files);

  return (
    <SharedStepReference
      projectKey={project.key}
      sharedStepKey={sharedStepKey}
      references={references}
    />
  );
};
