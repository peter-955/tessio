import { describe, expect, it } from "vitest";
import { buildJunitImportCommand } from "./junit-import-command.util";

describe("buildJunitImportCommand", () => {
  it("builds a curl call that uploads a JUnit file with the token", () => {
    expect(
      buildJunitImportCommand({
        tessioUrl: "https://tessio.example.com",
        projectKey: "TES",
        token: "tsio_a1b2c3d4_S3cret",
      }),
    ).toBe(
      [
        "curl -X POST https://tessio.example.com/api/projects/TES/runs/import \\",
        "  -H 'Authorization: Bearer tsio_a1b2c3d4_S3cret' \\",
        "  -F file=@results.xml \\",
        "  -F environment=Staging",
      ].join("\n"),
    );
  });

  it("quotes a token that holds shell characters", () => {
    expect(
      buildJunitImportCommand({
        tessioUrl: "https://tessio.example.com",
        projectKey: "TES",
        token: "tsio_x'y",
      }),
    ).toContain("-H 'Authorization: Bearer tsio_x'\\''y'");
  });
});
