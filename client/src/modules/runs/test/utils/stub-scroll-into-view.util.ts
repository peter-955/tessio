export const stubScrollIntoView = (): void => {
  Object.defineProperty(Element.prototype, "scrollIntoView", {
    configurable: true,
    writable: true,
    value: (): void => {
      return;
    },
  });
};
