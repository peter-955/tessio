import { Skeleton } from "@mantine/core";
import type { FC } from "react";
import { DSStack } from "../stack/stack";
import { DS_SKELETON_LAST_LINE_WIDTH, DS_SKELETON_LINE_HEIGHT } from "./skeleton.constant";
import type { DSSkeletonRadius } from "./skeleton.type";

interface Props {
  height?: number | string;
  width?: number | string;
  isCircle?: boolean;
  radius?: DSSkeletonRadius;
  lineCount?: number;
}

export const DSSkeleton: FC<Props> = ({
  height,
  width,
  isCircle = false,
  radius = "sm",
  lineCount,
}) => {
  if (lineCount === undefined) {
    return (
      <Skeleton
        height={height ?? DS_SKELETON_LINE_HEIGHT}
        width={isCircle ? (height ?? DS_SKELETON_LINE_HEIGHT) : width}
        circle={isCircle}
        radius={radius}
        aria-hidden
      />
    );
  }

  const lineIndexes = [...Array(lineCount).keys()];

  return (
    <div aria-hidden>
      <DSStack gap={2}>
        {lineIndexes.map((lineIndex) => {
          const isLastLine = lineCount > 1 && lineIndex === lineCount - 1;
          return (
            <Skeleton
              key={lineIndex}
              height={height ?? DS_SKELETON_LINE_HEIGHT}
              width={isLastLine ? DS_SKELETON_LAST_LINE_WIDTH : width}
              radius={radius}
            />
          );
        })}
      </DSStack>
    </div>
  );
};
