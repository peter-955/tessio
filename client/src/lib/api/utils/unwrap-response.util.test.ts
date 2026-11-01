import { describe, expect, it } from "vitest";
import { ApiError } from "../api-error";
import { unwrapResponse } from "./unwrap-response.util";

describe("unwrapResponse", () => {
  it("returns the data of a successful response", async () => {
    const data = await unwrapResponse(
      Promise.resolve({ data: { name: "Ada" }, response: new Response(null, { status: 200 }) }),
    );

    expect(data).toEqual({ name: "Ada" });
  });

  it("returns undefined for a no-content response", async () => {
    const data = await unwrapResponse<undefined>(
      Promise.resolve({ data: undefined, response: new Response(null, { status: 204 }) }),
    );

    expect(data).toBeUndefined();
  });

  it("throws an ApiError for a failed response", async () => {
    const request = unwrapResponse<{ name: string }>(
      Promise.resolve({
        error: { code: "PERMISSION_DENIED", message: "Permission denied." },
        response: new Response(null, { status: 403 }),
      }),
    );

    await expect(request).rejects.toBeInstanceOf(ApiError);
    await expect(request).rejects.toMatchObject({ status: 403, code: "PERMISSION_DENIED" });
  });
});
