import { useEffect, useState } from "react";
import { Link, useParams, useSearchParams } from "react-router-dom";
import { fetchJson, type CampaignUsersResponse } from "../api";

export default function CampaignDetailPage() {
  const { id } = useParams();
  const [search] = useSearchParams();
  const page = Number(search.get("page") ?? "1") || 1;
  const [data, setData] = useState<CampaignUsersResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    setError(null);
    fetchJson<CampaignUsersResponse>(
      `/campaigns/${id}?page=${page}&page_size=20`
    )
      .then(setData)
      .catch((e) => setError(e instanceof Error ? e.message : "Erro"));
  }, [id, page]);

  if (!id) return null;

  return (
    <div className="panel">
      <p>
        <Link to="/campaigns">← Campanhas</Link>
      </p>
      {error && <p className="error">{error}</p>}
      {data && (
        <>
          <h1>{data.campaign.name}</h1>
          <p className="muted">
            Usuários na campanha: {data.campaign.users_count} · Renda média:{" "}
            {data.campaign.average_income.toFixed(2)}
          </p>
          <div className="table-wrap">
            <table className="table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>customer_id</th>
                  <th>Nome</th>
                  <th>Idade</th>
                  <th>Cidade</th>
                  <th>Renda</th>
                </tr>
              </thead>
              <tbody>
                {data.users.data.map((u) => (
                  <tr key={u.id}>
                    <td>{u.id}</td>
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
              <Link to={`/campaigns/${id}?page=${page - 1}`}>Anterior</Link>
            )}
            <span>
              Página {data.users.page} de {Math.max(1, Math.ceil(data.users.total / data.users.page_size))}
            </span>
            {data.users.page * data.users.page_size < data.users.total && (
              <Link to={`/campaigns/${id}?page=${page + 1}`}>Próxima</Link>
            )}
          </div>
        </>
      )}
    </div>
  );
}
