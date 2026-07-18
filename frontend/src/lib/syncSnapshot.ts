/**
 * Cached snapshot helpers for useSyncExternalStore.
 * getSnapshot must return a stable reference until the store changes.
 */

export interface CachedExternalStore<T> {
  subscribe: (onStoreChange: () => void) => () => void;
  getSnapshot: () => T;
  getServerSnapshot: () => T;
}

export function createCachedSnapshot<T>(
  read: () => T,
  subscribeToStore: (onStoreChange: () => void) => () => void,
  getServerSnapshot: () => T,
): CachedExternalStore<T> {
  let snapshot = getServerSnapshot();
  let version = 0;
  let cachedVersion = -1;

  function getSnapshot(): T {
    if (cachedVersion !== version) {
      snapshot = read();
      cachedVersion = version;
    }
    return snapshot;
  }

  function subscribe(onStoreChange: () => void) {
    return subscribeToStore(() => {
      version += 1;
      onStoreChange();
    });
  }

  return { subscribe, getSnapshot, getServerSnapshot };
}

export function createCachedPrimitiveSnapshot<T extends string | number | boolean | null>(
  read: () => T,
  subscribeToStore: (onStoreChange: () => void) => () => void,
  getServerSnapshot: () => T,
): CachedExternalStore<T> {
  return createCachedSnapshot(read, subscribeToStore, getServerSnapshot);
}
