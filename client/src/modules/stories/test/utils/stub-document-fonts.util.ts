export const stubDocumentFonts = (): void => {
  if ("fonts" in document) {
    return;
  }

  Object.defineProperty(document, "fonts", {
    configurable: true,
    value: {
      ready: Promise.resolve(),
      addEventListener: (): void => {
        return;
      },
      removeEventListener: (): void => {
        return;
      },
    },
  });
};
