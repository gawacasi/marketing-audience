# Marketing Audience Campaign Builder

Projeto full-stack: você sobe um CSV de clientes, o backend valida linha a linha, joga o processamento pesado pro Celery e monta as campanhas (várias campanhas por usuário, via tabela de junção).

**Stack:** FastAPI + SQLAlchemy + Celery + Redis no backend; React + Vite no front. API documentada em `/docs` quando o servidor estiver no ar.

---

## Rodar na mão

Precisa de Python 3.12+, Node 20+ e Redis rodando (o worker Celery usa a fila).

## Backend (na pasta `backend`):

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL=sqlite:///./app.db
export REDIS_URL=redis://localhost:6379/0
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Worker (outro terminal, mesma venv):

```bash
celery -A app.celery_app worker --loglevel=info
```

## Frontend:

```bash
cd frontend && npm install && npm run dev
```

O vite encaminha as rotas da API pro `localhost:8000` — com a API ligada, é só abrir o que o vite mostrar (geralmente `http://localhost:5173`).

## Testes: `cd backend && pytest -v` (com dependências instaladas).

---

## Docker

Na raiz:

```bash
docker compose up --build
```

- API: http://localhost:8000  
- Interface: http://localhost:8080  
- Swagger: http://localhost:8000/docs  

Postgres e Redis no host estão mapeados pra **5433** e **6380** pra não brigar com instalação local na 5432/6379. Por dentro do Docker nada muda (`db` e `redis` como hostname).

---

- **Celery + Redis** pra gerar campanhas depois do upload sem travar a requisição.
- **Cada upload novo** gera um `upload_id` novo — mesmo CSV de novo = novo lote (histórico simples; da pra filtrar campanhas por `upload_id` na API).
- **`id` do CSV** vira `customer_id` no banco; o `id` numérico da tabela `users` é outro.
- Campanhas são as quatro do enunciado; se rodar o job de novo pro mesmo upload, eh limpado os vínculos daquele lote e recria (não duplica linha na junção).

---
