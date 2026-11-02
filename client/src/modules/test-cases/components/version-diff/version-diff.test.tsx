import englishTestCases from "@/lib/i18n/locales/en/testCases.json";
import { screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { buildProject } from "../../test/utils/project-fixture.util";
import { renderWithProject } from "../../test/utils/render-with-project.util";
import { buildTestCaseVersion, STORY_CRITERIA } from "../../test/utils/test-case-fixture.util";
import { buildVersionDiff } from "../../utils/version-diff.util";
import { VersionDiff } from "./version-diff";

const { history } = englishTestCases;

describe("VersionDiff", () => {
  it("names a change to only the parameters and data rows instead of saying identical", () => {
    const older = buildTestCaseVersion({ number: 1 });
    const newer = buildTestCaseVersion({
      number: 2,
      parameters: ["email"],
      dataRows: [{ email: "ann" }],
    });

    const { container } = renderWithProject(
      <VersionDiff entries={buildVersionDiff(older, newer, STORY_CRITERIA)} />,
      buildProject(),
    );

    expect(screen.getByText(history.fields.dataTable)).toBeInTheDocument();
    expect(screen.queryByText(history.identical)).toBeNull();
    expect(container.querySelector("ins")).toHaveTextContent(`${history.diffAdded}: email`);
  });
});
