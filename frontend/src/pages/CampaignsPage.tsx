import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  fetchJson,
  type CampaignSummary,
  type Paginated,
  type UploadStatus,
} from "../api";

function formatUploadLabel(u: UploadStatus): string {
  const date = new Date(u.created_at);
  const when = Number.isNaN(date.getTime())
    ? u.created_at
    : date.toLocaleString(undefined, {
        dateStyle: "short",
        timeStyle: "short",
      });
  return `${u.filename} · ${when} · ${u.status}`;
}

export default function CampaignsPage() {
  const [data, setData] = useState<Paginated<CampaignSummary> | null>(null);
  const [uploads, setUploads] = useState<UploadStatus[] | null>(null);
  const [uploadId, setUploadId] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [uploadsError, setUploadsError] = useState<string | null>(null);

  useEffect(() => {
    setUploadsError(null);
    fetchJson<Paginated<UploadStatus>>("/uploads?page=1&page_size=100")
      .then((res) => setUploads(res.data))
      .catch((e) =>
        setUploadsError(e instanceof Error ? e.message : "Erro ao carregar uploads")
      );
  }, []);

  useEffect(() => {
    const q = uploadId.trim()
      ? `/campaigns?page=1&page_size=20&upload_id=${encodeURIComponent(uploadId.trim())}`
      : "/campaigns?page=1&page_size=20";
    setError(null);
    fetchJson<Paginated<CampaignSummary>>(q)
      .then(setData)
      .catch((e) => setError(e instanceof Error ? e.message : "Erro"));
  }, [uploadId]);

  return (
    <div className="panel">
      <h1>Campanhas</h1>
      <label className="field">
        Upload (filtro opcional)
        <select
          value={uploadId}
          onChange={(e) => setUploadId(e.target.value)}
          disabled={uploads === null && uploadsError === null}
        >
          <option value="">Todos os uploads</option>
          {uploads?.map((u) => (
            <option key={u.id} value={u.id}>
              {formatUploadLabel(u)}
            </option>
          ))}
        </select>
      </label>
      {uploadsError && <p className="error">{uploadsError}</p>}
      {error && <p className="error">{error}</p>}
      {data && (
        <div className="table-wrap">
          <table className="table">
            <thead>
              <tr>
                <th>Nome</th>
                <th>Usuários</th>
                <th>Renda média</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {data.data.map((c) => (
                <tr key={c.id}>
                  <td>{c.name}</td>
                  <td>{c.users_count}</td>
                  <td>{c.average_income.toFixed(2)}</td>
                  <td>
                    <Link to={`/campaigns/${c.id}`}>Detalhe</Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
