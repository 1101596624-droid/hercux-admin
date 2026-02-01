"""
测试端点 - 用于调试
"""

from fastapi import APIRouter

router = APIRouter(tags=["Test"])


@router.get("/ping")
async def ping():
    """简单的 ping 端点"""
    return {"message": "pong"}


@router.post("/echo")
async def echo(data: dict):
    """回显端点"""
    return {"received": data}
