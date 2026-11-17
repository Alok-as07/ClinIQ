"use client";
import { useCallback, useEffect, useState } from "react";
import { api } from "./api";

export function useApi<T>(path: string | null) {
    const [data, setData] = useState<T | null>(null);
    const [error, setError] = useState<string | null>(null);

    const reload = useCallback(() => {
        if (!path) return;
        setError(null);
        api<T>(path).then(setData).catch((e) => setError(e.message));
    }, [path]);

    useEffect(reload, [reload]);
    return { data, error, reload };
}