import { describe, expect, it } from "vitest";
import { buildPluginInstallCommand, quoteShellArgument } from "./plugin-install-command.util";

describe("quoteShellArgument", () => {
  it("leaves plain values unquoted", () => {
    expect(quoteShellArgument("https://tessio.example.com:8443/path")).toBe(
      "https://tessio.example.com:8443/path",
    );
    expect(quoteShellArgument("tsio_a1b2c3d4_Secret-Value+1=")).toBe(
      "tsio_a1b2c3d4_Secret-Value+1=",
    );
  });

  it("quotes a value with a space", () => {
    expect(quoteShellArgument("my value")).toBe("'my value'");
  });

  it("escapes a single quote inside the quotes", () => {
    expect(quoteShellArgument("it's")).toBe("'it'\\''s'");
  });

  it("quotes an empty value", () => {
    expect(quoteShellArgument("")).toBe("''");
  });
});

describe("buildPluginInstallCommand", () => {
  it("installs from the marketplace this Tessio serves", () => {
    expect(
      buildPluginInstallCommand({
        tessioUrl: "https://tessio.example.com",
        token: "tsio_a1b2c3d4_secret",
      }),
    ).toBe(
      "claude plugin install tessio --marketplace https://tessio.example.com/api/plugin/marketplace.json --config tessio_url=https://tessio.example.com --config tessio_token=tsio_a1b2c3d4_secret",
    );
  });

  it("quotes values that need it", () => {
    expect(
      buildPluginInstallCommand({
        tessioUrl: "https://tessio.example.com/team a",
        token: "tsio_x'y",
      }),
    ).toBe(
      "claude plugin install tessio --marketplace 'https://tessio.example.com/team a/api/plugin/marketplace.json' --config tessio_url='https://tessio.example.com/team a' --config tessio_token='tsio_x'\\''y'",
    );
  });
});
