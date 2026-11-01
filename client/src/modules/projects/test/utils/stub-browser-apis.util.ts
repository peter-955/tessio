const ignoreBrowserCall = (): void => {
  return;
};

export const stubBrowserApis = (): void => {
  if (!("fonts" in document) || document.fonts === undefined) {
    Object.defineProperty(document, "fonts", {
      configurable: true,
      value: { addEventListener: ignoreBrowserCall, removeEventListener: ignoreBrowserCall },
    });
  }

  if (typeof Element.prototype.scrollIntoView !== "function") {
    Element.prototype.scrollIntoView = ignoreBrowserCall;
  }
};
