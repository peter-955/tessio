import { describe, expect, it, vi } from "vitest";
import { OBJECT_URL, stubObjectUrl } from "../test/utils/stub-object-url.util";
import { downloadTextFile } from "./download-text-file.util";

describe("downloadTextFile", () => {
  it("downloads the content through a temporary anchor and revokes the URL", async () => {
    const { createObjectURL, revokeObjectURL } = stubObjectUrl();
    const click = vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(() => {
      return;
    });

    downloadTextFile("codes.txt", "aaaaa-bbbbb\nccccc-ddddd");

    const blob = createObjectURL.mock.calls[0]?.[0];
    expect(blob).toBeInstanceOf(Blob);
    expect((blob as Blob).type).toBe("text/plain;charset=utf-8");
    expect(await (blob as Blob).text()).toBe("aaaaa-bbbbb\nccccc-ddddd");
    expect(click).toHaveBeenCalledTimes(1);
    expect((click.mock.contexts[0] as HTMLAnchorElement).download).toBe("codes.txt");
    expect((click.mock.contexts[0] as HTMLAnchorElement).href).toBe(OBJECT_URL);
    expect(revokeObjectURL).toHaveBeenCalledWith(OBJECT_URL);
    expect(document.querySelector("a[download]")).toBeNull();
  });
});
