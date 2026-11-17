export async function api<T>(path: string, init?: RequestInit): Promise<T> {
    const res = await fetch(`/api/v1${path}`, init);

    if (res.status === 401) {
        window.location.href = "/login";
        throw new Error("Not signed in");
    }
    if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(typeof body.detail === "string" ? body.detail : `Request failed (${res.status})`);
    }
    return res.json();
}

export function postJson<T>(path: string, data: unknown) {
    return api<T>(path, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
    });
}