import type { FC } from "react";
import type { InsightStat } from "../../typing/types/insight-stat.type";
import styles from "./insight-stat-list.module.scss";

interface Props {
  stats: InsightStat[];
}

export const InsightStatList: FC<Props> = ({ stats }) => {
  return (
    <dl className={styles.stats}>
      {stats.map((stat) => {
        return (
          <div key={stat.key} className={styles.tile}>
            <dt className={styles.label}>{stat.label}</dt>
            <dd className={styles.value}>{stat.value}</dd>
          </div>
        );
      })}
    </dl>
  );
};
