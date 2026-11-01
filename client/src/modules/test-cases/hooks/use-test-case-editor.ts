"use client";

import { useState } from "react";
import type { TestCaseFormValues } from "../typing/types/test-case-form-values.type";
import type {
  TestCaseDetail,
  TestCaseVersion,
  UpdateTestCaseRequest,
} from "../typing/types/test-case.type";
import {
  buildTestCaseFormValues,
  buildUpdateTestCaseRequest,
  checkHasTestCaseChanges,
} from "../utils/test-case-form.util";

interface Result {
  values: TestCaseFormValues;
  baseVersion: TestCaseVersion;
  updateRequest: UpdateTestCaseRequest;
  isDirty: boolean;
  changeValues: (values: TestCaseFormValues) => void;
  markSaved: (detail: TestCaseDetail) => void;
  resetTo: (detail: TestCaseDetail) => void;
}

export const useTestCaseEditor = (detail: TestCaseDetail): Result => {
  const [values, setValues] = useState(() => {
    return buildTestCaseFormValues(detail.currentVersion, detail.story.jiraKey);
  });
  const [baseVersion, setBaseVersion] = useState(detail.currentVersion);
  const updateRequest = buildUpdateTestCaseRequest(values, baseVersion);
  const isDirty = checkHasTestCaseChanges(updateRequest);

  if (detail.currentVersion.id !== baseVersion.id && !isDirty) {
    setBaseVersion(detail.currentVersion);
    setValues(buildTestCaseFormValues(detail.currentVersion, detail.story.jiraKey));
  }

  return {
    values,
    baseVersion,
    updateRequest,
    isDirty,
    changeValues: setValues,
    markSaved: (savedDetail) => {
      setBaseVersion(savedDetail.currentVersion);
    },
    resetTo: (latestDetail) => {
      setBaseVersion(latestDetail.currentVersion);
      setValues(buildTestCaseFormValues(latestDetail.currentVersion, latestDetail.story.jiraKey));
    },
  };
};
