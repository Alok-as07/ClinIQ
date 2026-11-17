import type { TrendPoint } from "@/lib/types";

export default function TrendChart({ points, unit }: { points: TrendPoint[]; unit: string }) {
    if (points.length < 2) {
        return <p className="text-sm text-slate-500">A trend needs at least two reviewed results.</p>;
    }

    const W = 480, H = 160, pad = 28;
    const xs = points.map((p) => new Date(p.date).getTime());
    const ys = points.map((p) => p.value);
    const [x0, x1] = [Math.min(...xs), Math.max(...xs)];
    const [y0, y1] = [Math.min(...ys), Math.max(...ys)];
    const sx = (x: number) => pad + ((x - x0) / (x1 - x0 || 1)) * (W - pad * 2);
    const sy = (y: number) => H - pad - ((y - y0) / (y1 - y0 || 1)) * (H - pad * 2);
    const coords = points.map((p, i) => `${sx(xs[i])},${sy(p.value)}`);

    return (
        <svg viewBox={`0 0 ${W} ${H}`} className="w-full max-w-lg rounded border bg-white">
            <polyline points={coords.join(" ")} fill="none" stroke="#334155" strokeWidth="2" />
            {points.map((p, i) => (
                <g key={p.date + i}>
                    <circle cx={sx(xs[i])} cy={sy(p.value)} r="4" fill={p.flag && p.flag !== "within" ? "#dc2626" : "#334155"}>
                        <title>{`${p.date}: ${p.value} ${unit}${p.flag ? ` (${p.flag} range)` : ""}`}</title>
                    </circle>
                    <text x={sx(xs[i])} y={H - 8} fontSize="9" textAnchor="middle" fill="#64748b">{p.date.slice(2)}</text>
                </g>
            ))}
            <text x={4} y={12} fontSize="10" fill="#64748b">{unit}</text>
        </svg>
    );
}