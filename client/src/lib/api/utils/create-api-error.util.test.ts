import { describe, expect, it } from "vitest";
import { ApiError } from "../api-error";
import { createApiError } from "./create-api-error.util";

const createResponse = (status: number, statusText = ""): Response => {
  return new Response(null, { status, statusText });
};

describe("createApiError", () => {
  it("uses the code and message of a Tessio error body", () => {
    const error = createApiError(createResponse(409), {
      code: "EMAIL_ALREADY_USED",
      message: "Email already used.",
    });

    expect(error).toBeInstanceOf(ApiError);
    expect(error.name).toBe("ApiError");
    expect(error.status).toBe(409);
    expect(error.code).toBe("EMAIL_ALREADY_USED");
    expect(error.message).toBe("Email already used.");
    expect(error.fieldErrors).toEqual({});
  });

  it("maps a validation body to INVALID_REQUEST with field errors", () => {
    const error = createApiError(createResponse(422), {
      detail: [
        { loc: ["body", "email"], msg: "Field required", type: "missing" },
        { loc: ["body", "password"], msg: "String too short", type: "string_too_short" },
        { loc: ["query", 0], msg: "Invalid index", type: "int_parsing" },
      ],
    });

    expect(error.status).toBe(422);
    expect(error.code).toBe("INVALID_REQUEST");
    expect(error.message).toBe("Field required");
    expect(error.fieldErrors).toEqual({
      email: "Field required",
      password: "String too short",
      "0": "Invalid index",
    });
  });

  it("falls back to the status text for an HTML body", () => {
    const error = createApiError(createResponse(502, "Bad Gateway"), "<html>Bad gateway</html>");

    expect(error.status).toBe(502);
    expect(error.code).toBeNull();
    expect(error.message).toBe("Bad Gateway");
  });

  it("falls back to the status for an empty body", () => {
    const error = createApiError(createResponse(500), undefined);

    expect(error.code).toBeNull();
    expect(error.message).toBe("500");
    expect(error.fieldErrors).toEqual({});
  });

  it("ignores a string detail body", () => {
    const error = createApiError(createResponse(404, "Not Found"), { detail: "Not Found" });

    expect(error.code).toBeNull();
    expect(error.message).toBe("Not Found");
  });
});
