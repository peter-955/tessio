import { act, renderHook } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { isNotEmpty } from "./form-validators.util";
import { useDSForm, type DSForm } from "./use-ds-form";

interface ProjectValues {
  name: string;
}

describe("useDSForm", () => {
  it("validates with the re-exported validators and accepts server-side field errors", () => {
    const { result } = renderHook((): DSForm<ProjectValues> => {
      return useDSForm<ProjectValues>({
        mode: "controlled",
        initialValues: { name: "" },
        validate: { name: isNotEmpty("Name is required") },
      });
    });

    act(() => {
      result.current.validate();
    });

    expect(result.current.errors.name).toBe("Name is required");

    act(() => {
      result.current.setFieldValue("name", "Checkout");
    });
    act(() => {
      result.current.setFieldError("name", "Name already used");
    });

    expect(result.current.values.name).toBe("Checkout");
    expect(result.current.errors.name).toBe("Name already used");
  });
});
