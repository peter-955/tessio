import { describe, expect, it } from "vitest";
import { DurationUnit } from "../typing/enums/duration-unit.enum";
import { pickDuration, toDays, toPercent } from "./insight-number.util";

describe("insight numbers", () => {
  it("turns shares into percents with one decimal", () => {
    expect(toPercent(0.8125)).toBe(81.3);
    expect(toPercent(1)).toBe(100);
    expect(toPercent(null)).toBeNull();
  });

  it("turns seconds into days with one decimal", () => {
    expect(toDays(129600)).toBe(1.5);
    expect(toDays(null)).toBeNull();
  });

  it("picks minutes, hours or days for a duration", () => {
    expect(pickDuration(90)).toEqual({ unit: DurationUnit.MINUTE, value: 2 });
    expect(pickDuration(5400)).toEqual({ unit: DurationUnit.HOUR, value: 1.5 });
    expect(pickDuration(172800)).toEqual({ unit: DurationUnit.DAY, value: 2 });
    expect(pickDuration(0)).toEqual({ unit: DurationUnit.MINUTE, value: 0 });
  });
});
