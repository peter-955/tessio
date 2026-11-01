import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { ImageCropError } from "../image-crop-error";
import { cropImageToSquare } from "./crop-image-to-square.util";

const drawImage = vi.fn<(...drawArguments: unknown[]) => void>();
const closeBitmap = vi.fn<() => void>();

const stubBitmap = (width: number, height: number): void => {
  vi.stubGlobal(
    "createImageBitmap",
    vi.fn(() => {
      return Promise.resolve({ width, height, close: closeBitmap });
    }),
  );
};

interface FakeContext {
  drawImage: typeof drawImage;
}

const stubContext = (context: FakeContext | null): void => {
  vi.spyOn(HTMLCanvasElement.prototype, "getContext").mockReturnValue(
    context as unknown as CanvasRenderingContext2D | null,
  );
};

const stubToBlob = (isEncoded: boolean): ReturnType<typeof vi.spyOn> => {
  return vi.spyOn(HTMLCanvasElement.prototype, "toBlob").mockImplementation((callback, type) => {
    callback(isEncoded ? new Blob(["cropped"], { type }) : null);
  });
};

describe("cropImageToSquare", () => {
  beforeEach(() => {
    drawImage.mockReset();
    closeBitmap.mockReset();
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("draws the centred square of a wide image at 512 px at most", async () => {
    stubBitmap(1200, 800);
    stubContext({ drawImage });
    const toBlob = stubToBlob(true);

    const croppedFile = await cropImageToSquare(
      new File(["source"], "photo.png", { type: "image/png" }),
    );

    expect(drawImage).toHaveBeenCalledWith(expect.anything(), 200, 0, 800, 800, 0, 0, 512, 512);
    expect(toBlob).toHaveBeenCalledWith(expect.any(Function), "image/png", 0.9);
    expect(croppedFile.name).toBe("photo.png");
    expect(croppedFile.type).toBe("image/png");
    expect(closeBitmap).toHaveBeenCalled();
  });

  it("keeps a small tall image at its own size", async () => {
    stubBitmap(200, 300);
    stubContext({ drawImage });
    stubToBlob(true);

    await cropImageToSquare(new File(["source"], "photo.webp", { type: "image/webp" }));

    expect(drawImage).toHaveBeenCalledWith(expect.anything(), 0, 50, 200, 200, 0, 0, 200, 200);
  });

  it("rejects when the canvas has no 2D context", async () => {
    stubBitmap(100, 100);
    stubContext(null);

    await expect(
      cropImageToSquare(new File(["source"], "photo.png", { type: "image/png" })),
    ).rejects.toBeInstanceOf(ImageCropError);
  });

  it("rejects when the image cannot be encoded", async () => {
    stubBitmap(100, 100);
    stubContext({ drawImage });
    stubToBlob(false);

    await expect(
      cropImageToSquare(new File(["source"], "photo.png", { type: "image/png" })),
    ).rejects.toBeInstanceOf(ImageCropError);
  });
});
