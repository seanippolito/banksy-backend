import pytest

@pytest.mark.asyncio
async def test_cors_headers(client):
    resp = await client.options(
        "/api/v1/health",
        headers={
            "origin": "http://localhost:3000",
            "access-control-request-method": "GET",
        },
    )
    assert resp.status_code in (200, 204)
    assert resp.headers.get("access-control-allow-origin") == "http://localhost:3000"


@pytest.mark.asyncio
async def test_users_router_mounted(authorized_client):
    resp = await authorized_client.get("/api/v1/users")
    # Either 200 with list or 200 empty
    assert resp.status_code == 200
