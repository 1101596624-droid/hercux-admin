"""
TTS API - 使用 Edge TTS 生成高质量语音
"""
import edge_tts
import hashlib
import os
import asyncio
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

# 音频缓存目录
AUDIO_CACHE_DIR = "/tmp/hercu_tts_cache"
os.makedirs(AUDIO_CACHE_DIR, exist_ok=True)

# 可用的中文语音
VOICES = {
    "xiaoxiao": "zh-CN-XiaoxiaoNeural",      # 女声，温柔自然（推荐）
    "yunxi": "zh-CN-YunxiNeural",            # 男声，年轻活力
    "yunyang": "zh-CN-YunyangNeural",        # 男声，新闻播报风格
    "xiaoyi": "zh-CN-XiaoyiNeural",          # 女声，活泼
    "yunfeng": "zh-CN-YunfengNeural",        # 男声，成熟稳重
    "xiaoxuan": "zh-CN-XiaoxuanNeural",      # 女声，甜美
}

DEFAULT_VOICE = "xiaoxiao"


class TTSRequest(BaseModel):
    text: str
    voice: Optional[str] = DEFAULT_VOICE
    rate: Optional[str] = "+0%"  # 语速调整，如 "+10%", "-10%"
    pitch: Optional[str] = "+0Hz"  # 音调调整


@router.get("/voices")
async def list_voices():
    """获取可用的语音列表"""
    return {
        "voices": [
            {"id": k, "name": v, "description": get_voice_description(k)}
            for k, v in VOICES.items()
        ],
        "default": DEFAULT_VOICE
    }


def get_voice_description(voice_id: str) -> str:
    descriptions = {
        "xiaoxiao": "晓晓 - 女声，温柔自然，适合讲解",
        "yunxi": "云希 - 男声，年轻活力",
        "yunyang": "云扬 - 男声，新闻播报风格",
        "xiaoyi": "晓伊 - 女声，活泼可爱",
        "yunfeng": "云枫 - 男声，成熟稳重",
        "xiaoxuan": "晓萱 - 女声，甜美温柔",
    }
    return descriptions.get(voice_id, "")


@router.post("/generate")
async def generate_tts(request: TTSRequest):
    """生成 TTS 音频并返回音频文件"""
    voice_name = VOICES.get(request.voice, VOICES[DEFAULT_VOICE])

    # 生成缓存 key
    cache_key = hashlib.md5(
        f"{request.text}_{voice_name}_{request.rate}_{request.pitch}".encode()
    ).hexdigest()
    cache_path = os.path.join(AUDIO_CACHE_DIR, f"{cache_key}.mp3")

    # 检查缓存
    if os.path.exists(cache_path):
        return FileResponse(
            cache_path,
            media_type="audio/mpeg",
            headers={"X-Cache": "HIT"}
        )

    try:
        # 生成音频
        communicate = edge_tts.Communicate(
            request.text,
            voice_name,
            rate=request.rate,
            pitch=request.pitch
        )
        await communicate.save(cache_path)

        return FileResponse(
            cache_path,
            media_type="audio/mpeg",
            headers={"X-Cache": "MISS"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS 生成失败: {str(e)}")


@router.get("/generate")
async def generate_tts_get(
    text: str = Query(..., description="要转换的文本"),
    voice: str = Query(DEFAULT_VOICE, description="语音ID"),
    rate: str = Query("+0%", description="语速调整"),
    pitch: str = Query("+0Hz", description="音调调整")
):
    """GET 方式生成 TTS 音频（方便前端直接使用 audio src）"""
    request = TTSRequest(text=text, voice=voice, rate=rate, pitch=pitch)
    return await generate_tts(request)


@router.delete("/cache")
async def clear_cache():
    """清理 TTS 缓存"""
    import shutil
    try:
        shutil.rmtree(AUDIO_CACHE_DIR)
        os.makedirs(AUDIO_CACHE_DIR, exist_ok=True)
        return {"success": True, "message": "缓存已清理"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"清理缓存失败: {str(e)}")
