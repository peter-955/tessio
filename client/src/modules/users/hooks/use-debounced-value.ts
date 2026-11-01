"use client";

import { useEffect, useState } from "react";

export const useDebouncedValue = <T>(value: T, delayMilliseconds: number): T => {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const timeoutId = setTimeout(() => {
      setDebouncedValue(value);
    }, delayMilliseconds);

    return (): void => {
      clearTimeout(timeoutId);
    };
  }, [value, delayMilliseconds]);

  return debouncedValue;
};
