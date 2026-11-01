import { ImageCropError } from "../image-crop-error";
import {
  AVATAR_OUTPUT_QUALITY,
  AVATAR_OUTPUT_SIZE_IN_PIXELS,
} from "../typing/constants/profile.constant";

const HALF = 2;

const canvasToBlob = (canvas: HTMLCanvasElement, type: string): Promise<Blob | null> => {
  return new Promise((resolve) => {
    canvas.toBlob(resolve, type, AVATAR_OUTPUT_QUALITY);
  });
};

export const cropImageToSquare = async (file: File): Promise<File> => {
  const bitmap = await createImageBitmap(file);
  const side = Math.min(bitmap.width, bitmap.height);
  const outputSize = Math.min(side, AVATAR_OUTPUT_SIZE_IN_PIXELS);
  const canvas = document.createElement("canvas");
  canvas.width = outputSize;
  canvas.height = outputSize;

  const context = canvas.getContext("2d");
  if (context === null) {
    bitmap.close();
    throw new ImageCropError("The canvas has no 2D context.");
  }

  context.drawImage(
    bitmap,
    (bitmap.width - side) / HALF,
    (bitmap.height - side) / HALF,
    side,
    side,
    0,
    0,
    outputSize,
    outputSize,
  );
  bitmap.close();

  const blob = await canvasToBlob(canvas, file.type);
  if (blob === null) {
    throw new ImageCropError("The cropped image could not be encoded.");
  }

  return new File([blob], file.name, { type: file.type });
};
