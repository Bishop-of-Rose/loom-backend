from typing import Any

from httpx2 import AsyncClient

from src.schemas import CommentResponse

async def test_create_root_comment_success(
    client: AsyncClient, init_auth_header: dict[str, str], created_post: dict[str, Any]
):
    payload = {'commented': created_post['id'], 'content': 'random content'}
    res = await client.post('/comments', headers=init_auth_header, json=payload)
    assert res.status_code == 201
    comment = res.json()
    CommentResponse.model_validate(comment)
    payload.update(comment)
    assert payload == comment

async def test_create_branch_comment_success(
    client: AsyncClient, init_auth_header: dict[str, str], created_root_comment: dict[str, Any]
):
    payload = {'replied': created_root_comment['id'], 'content': 'random content'}
    res = await client.post('/comments', headers=init_auth_header, json=payload)
    assert res.status_code == 201
    comment = res.json()
    CommentResponse.model_validate(comment)
    payload.update(comment)
    assert payload == comment

async def test_update_comment_success(
    client: AsyncClient, init_auth_header: dict[str, str], created_root_comment: dict[str, Any]
):
    payload = {'content': 'updated content'}
    res = await client.put(
        f'/comments/{created_root_comment['id']}', headers=init_auth_header, json=payload
    )
    assert res.status_code == 200
    comment = res.json()
    CommentResponse.model_validate(comment)
    payload.update(comment)
    assert payload == comment

async def test_delete_comment_success(
    client: AsyncClient, init_auth_header: dict[str, str], created_root_comment: dict[str, Any]
):
    res = await client.delete(
        f'/comments/{created_root_comment['id']}', headers=init_auth_header
    )
    assert res.status_code == 204
    res = await client.delete(
        f'/comments/{created_root_comment['id']}', headers=init_auth_header
    )
    assert res.status_code == 404