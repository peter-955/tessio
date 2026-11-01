import type { KnownFileType } from "../types/known-file-type.type";

export const MIME_TYPE_PATTERN = /^[a-z]+\/[a-z0-9.+-]+$/;

export const MIME_TYPE_MAX_LENGTH = 255;

export const MAX_ALLOWED_FILE_TYPES = 50;

const WORD_DOCUMENT_MIME_TYPE =
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document";

const EXCEL_SHEET_MIME_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet";

export const DEFAULT_ALLOWED_FILE_TYPES: string[] = [
  "image/png",
  "image/jpeg",
  "image/webp",
  "image/gif",
  "application/pdf",
  "text/plain",
  "text/csv",
  "application/json",
  WORD_DOCUMENT_MIME_TYPE,
  EXCEL_SHEET_MIME_TYPE,
];

export const KNOWN_FILE_TYPES: KnownFileType[] = [
  { mimeType: "image/png", formatLabel: "PNG" },
  { mimeType: "image/jpeg", formatLabel: "JPEG" },
  { mimeType: "image/webp", formatLabel: "WebP" },
  { mimeType: "image/gif", formatLabel: "GIF" },
  { mimeType: "application/pdf", formatLabel: "PDF" },
  { mimeType: "text/plain", formatLabel: "TXT" },
  { mimeType: "text/csv", formatLabel: "CSV" },
  { mimeType: "application/json", formatLabel: "JSON" },
  { mimeType: WORD_DOCUMENT_MIME_TYPE, formatLabel: "DOCX" },
  { mimeType: EXCEL_SHEET_MIME_TYPE, formatLabel: "XLSX" },
  { mimeType: "text/markdown", formatLabel: "Markdown" },
  { mimeType: "application/zip", formatLabel: "ZIP" },
  { mimeType: "application/yaml", formatLabel: "YAML" },
  { mimeType: "application/xml", formatLabel: "XML" },
  { mimeType: "text/html", formatLabel: "HTML" },
  { mimeType: "video/mp4", formatLabel: "MP4" },
];
