import { NetworkStatus } from '@apollo/client';

export interface RequestState {
  isInitial: boolean;
  isRefreshing: boolean;
  isPaginating: boolean;
}

export function useRequestState(networkStatus?: number): RequestState {
  const status = networkStatus ?? 0;
  return {
    isInitial: status === NetworkStatus.loading || status === 1,
    isRefreshing:
      status === NetworkStatus.refetch ||
      status === NetworkStatus.poll ||
      status === 3 ||
      status === 6,
    isPaginating:
      status === NetworkStatus.fetchMore || status === 7 /* legacy mapping */,
  };
}
