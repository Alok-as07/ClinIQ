"use client";
import { useParams, useSearchParams } from "next/navigation";
import { useState } from "react";
import { postJson } from "@/lib/api";
import type { Obs } from "@/lib/types";
import { useApi } from "@/lib/useApi";

type Detail = {
    id: string; patient_id: string; status: string;
    extraction_notes: { page: number; reason: string }[];
    observations: Obs[];
};
type Edit = { value?: number; unit?: string };

export default function ReviewPage() {
    const { id } = useParams<{ id: string }>();
    const startPage = Number(useSearchParams().get("page") ?? 1);
    const { data: doc, reload } = useApi<Detail>(`/documents/${id}`);

    const [page, setPage] = useState(startPage);
    const [edits, setEdits] = useState<Record<string, Edit>>({});
    const [error, setError] = useState("");

    function change(obsId: string, patch: Edit) {
        setEdits((e) => ({ ...e, [obsId]: { ...e[obsId], ...patch } }));
    }

    async function approve() {
        setError("");
        const corrections = Object.entries(edits).map(([observation_id, e]) => ({ observation_id, ...e }));
        try {
            await postJson(`/documents/${id}/review`, { corrections });
            setEdits({});
            reload();
        } catch (err) {
            setError((err as Error).message);
        }
    }

    if (!doc) return <p className="text-sm text-slate-500">Loading...</p>;

    return (
        <div className="grid gap-4 lg:grid-cols-2">
            <iframe
                key={page}
                src={`/api/v1/documents/${id}/file#page=${page}`}
                className="h-[80vh] w-full rounded border bg-white"
                title="Original document"
            />

            <div className="space-y-3">
                <div className="flex items-center gap-3">
                    <h1 className="font-semibold">Review extracted values</h1>
                    <span className="rounded bg-slate-100 px-2 py-0.5 text-xs">{doc.status}</span>
                </div>

                {doc.extraction_notes.length > 0 && (
                    <div className="rounded border border-amber-300 bg-amber-50 p-3 text-sm">
                        Some rows couldn&apos;t be read and need a manual look:
                        <ul className="list-disc pl-5">
                            {doc.extraction_notes.map((n, i) => <li key={i}>page {n.page}: {n.reason}</li>)}
                        </ul>
                    </div>
                )}

                {doc.observations.map((o) => (
                    <div key={o.id} onClick={() => setPage(o.page)}
                        className={`cursor-pointer rounded border bg-white p-3 text-sm ${o.needs_review ? "border-amber-400" : ""}`}>
                        <div className="flex justify-between">
                            <b>{o.test_name}</b>
                            <span className="text-slate-500">p.{o.page} · confidence {Math.round(o.confidence * 100)}%</span>
                        </div>
                        <p className="my-1 text-xs text-slate-500">&ldquo;{o.source_quote}&rdquo;</p>
                        <div className="flex items-center gap-2" onClick={(e) => e.stopPropagation()}>
                            <input
                                type="number" step="any" defaultValue={o.value} disabled={doc.status !== "needs_review"}
                                onChange={(e) => change(o.id, { value: Number(e.target.value) })}
                                className="w-24 rounded border p-1"
                            />
                            <input
                                defaultValue={o.unit} disabled={doc.status !== "needs_review"}
                                onChange={(e) => change(o.id, { unit: e.target.value })}
                                className="w-24 rounded border p-1"
                            />
                            <span className="text-xs text-slate-500">range: {o.reference_range ?? "none given"}</span>
                            <span className="ml-auto text-xs">{o.needs_review ? "needs a look" : o.review_status}</span>
                        </div>
                    </div>
                ))}

                {error && <p className="text-sm text-red-600">{error}</p>}
                {doc.status === "needs_review" && (
                    <button onClick={approve} className="rounded bg-slate-900 px-4 py-2 text-sm text-white">
                        Approve{Object.keys(edits).length > 0 ? ` with ${Object.keys(edits).length} correction(s)` : ""} and index
                    </button>
                )}
            </div>
        </div>
    );
}