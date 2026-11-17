"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { useApi } from "@/lib/useApi";

type Entry = { document_id: string; status: string; created_at: string };
const STILL_WORKING = ["queued", "redacted", "ready"];

export default function Timeline({ patientId }: { patientId: string }) {
    const { data, reload } = useApi<Entry[]>(`/patients/${patientId}/timeline`);
    const [msg, setMsg] = useState("");

    const busy = data?.some((d) => STILL_WORKING.includes(d.status));
    useEffect(() => {
        if (!busy) return;
        const t = setInterval(reload, 4000);
        return () => clearInterval(t);
    }, [busy, reload]);

    async function upload(e: React.ChangeEvent<HTMLInputElement>) {
        const file = e.target.files?.[0];
        if (!file) return;
        const body = new FormData();
        body.append("patient_id", patientId);
        body.append("file", file);
        try {
            await api("/documents", { method: "POST", body });
            setMsg("Uploaded, processing started.");
            reload();
        } catch (err) {
            setMsg((err as Error).message);
        }
        e.target.value = "";
    }

    return (
        <section className="panel overflow-hidden">
            <div className="flex items-center justify-between border-b border-slate-100 px-5 py-4">
                <div><p className="eyebrow">Record history</p><h2 className="mt-1 text-lg font-semibold text-[#123b52]">Documents</h2></div>
                <label className="cursor-pointer rounded-lg bg-[#123b52] px-3 py-2 text-xs font-semibold text-white shadow-sm transition hover:bg-[#1c526d]">
                    + Upload PDF
                    <input type="file" accept="application/pdf" onChange={upload} className="hidden" />
                </label>
            </div>
            {msg && <p className="border-b border-slate-100 bg-teal-50 px-5 py-3 text-sm text-teal-800">{msg}</p>}
            <ul className="divide-y divide-slate-100 text-sm">
                {data?.map((d) => (
                    <li key={d.document_id} className="flex items-center gap-3 px-5 py-4">
                        <span className="grid size-9 place-items-center rounded-lg bg-slate-100 text-slate-500">▤</span>
                        <Link className="font-semibold text-[#247b70] hover:underline" href={`/documents/${d.document_id}`}>{d.document_id}</Link>
                        <span className="status-pill bg-slate-100 text-slate-500">{d.status}</span>
                        <span className="ml-auto text-xs text-slate-400">{new Date(d.created_at).toLocaleString()}</span>
                    </li>
                ))}
                {data?.length === 0 && <li className="px-5 py-8 text-center text-slate-500">No documents yet. Upload a PDF to begin.</li>}
            </ul>
        </section>
    );
}