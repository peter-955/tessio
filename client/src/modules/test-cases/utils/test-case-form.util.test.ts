import { describe, expect, it } from "vitest";
import {
  FIRST_CRITERION_ID,
  SECOND_CRITERION_ID,
  buildTestCaseVersion,
} from "../test/utils/test-case-fixture.util";
import type { TestCaseFormValues } from "../typing/types/test-case-form-values.type";
import {
  buildCreateTestCaseRequest,
  buildTestCaseFormValues,
  buildUpdateTestCaseRequest,
  checkHasTestCaseChanges,
  checkHasTestCaseFormErrors,
  createEmptyTestCaseFormValues,
  validateTestCaseForm,
} from "./test-case-form.util";

const VERSION = buildTestCaseVersion();

const buildValues = (overrides: Partial<TestCaseFormValues> = {}): TestCaseFormValues => {
  return { ...buildTestCaseFormValues(VERSION, "SHOP-1"), ...overrides };
};

describe("buildUpdateTestCaseRequest", () => {
  it("sends only the base version when nothing changed", () => {
    const request = buildUpdateTestCaseRequest(buildValues(), VERSION);

    expect(request).toEqual({ baseVersionNumber: 2 });
    expect(checkHasTestCaseChanges(request)).toBe(false);
  });

  it("ignores whitespace and criterion order", () => {
    const values = buildValues({
      title: "  Pay with a valid card ",
      businessValue: "Customers can pay\n",
    });

    expect(checkHasTestCaseChanges(buildUpdateTestCaseRequest(values, VERSION))).toBe(false);
  });

  it("sends the changed fields with the base version number", () => {
    const values = buildValues({
      title: "Pay with a saved card",
      priority: "critical",
      preconditions: "Signed in",
      criterionIds: [SECOND_CRITERION_ID, FIRST_CRITERION_ID],
    });

    expect(buildUpdateTestCaseRequest(values, VERSION)).toEqual({
      baseVersionNumber: 2,
      title: "Pay with a saved card",
      priority: "critical",
      preconditions: "Signed in",
      criterionIds: [SECOND_CRITERION_ID, FIRST_CRITERION_ID],
    });
  });

  it("sends all steps when one changes and an empty text to clear a field", () => {
    const values = buildValues({ businessValue: "  " });
    const [firstStep, secondStep] = values.steps;
    if (firstStep === undefined || secondStep === undefined) {
      throw new Error("The fixture has two steps.");
    }

    expect(
      buildUpdateTestCaseRequest(
        { ...values, steps: [firstStep, { ...secondStep, expected: "Paid" }] },
        VERSION,
      ),
    ).toEqual({
      baseVersionNumber: 2,
      businessValue: "",
      steps: [
        { action: "Open the cart", expected: null },
        { action: "Pay as {{data.username}}", expected: "Paid" },
      ],
    });
  });
});

describe("buildCreateTestCaseRequest", () => {
  it("trims the text and turns blank optional fields into null", () => {
    const values: TestCaseFormValues = {
      ...createEmptyTestCaseFormValues("SHOP-1"),
      title: " Refund ",
      steps: [{ id: "step", action: " Refund the order ", expected: " " }],
      criterionIds: [FIRST_CRITERION_ID],
    };

    expect(buildCreateTestCaseRequest(values, "SHOP-1")).toEqual({
      storyKey: "SHOP-1",
      title: "Refund",
      priority: "medium",
      businessValue: null,
      preconditions: null,
      steps: [{ action: "Refund the order", expected: null }],
      criterionIds: [FIRST_CRITERION_ID],
    });
  });
});

describe("validateTestCaseForm", () => {
  it("requires a story, a title and an action on every step", () => {
    const errors = validateTestCaseForm({
      ...createEmptyTestCaseFormValues(null),
      steps: [{ id: "empty", action: " ", expected: "" }],
    });

    expect(errors).toMatchObject({
      storyKey: "required",
      title: "required",
      stepActions: { empty: "required" },
    });
    expect(checkHasTestCaseFormErrors(errors)).toBe(true);
  });

  it("limits the text lengths", () => {
    const errors = validateTestCaseForm(
      buildValues({ title: "a".repeat(201), preconditions: "b".repeat(5001) }),
    );

    expect(errors.title).toBe("tooLong");
    expect(errors.preconditions).toBe("tooLong");
  });

  it("accepts a valid case", () => {
    expect(checkHasTestCaseFormErrors(validateTestCaseForm(buildValues()))).toBe(false);
  });
});

describe("shared steps and data rows", () => {
  const DATA_VERSION = buildTestCaseVersion({
    steps: [
      { order: 1, action: "Open {{param.page}}", expected: null, sharedStepKey: null },
      { order: 2, action: null, expected: null, sharedStepKey: "login_as_admin" },
    ],
    parameters: ["page"],
    dataRows: [{ page: "/cart" }],
  });

  it("keeps a shared step as a reference and sends nothing when unchanged", () => {
    const values = buildTestCaseFormValues(DATA_VERSION, "SHOP-1");

    expect(values.steps[1]?.sharedStepKey).toBe("login_as_admin");
    expect(buildUpdateTestCaseRequest(values, DATA_VERSION)).toEqual({ baseVersionNumber: 2 });
    expect(checkHasTestCaseFormErrors(validateTestCaseForm(values))).toBe(false);
  });

  it("sends the parameters with the rows when a row changes", () => {
    const values = buildTestCaseFormValues(DATA_VERSION, "SHOP-1");
    const [row] = values.dataTable.rows;
    const [parameter] = values.dataTable.parameters;
    if (row === undefined || parameter === undefined) {
      throw new Error("The fixture has a row and a parameter.");
    }

    const changed: TestCaseFormValues = {
      ...values,
      dataTable: {
        ...values.dataTable,
        rows: [{ ...row, values: { [parameter.id]: "/orders" } }],
      },
    };

    expect(buildUpdateTestCaseRequest(changed, DATA_VERSION)).toEqual({
      baseVersionNumber: 2,
      parameters: ["page"],
      dataRows: [{ page: "/orders" }],
    });
  });

  it("sends every step when a shared step is removed", () => {
    const values = buildTestCaseFormValues(DATA_VERSION, "SHOP-1");

    expect(
      buildUpdateTestCaseRequest({ ...values, steps: values.steps.slice(0, 1) }, DATA_VERSION),
    ).toEqual({
      baseVersionNumber: 2,
      steps: [{ action: "Open {{param.page}}", expected: null }],
    });
  });
});
