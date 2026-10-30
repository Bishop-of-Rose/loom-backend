from typing import Any

from httpx2 import AsyncClient

from src.schemas import PostResponse

async def test_create_post_success(
    client: AsyncClient, init_auth_header: dict[str, str]
):
    payload = {'title': 'random title', 'content': 'random content'}
    res = await client.post('/posts', headers=init_auth_header, json=payload)
    assert res.status_code == 201
    post = res.json()
    PostResponse.model_validate(post)
    payload.update(post)
    assert payload == post

async def test_update_post_success(
    client: AsyncClient, init_auth_header: dict[str, str], created_post: dict[str, Any]
):
    payload = {'title': 'updated title', 'content': 'updated content'}
    res = await client.put(
        f'/posts/{created_post['id']}', headers=init_auth_header, json=payload
    )
    assert res.status_code == 200
    post = res.json()
    PostResponse.model_validate(post)
    payload.update(post)
    assert payload == post

async def test_delete_post_success(
    client: AsyncClient, init_auth_header: dict[str, str], created_post: dict[str, Any]
):
    res = await client.delete(f'/posts/{created_post["id"]}', headers=init_auth_header)
    assert res.status_code == 204
    res = await client.delete(f'/posts/{created_post["id"]}', headers=init_auth_header)
    assert res.status_code == 404