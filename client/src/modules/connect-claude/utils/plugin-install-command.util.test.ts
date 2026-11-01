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
  it("builds the one-step install command", () => {
    expect(
      buildPluginInstallCommand({
        marketplace: "acme/tessio",
        tessioUrl: "https://tessio.example.com",
        token: "tsio_a1b2c3d4_secret",
      }),
    ).toBe(
      "claude plugin install tessio --marketplace acme/tessio --config tessio_url=https://tessio.example.com --config tessio_token=tsio_a1b2c3d4_secret",
    );
  });

  it("quotes values that need it", () => {
    expect(
      buildPluginInstallCommand({
        marketplace: "git@host:team/tessio repo.git",
        tessioUrl: "https://tessio.example.com",
        token: "tsio_x'y",
      }),
    ).toBe(
      "claude plugin install tessio --marketplace 'git@host:team/tessio repo.git' --config tessio_url=https://tessio.example.com --config tessio_token='tsio_x'\\''y'",
    );
  });

  it("shows the placeholder when the marketplace is not configured", () => {
    expect(
      buildPluginInstallCommand({
        marketplace: "",
        tessioUrl: "http://localhost:3201",
        token: "tsio_a1b2c3d4_secret",
      }),
    ).toBe(
      "claude plugin install tessio --marketplace <marketplace> --config tessio_url=http://localhost:3201 --config tessio_token=tsio_a1b2c3d4_secret",
    );
  });
});
