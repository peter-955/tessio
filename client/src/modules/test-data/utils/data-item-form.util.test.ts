import { describe, expect, it } from "vitest";
import { buildDataItem, STAGING_ENVIRONMENT_ID } from "../test/utils/test-data-fixture.util";
import { PROJECT_SCOPE_ID } from "../typing/constants/test-data.constant";
import {
  buildCreateDataItemRequest,
  buildDataItemFormValues,
  buildUpdateDataItemRequest,
  isKeepingSecretValue,
} from "./data-item-form.util";

const secretItem = buildDataItem({
  key: "PASSWORD",
  kind: "secret",
  value: null,
  environmentId: STAGING_ENVIRONMENT_ID,
});

describe("buildDataItemFormValues", () => {
  it("starts a blank project variable", () => {
    expect(buildDataItemFormValues({ mode: "create", preset: null })).toEqual({
      key: "",
      kind: "variable",
      scopeId: PROJECT_SCOPE_ID,
      value: "",
    });
  });

  it("uses the preset of a cell", () => {
    expect(
      buildDataItemFormValues({
        mode: "create",
        preset: { key: "API_URL", kind: "endpoint", scopeId: STAGING_ENVIRONMENT_ID },
      }),
    ).toEqual({ key: "API_URL", kind: "endpoint", scopeId: STAGING_ENVIRONMENT_ID, value: "" });
  });

  it("prefills a variable but never a secret", () => {
    expect(buildDataItemFormValues({ mode: "edit", item: buildDataItem() }).value).toBe("/shop");
    expect(buildDataItemFormValues({ mode: "edit", item: secretItem })).toEqual({
      key: "PASSWORD",
      kind: "secret",
      scopeId: STAGING_ENVIRONMENT_ID,
      value: "",
    });
  });
});

describe("buildCreateDataItemRequest", () => {
  it("sends a null environment for the project scope", () => {
    expect(
      buildCreateDataItemRequest({
        key: " BASE ",
        kind: "variable",
        scopeId: PROJECT_SCOPE_ID,
        value: " /a ",
      }),
    ).toEqual({ key: "BASE", kind: "variable", value: " /a ", environmentId: null });
  });

  it("sends the environment id for an environment scope", () => {
    expect(
      buildCreateDataItemRequest({
        key: "BASE",
        kind: "variable",
        scopeId: STAGING_ENVIRONMENT_ID,
        value: "/a",
      }).environmentId,
    ).toBe(STAGING_ENVIRONMENT_ID);
  });
});

describe("buildUpdateDataItemRequest", () => {
  it("keeps a secret value when it stays secret and the field is empty", () => {
    expect(
      buildUpdateDataItemRequest(
        { key: "PASSWORD", kind: "secret", scopeId: STAGING_ENVIRONMENT_ID, value: "" },
        secretItem,
      ),
    ).toEqual({ key: "PASSWORD", kind: "secret", value: null });
  });

  it("sends the new value otherwise", () => {
    expect(
      buildUpdateDataItemRequest(
        { key: "PASSWORD", kind: "variable", scopeId: STAGING_ENVIRONMENT_ID, value: "plain" },
        secretItem,
      ).value,
    ).toBe("plain");
  });
});

describe("isKeepingSecretValue", () => {
  it("is true only for a secret that stays secret", () => {
    expect(isKeepingSecretValue(secretItem, "secret")).toBe(true);
    expect(isKeepingSecretValue(secretItem, "variable")).toBe(false);
    expect(isKeepingSecretValue(buildDataItem(), "secret")).toBe(false);
    expect(isKeepingSecretValue(null, "secret")).toBe(false);
  });
});
