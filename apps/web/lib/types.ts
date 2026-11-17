export type Patient = { id: string; ref: string };
export type Doc = { id: string; patient_id: string; status: string; created_at: string };
export type Obs = {
    id: string; test_name: string; value: number; unit: string; reference_range: string | null;
    observed_at: string; page: number; source_quote: string; confidence: number;
    review_status: string; needs_review: boolean;
};
export type TrendPoint = {
    date: string; value: number; flag: string | null; reference_range: string | null;
    document_id: string; page: number;
};
export type Trend = {
    test: string; unit: string | null; points: TrendPoint[];
    change: { absolute: number; percent: number | null; direction: string } | null;
};