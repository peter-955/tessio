import type { UpdateLabelRequest } from "./label.type";

export interface LabelUpdate {
  labelId: string;
  body: UpdateLabelRequest;
}
