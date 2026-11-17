"use client";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { postJson } from "@/lib/api";
import type { Doc, Patient } from "@/lib/types";
import { useApi } from "@/lib/useApi";

type Overview = {
  pending_reviews: number; processing: number; needs_attention: number;
  ai: { requests_7d: number; tokens_7d: number; avg_latency_ms: number };
  recent_patients: string[];
};

function Card({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded border bg-white p-4">
      <div className="text-2xl font-semibold">{value}</div>
      <div className="text-sm text-slate-500">{label}</div>
    </div>
  );
}

export default function Home() {
  const router = useRouter();
  const { data: o } = useApi<Overview>("/overview");
  const { data: patients, reload } = useApi<Patient[]>("/patients");
  const { data: queue } = useApi<Doc[]>("/documents?status=needs_review");

  async function addPatient() {
    const p = await postJson<Patient>("/patients", {});
    reload();
    router.push(`/patients/${p.id}`);
  }

  return (
    <div className="space-y-8">
      <section className="grid grid-cols-2 gap-3 md:grid-cols-4">
        <Card label="Waiting for review" value={o?.pending_reviews ?? "-"} />
        <Card label="Processing" value={o?.processing ?? "-"} />
        <Card label="Needs attention" value={o?.needs_attention ?? "-"} />
        <Card label="AI requests (7d)" value={o?.ai.requests_7d ?? "-"} />
      </section>
      {o && (
        <p className="text-sm text-slate-500">
          Last 7 days: {o.ai.tokens_7d.toLocaleString()} tokens, average {o.ai.avg_latency_ms} ms per answer.
        </p>
      )}

      <section>
        <h2 className="mb-2 font-semibold">Review queue</h2>
        {queue?.length === 0 && <p className="text-sm text-slate-500">Nothing waiting.</p>}
        <ul className="space-y-1 text-sm">
          {queue?.map((d) => (
            <li key={d.id}>
              <Link className="underline" href={`/documents/${d.id}`}>{d.id}</Link>
              <span className="ml-2 text-slate-500">{new Date(d.created_at).toLocaleString()}</span>
            </li>
          ))}
        </ul>
      </section>

      <section>
        <div className="mb-2 flex items-center justify-between">
          <h2 className="font-semibold">Patients</h2>
          <button onClick={addPatient} className="rounded border bg-white px-3 py-1 text-sm">
            New synthetic patient
          </button>
        </div>
        <ul className="space-y-1 text-sm">
          {patients?.map((p) => (
            <li key={p.id}>
              <Link className="underline" href={`/patients/${p.id}`}>{p.ref}</Link>
              {o?.recent_patients.includes(p.id) && <span className="ml-2 text-slate-500">recent</span>}
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}