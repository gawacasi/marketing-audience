from io import BytesIO


def test_upload_flow_creates_users_and_campaigns(client):
    csv_content = (
        "id,name,age,city,income\n"
        "1,Alice,25,Sao Paulo,8000\n"
        "2,Bob,45,Rio,5000\n"
        "3,Carol,60,SP,2000\n"
    )
    files = {"file": ("customers.csv", BytesIO(csv_content.encode()), "text/csv")}
    r = client.post("/upload", files=files)
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["status"] == "processing"
    assert body["total_rows"] == 3
    assert body["valid_rows"] == 3
    upload_id = body["upload_id"]

    listed = client.get("/uploads").json()
    assert listed["total"] >= 1
    ids = {u["id"] for u in listed["data"]}
    assert upload_id in ids

    st = client.get(f"/upload/{upload_id}/status")
    assert st.status_code == 200
    assert st.json()["status"] == "completed"

    users = client.get("/users").json()
    assert users["total"] == 3

    camps = client.get("/campaigns", params={"upload_id": upload_id}).json()
    assert camps["total"] == 4
    by_name = {c["name"]: c for c in camps["data"]}
    assert by_name["Starter"]["users_count"] == 0
    assert by_name["Growth"]["users_count"] >= 1
    assert by_name["Premium"]["users_count"] >= 1

    detail = client.get(f"/campaigns/{by_name['High Value Youth']['id']}").json()
    assert detail["campaign"]["name"] == "High Value Youth"
    assert detail["users"]["total"] >= 1


def test_upload_partial_invalid_rows(client):
    csv_content = (
        "id,name,age,city,income\n"
        "1,OK,30,X,4000\n"
        "2,BAD,-5,X,4000\n"
    )
    files = {"file": ("x.csv", BytesIO(csv_content.encode()), "text/csv")}
    r = client.post("/upload", files=files)
    assert r.status_code == 201
    body = r.json()
    assert body["valid_rows"] == 1
    assert body["invalid_rows"] == 1
    assert len(body["errors"]) >= 1
