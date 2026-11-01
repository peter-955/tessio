export class ImageCropError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "ImageCropError";
  }
}
