import type { ProjectCapability } from "@/components/project-context/typing/types/project.type";
import { describe, expect, it } from "vitest";
import { canEditDataItemKinds } from "./data-item-capability.util";

const withCapabilities = (
  capabilities: ProjectCapability[],
): { capabilities: ProjectCapability[] } => {
  return { capabilities };
};

describe("canEditDataItemKinds", () => {
  it("needs test_data.edit", () => {
    expect(canEditDataItemKinds(withCapabilities(["test_data.view"]), ["variable"])).toBe(false);
    expect(canEditDataItemKinds(withCapabilities(["test_data.edit"]), ["variable"])).toBe(true);
    expect(canEditDataItemKinds(withCapabilities(["test_data.edit"]), [])).toBe(true);
  });

  it("also needs secret.edit when a kind is secret", () => {
    expect(canEditDataItemKinds(withCapabilities(["test_data.edit"]), ["variable", "secret"])).toBe(
      false,
    );
    expect(
      canEditDataItemKinds(withCapabilities(["test_data.edit", "secret.edit"]), ["secret"]),
    ).toBe(true);
  });

  it("refuses secret.edit alone", () => {
    expect(canEditDataItemKinds(withCapabilities(["secret.edit"]), ["secret"])).toBe(false);
  });
});
