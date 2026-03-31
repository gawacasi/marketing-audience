import { FormEvent, useEffect, useState } from "react";
import { fetchJson, type Paginated, type UserOut } from "../api";

type Filters = {
  name: string;
  minAge: string;
  maxAge: string;
  minIncome: string;
  maxIncome: string;
};

export default function UsersPage() {
  const [data, setData] = useState<Paginated<UserOut> | null>(null);
  const [page, setPage] = useState(1);
  const [draft, setDraft] = useState<Filters>({
    name: "",
    minAge: "",
    maxAge: "",
    minIncome: "",
    maxIncome: "",
  });
  const [applied, setApplied] = useState<Filters>(draft);
  const [error, setError] = useState<string | null>(null);

  function buildQuery(p: number, f: Filters) {
    const params = new URLSearchParams();
    params.set("page", String(p));
    params.set("page_size", "20");
    if (f.name.trim()) params.set("name", f.name.trim());
    if (f.minAge) params.set("min_age", f.minAge);
    if (f.maxAge) params.set("max_age", f.maxAge);
    if (f.minIncome) params.set("min_income", f.minIncome);
    if (f.maxIncome) params.set("max_income", f.maxIncome);
    return `/users?${params.toString()}`;
  }

  useEffect(() => {
    setError(null);
    fetchJson<Paginated<UserOut>>(buildQuery(page, applied))
      .then(setData)
      .catch((e) => setError(e instanceof Error ? e.message : "Erro"));
  }, [page, applied]);

  function onFilter(e: FormEvent) {
    e.preventDefault();
    setApplied(draft);
    setPage(1);
  }

  return (
    <div className="panel">
      <h1>Usuários</h1>
      <form className="filters" onSubmit={onFilter}>
        <label>
          Nome
          <input
            value={draft.name}
            onChange={(e) => setDraft((d) => ({ ...d, name: e.target.value }))}
          />
        </label>
        <label>
          Idade mín
          <input
            type="number"
            min={0}
            value={draft.minAge}
            onChange={(e) => setDraft((d) => ({ ...d, minAge: e.target.value }))}
          />
        </label>
        <label>
          Idade máx
          <input
            type="number"
            min={0}
            value={draft.maxAge}
            onChange={(e) => setDraft((d) => ({ ...d, maxAge: e.target.value }))}
          />
        </label>
        <label>
          Renda mín
          <input
            type="number"
            min={0}
            step="0.01"
            value={draft.minIncome}
            onChange={(e) =>
              setDraft((d) => ({ ...d, minIncome: e.target.value }))
            }
          />
        </label>
        <label>
          Renda máx
          <input
            type="number"
            min={0}
            step="0.01"
            value={draft.maxIncome}
            onChange={(e) =>
              setDraft((d) => ({ ...d, maxIncome: e.target.value }))
            }
          />
        </label>
        <button type="submit">Aplicar filtros</button>
      </form>
      {error && <p className="error">{error}</p>}
      {data && (
        <>
          <div className="table-wrap">
            <table className="table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>upload</th>
                  <th>customer_id</th>
                  <th>Nome</th>
                  <th>Idade</th>
                  <th>Cidade</th>
                  <th>Renda</th>
                </tr>
              </thead>
              <tbody>
                {data.data.map((u) => (
                  <tr key={u.id}>
                    <td>{u.id}</td>
                    <td className="mono">{u.upload_id.slice(0, 8)}…</td>
                    <td>{u.customer_id}</td>
                    <td>{u.name}</td>
                    <td>{u.age}</td>
                    <td>{u.city}</td>
                    <td>{u.income}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="pager">
            {page > 1 && (
              <button type="button" onClick={() => setPage((p) => p - 1)}>
                Anterior
              </button>
            )}
            <span>
              Página {data.page} · {data.total} registros
            </span>
            {data.page * data.page_size < data.total && (
              <button type="button" onClick={() => setPage((p) => p + 1)}>
                Próxima
              </button>
            )}
          </div>
        </>
      )}
    </div>
  );
}
