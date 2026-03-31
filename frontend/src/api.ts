export const API_BASE = import.meta.env.VITE_API_BASE ?? "";

export async function fetchJson<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      Accept: "application/json",
      ...(init?.headers ?? {}),
    },
  });
  const text = await res.text();
  const data = text ? JSON.parse(text) : null;
  if (!res.ok) {
    const msg = data?.message ?? res.statusText;
    throw new Error(msg || `HTTP ${res.status}`);
  }
  return data as T;
}

export type UploadResponse = {
  upload_id: string;
  status: string;
  total_rows: number;
  valid_rows: number;
  invalid_rows: number;
  errors: { row: number; field: string; message: string }[];
};

export type Paginated<T> = {
  data: T[];
  page: number;
  page_size: number;
  total: number;
};

export type UploadStatus = {
  id: string;
  filename: string;
  status: string;
  total_rows: number;
  valid_rows: number;
  invalid_rows: number;
  created_at: string;
  processed_at: string | null;
};

export type CampaignSummary = {
  id: number;
  name: string;
  users_count: number;
  average_income: number;
};

export type UserOut = {
  id: number;
  upload_id: string;
  customer_id: number;
  name: string;
  age: number;
  city: string;
  income: number;
};

export type CampaignUsersResponse = {
  campaign: {
    id: number;
    name: string;
    users_count: number;
    average_income: number;
  };
  users: Paginated<UserOut>;
};
