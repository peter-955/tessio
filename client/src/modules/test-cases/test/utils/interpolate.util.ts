export const interpolate = (template: string, values: Record<string, string>): string => {
  return Object.entries(values).reduce((text, [name, value]) => {
    return text.replace(`{{${name}}}`, value);
  }, template);
};
