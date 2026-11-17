"use client";
import { useRouter } from "next/navigation";
import { useState } from "react";

export default function Login() {
    const router = useRouter();
    const [error, setError] = useState("");

    async function submit(e: React.FormEvent<HTMLFormElement>) {
        e.preventDefault();
        const form = new FormData(e.currentTarget);
        const res = await fetch("/api/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email: form.get("email"), password: form.get("password") }),
        });
        if (!res.ok) return setError("Wrong email or password");
        router.push("/");
    }

    return (
        <form onSubmit={submit} className="mx-auto mt-24 flex max-w-sm flex-col gap-3 rounded border bg-white p-6">
            <h1 className="text-lg font-semibold">Sign in</h1>
            <input name="email" type="email" placeholder="Email" required className="rounded border p-2" />
            <input name="password" type="password" placeholder="Password" required className="rounded border p-2" />
            {error && <p className="text-sm text-red-600">{error}</p>}
            <button className="rounded bg-slate-900 p-2 text-white">Sign in</button>
            <p className="text-xs text-slate-500">Synthetic data only. Not a medical device.</p>
        </form>
    );
}