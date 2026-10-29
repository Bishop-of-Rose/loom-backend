from typing import Any

from httpx2 import AsyncClient

from src.schemas import PostResponse

async def test_create_post_success(
    client: AsyncClient, init_auth_header: dict[str, str]
):
    payload = {'title': 'random title', 'content': 'random content'}
    res = await client.post('/posts', headers=init_auth_header, json=payload)
    assert res.status_code == 201
    PostResponse.model_validate(res.json())
    assert res.json()['title'] == payload['title']
    assert res.json()['content'] == payload['content']

async def test_update_post_success(
    client: AsyncClient, init_auth_header: dict[str, str], created_post: dict[str, Any]
):
    payload = {'title': 'updated title', 'content': 'updated content'}
    res = await client.put(
        f'/posts/{created_post["id"]}', headers=init_auth_header, json=payload
    )
    assert res.status_code == 200
    PostResponse.model_validate(res.json())
    assert res.json()['title'] == payload['title']
    assert res.json()['content'] == payload['content']

async def test_delete_post_success(
    client: AsyncClient, init_auth_header: dict[str, str], created_post: dict[str, Any]
):
    res = await client.delete(f'/posts/{created_post["id"]}', headers=init_auth_header)
    assert res.status_code == 204
    res = await client.delete(f'/posts/{created_post["id"]}', headers=init_auth_header)
    assert res.status_code == 404
    assert res.json()['detail'] == 'Post not found'