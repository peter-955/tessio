export interface InsightQueryState {
  isPending: boolean;
  isError: boolean;
  isFetching: boolean;
  refetch: () => unknown;
}
