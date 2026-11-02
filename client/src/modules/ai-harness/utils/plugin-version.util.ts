import { PLUGIN_VERSION_PATTERN } from "../typing/constants/plugin-version.constant";
import type { PluginState } from "../typing/types/plugin-state.type";

export const parsePluginVersion = (version: string): number[] | null => {
  const match = PLUGIN_VERSION_PATTERN.exec(version.trim());
  if (match === null) {
    return null;
  }

  return match.slice(1).map(Number);
};

export const checkIsVersionAtLeast = (sentVersion: string, requiredVersion: string): boolean => {
  const sent = parsePluginVersion(sentVersion);
  const required = parsePluginVersion(requiredVersion);
  if (sent === null || required === null) {
    return false;
  }

  const differentIndex = sent.findIndex((part, index) => {
    return part !== required[index];
  });

  return differentIndex === -1 || sent[differentIndex] > required[differentIndex];
};

export const resolvePluginState = (
  sentVersion: string | null,
  requiredVersion: string,
): PluginState => {
  if (sentVersion === null) {
    return "unused";
  }

  return checkIsVersionAtLeast(sentVersion, requiredVersion) ? "current" : "outdated";
};
