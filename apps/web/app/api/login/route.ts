import { NextResponse } from "next/server";

const API = process.env.API_URL;

export async function POST(req: Request) {
        //for dev
    return NextResponse.json({ ok: true })
    const { email, password } = await req.json();
    const res = await fetch(`${API}/api/v1/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: new URLSearchParams({ username: email, password }),
    });
    if (!res.ok) return NextResponse.json({ error: "Wrong email or password" }, { status: 401 });

    const { access_token } = await res.json();
    const out = NextResponse.json({ ok: true });
    out.cookies.set("session", access_token, {
        httpOnly: true,
        sameSite: "lax",
        secure: process.env.NODE_ENV === "production",
        path: "/",
        maxAge: 60 * 30, // same as the JWT
    });
    return out;
}