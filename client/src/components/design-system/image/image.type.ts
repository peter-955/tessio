export type DSImageFit = "cover" | "contain";

export type DSImageZoomControl =
  { isZoomable: true; closeLabel: string } | { isZoomable?: false; closeLabel?: never };
