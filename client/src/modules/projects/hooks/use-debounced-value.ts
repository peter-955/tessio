"use client";

import { useEffect, useState } from "react";

export const useDebouncedValue = <Value>(value: Value, delayInMilliseconds: number): Value => {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const timeout = setTimeout(() => {
      setDebouncedValue(value);
    }, delayInMilliseconds);

    return () => {
      clearTimeout(timeout);
    };
  }, [delayInMilliseconds, value]);

  return debouncedValue;
};
