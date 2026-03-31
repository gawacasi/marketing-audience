import { FormEvent, useCallback, useEffect, useRef, useState } from "react";
import {
  API_BASE,
  fetchJson,
  type UploadResponse,
  type UploadStatus,
} from "../api";

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [uploadResult, setUploadResult] = useState<UploadResponse | null>(null);
  const [status, setStatus] = useState<UploadStatus | null>(null);
  const pollRef = useRef<number | null>(null);

  const stopPoll = useCallback(() => {
    if (pollRef.current != null) {
      window.clearInterval(pollRef.current);
      pollRef.current = null;
    }
  }, []);

  useEffect(() => () => stopPoll(), [stopPoll]);

  async function pollStatus(uploadId: string) {
    try {
      const s = await fetchJson<UploadStatus>(`/upload/${uploadId}/status`);
      setStatus(s);
      if (s.status === "completed" || s.status === "failed") {
        stopPoll();
      }
    } catch {
      stopPoll();
    }
  }

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    if (!file) return;
    setError(null);
    setLoading(true);
    setUploadResult(null);
    setStatus(null);
    stopPoll();
    try {
      const fd = new FormData();
      fd.append("file", file);
      const res = await fetch(`${API_BASE}/upload`, { method: "POST", body: fd });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data?.message ?? "Falha no upload");
      }
      setUploadResult(data as UploadResponse);
      const id = (data as UploadResponse).upload_id;
      await pollStatus(id);
      pollRef.current = window.setInterval(() => void pollStatus(id), 1500);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="panel">
      <h1>Upload de CSV</h1>
      <p className="muted">
        Envie um arquivo com colunas: <code>id,name,age,city,income</code>
      </p>
      <form onSubmit={onSubmit} className="form">
        <input
          type="file"
          accept=".csv,text/csv"
          onChange={(e) => setFile(e.target.files?.[0] ?? null)}
        />
        <button type="submit" disabled={!file || loading}>
          {loading ? "Enviando…" : "Enviar"}
        </button>
      </form>
      {error && <p className="error">{error}</p>}
      {uploadResult && (
        <section className="section">
          <h2>Resposta do upload</h2>
          <ul className="kv">
            <li>
              <span>upload_id</span> <code>{uploadResult.upload_id}</code>
            </li>
            <li>
              <span>Linhas totais</span> {uploadResult.total_rows}
            </li>
            <li>
              <span>Válidas</span> {uploadResult.valid_rows}
            </li>
            <li>
              <span>Inválidas</span> {uploadResult.invalid_rows}
            </li>
          </ul>
          {uploadResult.errors.length > 0 && (
            <>
              <h3>Erros por linha</h3>
              <div className="table-wrap">
                <table className="table">
                  <thead>
                    <tr>
                      <th>Linha</th>
                      <th>Campo</th>
                      <th>Mensagem</th>
                    </tr>
                  </thead>
                  <tbody>
                    {uploadResult.errors.map((e, i) => (
                      <tr key={i}>
                        <td>{e.row}</td>
                        <td>{e.field}</td>
                        <td>{e.message}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </>
          )}
        </section>
      )}
      {status && (
        <section className="section">
          <h2>Status do processamento</h2>
          <p>
            Estado: <strong className={`status-${status.status}`}>{status.status}</strong>
          </p>
          {status.processed_at && (
            <p className="muted">Processado em: {status.processed_at}</p>
          )}
        </section>
      )}
    </div>
  );
}
