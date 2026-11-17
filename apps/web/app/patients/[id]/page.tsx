"use client";
import { useParams } from "next/navigation";
import Assistant from "@/components/Assistant";
import Labs from "@/components/Labs";
import Timeline from "@/components/Timeline";

export default function PatientWorkspace() {
    const { id } = useParams<{ id: string }>();

    return (
        <div className="space-y-8">
            <header className="flex flex-col justify-between gap-4 border-b border-slate-200/80 pb-7 sm:flex-row sm:items-end">
              <div>
                <p className="eyebrow">Patient workspace</p>
                <h1 className="mt-2 text-3xl font-bold tracking-tight text-[#123b52]">Clinical record</h1>
                <p className="mt-2 text-sm text-slate-500">Review documents, lab trends, and evidence-backed insights in one place.</p>
              </div>
              <span className="status-pill w-fit bg-[#e6f5f1] text-[#267f71]">Secure workspace</span>
            </header>
            <Timeline patientId={id} />
            <Labs patientId={id} />
            <Assistant patientId={id} />
        </div>
    );
}