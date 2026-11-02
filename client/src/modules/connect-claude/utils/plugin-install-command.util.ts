import {
  PLUGIN_MARKETPLACE_PATH,
  PLUGIN_NAME,
  PLUGIN_TOKEN_CONFIG_KEY,
  PLUGIN_URL_CONFIG_KEY,
} from "../typing/constants/plugin.constant";
import type { PluginInstallCommandOptions } from "../typing/types/plugin-install-command-options.type";

const SAFE_SHELL_ARGUMENT = /^[A-Za-z0-9_./:@=+-]+$/;

export const quoteShellArgument = (value: string): string => {
  if (SAFE_SHELL_ARGUMENT.test(value)) {
    return value;
  }

  return `'${value.replaceAll("'", "'\\''")}'`;
};

export const buildPluginInstallCommand = ({
  tessioUrl,
  token,
}: PluginInstallCommandOptions): string => {
  const marketplaceArgument = quoteShellArgument(`${tessioUrl}${PLUGIN_MARKETPLACE_PATH}`);

  return [
    "claude plugin install",
    PLUGIN_NAME,
    "--marketplace",
    marketplaceArgument,
    "--config",
    `${PLUGIN_URL_CONFIG_KEY}=${quoteShellArgument(tessioUrl)}`,
    "--config",
    `${PLUGIN_TOKEN_CONFIG_KEY}=${quoteShellArgument(token)}`,
  ].join(" ");
};
