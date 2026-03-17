import { useEffect, useState } from "react";

export function useApi(loader, deps = []) {
  const [state, setState] = useState({
    data: null,
    loading: true,
    error: null,
  });

  useEffect(() => {
    let cancelled = false;

    async function run() {
      setState((current) => ({ ...current, loading: true, error: null }));
      try {
        const data = await loader();
        if (!cancelled) {
          setState({ data, loading: false, error: null });
        }
      } catch (error) {
        if (!cancelled) {
          setState({ data: null, loading: false, error });
        }
      }
    }

    run();
    return () => {
      cancelled = true;
    };
  }, deps);

  return state;
}
