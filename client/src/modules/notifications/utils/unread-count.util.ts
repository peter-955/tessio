import { MAX_DISPLAYED_UNREAD_COUNT } from "../typing/constants/notification.constant";

export const formatUnreadCount = (count: number): string => {
  return count > MAX_DISPLAYED_UNREAD_COUNT ? `${MAX_DISPLAYED_UNREAD_COUNT}+` : String(count);
};
