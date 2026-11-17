"use client";
import { useApi } from "@/lib/useApi";

export default function Admin() {
    const { data: users, error } = useApi<{ id: string; email: string; role: string }[]>("/admin/users");
    const { data: cfg } = useApi<{ model: string; allowed_models: string[]; max_upload_mb: number }>("/admin/config");

    return (
        <div className="space-y-8">
            <header>
                <p className="eyebrow">Workspace settings</p>
                <h1 className="mt-2 text-3xl font-bold tracking-tight text-[#123b52]">Admin overview</h1>
                <p className="mt-2 text-sm text-slate-500">Manage access and the clinical model policy for your organization.</p>
            </header>
            {error && <p className="rounded-xl border border-red-200 bg-red-50 p-3 text-sm text-red-700">{error}</p>}

            <div className="grid gap-5 lg:grid-cols-[1.4fr_1fr]">
                <section className="panel overflow-hidden">
                    <div className="flex items-center justify-between border-b border-[#e5eef2] px-5 py-4">
                        <div><h2 className="font-semibold text-[#123b52]">Team members</h2><p className="mt-1 text-xs text-slate-500">People with access to this workspace</p></div>
                        <span className="status-pill bg-teal-50 text-teal-700">{users?.length ?? 0} members</span>
                    </div>
                    <ul className="divide-y divide-[#e5eef2] text-sm">
                        {users?.map((u) => (
                            <li key={u.id} className="flex items-center gap-3 px-5 py-4">
                                <span className="grid size-9 place-items-center rounded-full bg-[#e6f5f1] text-xs font-bold text-[#267f71]">{u.email.slice(0, 1).toUpperCase()}</span>
                                <span className="font-medium text-slate-700">{u.email}</span>
                                <span className="ml-auto status-pill bg-slate-100 text-slate-500">{u.role.replace("_", " ")}</span>
                            </li>
                        ))}
                        {!users && <li className="px-5 py-6 text-sm text-slate-400">Loading members...</li>}
                    </ul>
                </section>

            {cfg && (
                <section className="panel p-5 text-sm">
                    <p className="eyebrow">Configuration</p>
                    <h2 className="mt-2 text-lg font-semibold text-[#123b52]">Model policy</h2>
                    <dl className="mt-5 space-y-4">
                        <div><dt className="text-xs text-slate-400">Active model</dt><dd className="mt-1 font-semibold text-slate-700">{cfg.model}</dd></div>
                        <div><dt className="text-xs text-slate-400">Allowed models</dt><dd className="mt-1 font-semibold text-slate-700">{cfg.allowed_models.join(", ")}</dd></div>
                        <div><dt className="text-xs text-slate-400">Maximum upload</dt><dd className="mt-1 font-semibold text-slate-700">{cfg.max_upload_mb} MB</dd></div>
                    </dl>
                </section>
            )}
            </div>
        </div>
    );
}