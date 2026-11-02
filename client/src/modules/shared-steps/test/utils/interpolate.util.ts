export const interpolate = (template: string, values: Record<string, string | number>): string => {
  return Object.entries(values).reduce((text, [name, value]) => {
    return text.replace(`{{${name}}}`, String(value));
  }, template);
};
