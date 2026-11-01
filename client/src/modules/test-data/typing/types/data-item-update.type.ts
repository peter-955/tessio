import type { UpdateDataItemRequest } from "./data-item.type";

export interface DataItemUpdate {
  itemId: string;
  body: UpdateDataItemRequest;
}
