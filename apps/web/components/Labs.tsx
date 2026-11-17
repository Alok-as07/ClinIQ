"use client";
import Link from "next/link";
import { useState } from "react";
import TrendChart from "@/components/TrendChart";
import type { Obs, Trend } from "@/lib/types";
import { useApi } from "@/lib/useApi";

type ObsRow = Obs & { document_id: string };

export default function Labs({ patientId }: { patientId: string }) {
    const { data: obs } = useApi<ObsRow[]>(`/patients/${patientId}/observations`);
    const [test, setTest] = useState("");

    const names = [...new Set(obs?.map((o) => o.test_name))];
    const chosen = test || names[0] || "";
    const { data: trend, error } = useApi<Trend>(
        chosen ? `/patients/${patientId}/trends?test=${encodeURIComponent(chosen)}&months=12` : null,
    );

    return (
        <section className="panel overflow-hidden">
            <div className="border-b border-slate-100 px-5 py-4">
                <p className="eyebrow">Measurements</p>
                <h2 className="mt-1 text-lg font-semibold text-[#123b52]">Lab results</h2>
            </div>
            <div className="space-y-4 p-5">
            {obs?.length === 0 && <p className="text-sm text-slate-500">No extracted results yet.</p>}

            {names.length > 0 && (
                <div className="space-y-2">
                    <select value={chosen} onChange={(e) => setTest(e.target.value)} className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-700">
                        {names.map((n) => <option key={n}>{n}</option>)}
                    </select>
                    {error && <p className="text-sm text-amber-700">{error}</p>}
                    {trend?.unit && <TrendChart points={trend.points} unit={trend.unit} />}
                    {trend?.change && (
                        <p className="text-sm">
                            First to last: {trend.change.absolute > 0 ? "+" : ""}{trend.change.absolute} {trend.unit}
                            {trend.change.percent !== null && ` (${trend.change.percent}%)`}, {trend.change.direction}.
                        </p>
                    )}
                </div>
            )}

            <div className="overflow-x-auto rounded-xl border border-slate-100">
            <table className="w-full min-w-[680px] text-sm">
                <thead className="bg-slate-50 text-left text-xs uppercase tracking-wide text-slate-400">
                    <tr><th className="p-2">Test</th><th>Value</th><th>Range</th><th>Date</th><th>Status</th><th>Source</th></tr>
                </thead>
                <tbody>
                    {obs?.map((o) => (
                        <tr key={o.id} className="border-t border-slate-100">
                            <td className="p-2">{o.test_name}</td>
                            <td>{o.value} {o.unit}</td>
                            <td>{o.reference_range ?? "-"}</td>
                            <td>{o.observed_at}</td>
                            <td>{o.needs_review ? "awaiting review" : o.review_status}</td>
                            <td><Link className="underline" href={`/documents/${o.document_id}?page=${o.page}`}>p.{o.page}</Link></td>
                        </tr>
                    ))}
                </tbody>
            </table>
            </div>
            </div>
        </section>
    );
}