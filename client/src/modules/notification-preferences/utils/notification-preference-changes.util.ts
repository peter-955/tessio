import type { NotificationPreferenceChannel } from "../typing/types/notification-preference-channel.type";
import type {
  NotificationPreference,
  NotificationPreferenceChange,
  NotificationPreferenceKind,
} from "../typing/types/notification-preference.type";

export const setNotificationPreference = (
  preferences: readonly NotificationPreference[],
  kind: NotificationPreferenceKind,
  channel: NotificationPreferenceChannel,
  isOn: boolean,
): NotificationPreference[] => {
  return preferences.map((preference) => {
    return preference.kind === kind ? { ...preference, [channel]: isOn } : preference;
  });
};

export const buildNotificationPreferenceChanges = (
  saved: readonly NotificationPreference[],
  draft: readonly NotificationPreference[],
): NotificationPreferenceChange[] => {
  return draft.flatMap((preference): NotificationPreferenceChange[] => {
    const savedPreference = saved.find((candidate) => candidate.kind === preference.kind);
    const isInAppChanged = savedPreference?.inApp !== preference.inApp;
    const isEmailChanged = savedPreference?.email !== preference.email;

    if (!isInAppChanged && !isEmailChanged) {
      return [];
    }

    return [
      {
        kind: preference.kind,
        ...(isInAppChanged ? { inApp: preference.inApp } : {}),
        ...(isEmailChanged ? { email: preference.email } : {}),
      },
    ];
  });
};
