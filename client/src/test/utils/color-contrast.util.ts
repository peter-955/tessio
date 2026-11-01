const HEX_PATTERN = /^#([0-9a-f]{3}|[0-9a-f]{6})$/i;

const LINEAR_THRESHOLD = 0.04045;

const parseHexColor = (hex: string): [number, number, number] => {
  const match = HEX_PATTERN.exec(hex.trim());
  if (match === null) {
    throw new Error(`Not a hex colour: ${hex}`);
  }
  const digits = match[1];
  const fullDigits =
    digits.length === 3
      ? digits
          .split("")
          .map((digit) => `${digit}${digit}`)
          .join("")
      : digits;

  return [
    Number.parseInt(fullDigits.slice(0, 2), 16),
    Number.parseInt(fullDigits.slice(2, 4), 16),
    Number.parseInt(fullDigits.slice(4, 6), 16),
  ];
};

const toLinearChannel = (channel: number): number => {
  const normalized = channel / 255;

  return normalized <= LINEAR_THRESHOLD
    ? normalized / 12.92
    : ((normalized + 0.055) / 1.055) ** 2.4;
};

const toHexChannel = (channel: number): string => {
  const clamped = Math.min(255, Math.max(0, Math.round(channel)));

  return clamped.toString(16).padStart(2, "0");
};

export const toHex = (red: number, green: number, blue: number): string => {
  return `#${toHexChannel(red)}${toHexChannel(green)}${toHexChannel(blue)}`;
};

export const getRelativeLuminance = (hex: string): number => {
  const [red, green, blue] = parseHexColor(hex).map(toLinearChannel);

  return 0.2126 * red + 0.7152 * green + 0.0722 * blue;
};

export const getContrastRatio = (foreground: string, background: string): number => {
  const foregroundLuminance = getRelativeLuminance(foreground);
  const backgroundLuminance = getRelativeLuminance(background);
  const lighter = Math.max(foregroundLuminance, backgroundLuminance);
  const darker = Math.min(foregroundLuminance, backgroundLuminance);

  return (lighter + 0.05) / (darker + 0.05);
};

export const mixHexColors = (first: string, second: string, firstWeight: number): string => {
  if (firstWeight < 0 || firstWeight > 1) {
    throw new Error(`The first weight must be between 0 and 1, got ${firstWeight}`);
  }
  const firstChannels = parseHexColor(first);
  const secondChannels = parseHexColor(second);
  const [red, green, blue] = firstChannels.map((channel, index) => {
    return channel * firstWeight + secondChannels[index] * (1 - firstWeight);
  });

  return toHex(red, green, blue);
};
