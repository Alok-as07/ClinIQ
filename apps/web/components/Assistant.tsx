"use client";
import Link from "next/link";
import { useRef, useState } from "react";
import { postJson } from "@/lib/api";

type Cite = {
    label: string;
    source: string | null;
    refs: { document_id: string; page?: number; observation_id?: string }[];
};

export default function Assistant({ patientId }: { patientId: string }) {
    const [question, setQuestion] = useState("");
    const [purpose, setPurpose] = useState("treatment");
    const [status, setStatus] = useState("");
    const [answer, setAnswer] = useState("");
    const [cites, setCites] = useState<Cite[]>([]);
    const [unsupported, setUnsupported] = useState<string[]>([]);
    const [limits, setLimits] = useState<string[]>([]);
    const [busy, setBusy] = useState(false);
    const stream = useRef<EventSource | null>(null);

    async function ask() {
        stream.current?.close();
        setAnswer(""); setCites([]); setUnsupported([]); setLimits([]); setBusy(true);

        try {
            const { request_id } = await postJson<{ request_id: string }>("/clinical-assistant/query", {
                patient_id: patientId, question, purpose,
            });

            const es = new EventSource(`/api/v1/clinical-assistant/stream/${request_id}`);
            stream.current = es;

            es.addEventListener("status", (e) => setStatus(JSON.parse(e.data).message));
            es.addEventListener("token", (e) => setAnswer((a) => a + JSON.parse(e.data).text));
            es.addEventListener("citation", (e) => {
                const c: Cite = JSON.parse(e.data);
                setCites((all) => (all.some((x) => x.label === c.label) ? all : [...all, c]));
            });
            es.addEventListener("unsupported", (e) => setUnsupported(JSON.parse(e.data).claims));
            es.addEventListener("limitations", (e) => setLimits(JSON.parse(e.data).items));
            es.addEventListener("complete", () => { es.close(); setBusy(false); setStatus(""); });
            // EventSource reconnects by itself on errors, and our stream is one-shot, so stop it
            es.onerror = () => { es.close(); setBusy(false); setStatus("Connection lost, please ask again."); };
        } catch (err) {
            setStatus((err as Error).message);
            setBusy(false);
        }
    }

    return (
        <section className="panel overflow-hidden">
            <div className="border-b border-slate-100 bg-[#123b52] px-5 py-4 text-white">
                <p className="text-[10px] font-bold uppercase tracking-[0.14em] text-[#9bf0df]">Evidence companion</p>
                <h2 className="mt-1 text-lg font-semibold">Clinical assistant</h2>
                <p className="mt-1 text-xs text-slate-300">Summarizes this record with source citations. It does not diagnose or prescribe.</p>
            </div>
            <div className="space-y-4 p-5">

            <div className="flex flex-col gap-2 sm:flex-row">
                <input
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && question.length > 2 && !busy && ask()}
                    placeholder="e.g. How has creatinine changed over the last 6 months?"
                    className="flex-1 rounded-lg border border-slate-200 bg-white p-3 text-sm"
                />
                <select value={purpose} onChange={(e) => setPurpose(e.target.value)} className="rounded-lg border border-slate-200 bg-white p-3 text-sm">
                    <option value="treatment">Treatment</option>
                    <option value="care_review">Care review</option>
                    <option value="quality_review">Quality review</option>
                </select>
                <button onClick={ask} disabled={busy || question.length < 3} className="rounded-lg bg-[#2f9f8c] px-5 py-2 text-sm font-semibold text-white transition hover:bg-[#267f71] disabled:opacity-50">
                    Ask
                </button>
            </div>

            {status && <p className="text-sm text-slate-500">{status}</p>}
            {answer && <p className="rounded-xl border border-teal-100 bg-teal-50 p-4 text-sm leading-relaxed text-slate-700">{answer}</p>}

            {cites.length > 0 && (
                <div className="space-y-1 text-sm">
                    <h3 className="font-medium">Evidence</h3>
                    {cites.map((c) => (
                        <div key={c.label} className="flex flex-wrap items-center gap-2">
                            <span className="rounded bg-slate-200 px-1.5 text-xs">{c.label}</span>
                            {c.source && <span className="text-slate-600">{c.source}</span>}
                            {c.refs.map((r, i) => (
                                <Link key={i} className="underline" href={`/documents/${r.document_id}?page=${r.page ?? 1}`}>
                                    {r.document_id}{r.page ? ` p.${r.page}` : ""}
                                </Link>
                            ))}
                        </div>
                    ))}
                </div>
            )}

            {unsupported.length > 0 && (
                <div className="rounded border border-amber-300 bg-amber-50 p-3 text-sm">
                    <b>Not supported by the records:</b>
                    <ul className="list-disc pl-5">{unsupported.map((u, i) => <li key={i}>{u}</li>)}</ul>
                </div>
            )}
            {limits.length > 0 && (
                <ul className="list-disc pl-5 text-xs text-slate-500">{limits.map((l, i) => <li key={i}>{l}</li>)}</ul>
            )}
            </div>
        </section>
    );
}