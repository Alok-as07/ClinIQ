"use client";
import { useState } from "react";
import { useApi } from "@/lib/useApi";

type Redaction = {
    id: string; document_id: string; policy_version: string; action: string;
    entity_counts: Record<string, number>; created_at: string;
};
type Audit = {
    id: string; actor_id: string; action: string; resource_type: string;
    resource_id: string; outcome: string; created_at: string;
};

export default function Privacy() {
    const [tab, setTab] = useState<"redactions" | "audit">("redactions");
    const { data: red, error } = useApi<Redaction[]>(tab === "redactions" ? "/privacy/events" : null);
    const { data: aud } = useApi<Audit[]>(tab === "audit" ? "/audit/events" : null);

    return (
        <div className="space-y-7">
            <header>
                <p className="eyebrow">Governance</p>
                <h1 className="mt-2 text-3xl font-bold tracking-tight text-[#123b52]">Privacy console</h1>
                <p className="mt-2 text-sm text-slate-500">Review how sensitive clinical data is handled across the workspace.</p>
            </header>
            <div className="flex w-fit gap-1 rounded-xl border border-slate-200 bg-white p-1 text-sm">
                {(["redactions", "audit"] as const).map((t) => (
                    <button key={t} onClick={() => setTab(t)} className={`rounded-lg px-3 py-2 transition ${tab === t ? "bg-[#123b52] font-semibold text-white" : "text-slate-500 hover:bg-slate-50"}`}>
                        {t === "redactions" ? "Redaction events" : "Audit trail"}
                    </button>
                ))}
            </div>
            {error && <p className="text-sm text-red-600">{error}</p>}

            {tab === "redactions" && (
                <div className="panel overflow-x-auto"><table className="w-full min-w-[700px] text-sm">
                    <thead className="bg-slate-50 text-left text-xs uppercase tracking-wide text-slate-400"><tr><th className="p-3">When</th><th>Document</th><th>Action</th><th>Policy</th><th>Identifiers found</th></tr></thead>
                    <tbody>
                        {red?.map((e) => (
                            <tr key={e.id} className="border-t border-slate-100">
                                <td className="p-3 text-slate-500">{new Date(e.created_at).toLocaleString()}</td>
                                <td>{e.document_id}</td><td>{e.action}</td><td>{e.policy_version}</td>
                                <td>{Object.entries(e.entity_counts).map(([k, v]) => `${k}: ${v}`).join(", ") || "none"}</td>
                            </tr>
                        ))}
                    </tbody>
                </table></div>
            )}

            {tab === "audit" && (
                <div className="panel overflow-x-auto"><table className="w-full min-w-[700px] text-sm">
                    <thead className="bg-slate-50 text-left text-xs uppercase tracking-wide text-slate-400"><tr><th className="p-3">When</th><th>Actor</th><th>Action</th><th>Resource</th><th>Outcome</th></tr></thead>
                    <tbody>
                        {aud?.map((e) => (
                            <tr key={e.id} className="border-t border-slate-100">
                                <td className="p-3 text-slate-500">{new Date(e.created_at).toLocaleString()}</td>
                                <td>{e.actor_id}</td><td>{e.action}</td><td>{e.resource_type}/{e.resource_id}</td><td>{e.outcome}</td>
                            </tr>
                        ))}
                    </tbody>
                </table></div>
            )}
        </div>
    );
}