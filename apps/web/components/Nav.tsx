"use client";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useApi } from "@/lib/useApi";

export default function Nav() {
    const path = usePathname();
    const router = useRouter();
    const { data: me } = useApi<{ email: string; role: string }>(path === "/login" ? null : "/auth/me");

    if (path === "/login") return null;

    async function logout() {
        await fetch("/api/logout", { method: "POST" });
        router.push("/login");
    }

    const isAdmin = me?.role === "tenant_admin";
    const canSeePrivacy = isAdmin || me?.role === "privacy_admin";

    return (
        <nav className="border-b border-slate-200/80 bg-white/90 px-5 backdrop-blur sm:px-8">
            <div className="mx-auto flex min-h-18 max-w-6xl items-center gap-6">
                <Link href="/" className="flex items-center gap-3">
                    <span className="grid size-9 place-items-center rounded-xl bg-[#123b52] text-lg text-[#9bf0df] shadow-sm">✚</span>
                    <span>
                        <span className="block text-sm font-bold tracking-tight text-[#123b52]">ClinIQ</span>
                        <span className="hidden text-[10px] font-medium uppercase tracking-[0.16em] text-slate-400 sm:block">Clinical intelligence</span>
                    </span>
                </Link>
                <div className="hidden items-center gap-1 text-sm font-medium text-slate-500 sm:flex">
                    <Link href="/" className={`rounded-lg px-3 py-2 transition hover:bg-teal-50 hover:text-teal-800 ${path === "/" ? "bg-teal-50 text-teal-800" : ""}`}>Workspace</Link>
                    {canSeePrivacy && <Link href="/privacy" className={`rounded-lg px-3 py-2 transition hover:bg-teal-50 hover:text-teal-800 ${path === "/privacy" ? "bg-teal-50 text-teal-800" : ""}`}>Privacy</Link>}
                    {isAdmin && <Link href="/admin" className={`rounded-lg px-3 py-2 transition hover:bg-teal-50 hover:text-teal-800 ${path === "/admin" ? "bg-teal-50 text-teal-800" : ""}`}>Admin</Link>}
                </div>
                <div className="ml-auto flex items-center gap-3">
                    <span className="hidden max-w-48 truncate text-xs text-slate-500 md:block">{me?.email}</span>
                    <button onClick={logout} className="rounded-lg border border-slate-200 px-3 py-2 text-xs font-semibold text-slate-600 transition hover:border-slate-300 hover:bg-slate-50">Sign out</button>
                </div>
            </div>
        </nav>
    );
}