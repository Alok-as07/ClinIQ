import { NextResponse } from "next/server";

export async function POST() {
    const out = NextResponse.json({ ok: true });
    out.cookies.delete("session");
    return out;
}