"""
Gemini AI Service - 图片生成服务
使用 Gemini API 生成教育类图片和图表
支持 OpenAI 兼容格式的中转 API (如 hiapi.online)
"""
import aiohttp
import base64
import logging
import json
import ssl
import certifi
from typing import Optional
from app.core.config import settings

logger = logging.getLogger(__name__)


# 创建使用 certifi 证书的 SSL 上下文
def get_ssl_context():
    """获取配置了 certifi CA 证书的 SSL 上下文"""
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    return ssl_context


class GeminiService:
    """Gemini API 图片生成服务"""

    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.base_url = settings.GEMINI_BASE_URL.rstrip('/')
        # 图片生成模型 - 从配置读取
        self.image_model = settings.GEMINI_MODEL

    async def generate_image(
        self,
        prompt: str,
        style: str = "educational",
        size: str = "1024x1024"
    ) -> Optional[bytes]:
        """
        生成图片

        Args:
            prompt: 图片描述
            style: 风格 (educational, diagram, illustration)
            size: 尺寸

        Returns:
            图片二进制数据，失败返回 None
        """
        if not self.api_key:
            logger.warning("Gemini API key not configured")
            return None

        # 构建增强的 prompt
        enhanced_prompt = self._build_enhanced_prompt(prompt, style)

        # 使用固定的模型生成图片
        logger.info(f"Generating image with model: {self.image_model}")
        result = await self._try_openai_image_format(enhanced_prompt, size, self.image_model)
        if result:
            return result

        # 如果失败，尝试 chat completion 方式
        logger.warning(f"OpenAI format failed, trying chat completion format")
        result = await self._try_chat_image_format(enhanced_prompt)
        if result:
            return result

        logger.error("All image generation methods failed")
        return None

    async def _try_openai_image_format(self, prompt: str, size: str, model: str) -> Optional[bytes]:
        """尝试 OpenAI 图片生成格式"""
        try:
            async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=get_ssl_context())) as session:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }

                payload = {
                    "model": model,
                    "prompt": prompt,
                    "n": 1,
                    "size": size,
                    "response_format": "b64_json"
                }

                url = f"{self.base_url}/images/generations"
                logger.info(f"POST {url} with model={model}")

                async with session.post(
                    url,
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=180)
                ) as response:
                    response_text = await response.text()
                    logger.info(f"Response status: {response.status}, length: {len(response_text)}")

                    if response.status == 200:
                        try:
                            data = json.loads(response_text)
                            if data.get("data") and len(data["data"]) > 0:
                                # 尝试获取 b64_json
                                b64_image = data["data"][0].get("b64_json")
                                if b64_image:
                                    logger.info(f"Image generated successfully with model {model} (b64_json)")
                                    return base64.b64decode(b64_image)

                                # 尝试获取 url 并下载
                                image_url = data["data"][0].get("url")
                                if image_url:
                                    logger.info(f"Got image URL, downloading...")
                                    return await self._download_image(image_url)
                        except json.JSONDecodeError as e:
                            logger.warning(f"Failed to parse response JSON: {e}")
                    else:
                        logger.warning(f"Image generation failed: {response.status} - {response_text[:500]}")

        except aiohttp.ClientError as e:
            logger.warning(f"HTTP error with model {model}: {e}")
        except Exception as e:
            logger.warning(f"Error with model {model}: {e}")

        return None

    async def _try_chat_image_format(self, prompt: str) -> Optional[bytes]:
        """尝试通过 chat completion 生成图片"""
        try:
            async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=get_ssl_context())) as session:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }

                # 使用固定的模型
                payload = {
                    "model": self.image_model,
                    "messages": [
                        {
                            "role": "user",
                            "content": f"Generate an image: {prompt}"
                        }
                    ],
                    "max_tokens": 16384
                }

                url = f"{self.base_url}/chat/completions"
                logger.info(f"Trying chat completion format: {url}")

                async with session.post(
                    url,
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=180)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        # 检查响应中是否有图片
                        choices = data.get("choices", [])
                        if choices:
                            message = choices[0].get("message", {})
                            content = message.get("content", "")

                            # 检查是否有 base64 图片数据
                            if "data:image" in content or content.startswith("/9j/"):
                                # 提取 base64 数据
                                if "base64," in content:
                                    b64_data = content.split("base64,")[1].split('"')[0]
                                else:
                                    b64_data = content
                                try:
                                    return base64.b64decode(b64_data)
                                except:
                                    pass
                    else:
                        error_text = await response.text()
                        logger.warning(f"Chat format failed: {response.status} - {error_text[:300]}")

        except Exception as e:
            logger.warning(f"Chat format error: {e}")

        return None

    async def _download_image(self, url: str) -> Optional[bytes]:
        """下载图片"""
        try:
            async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=get_ssl_context())) as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=60)) as response:
                    if response.status == 200:
                        return await response.read()
        except Exception as e:
            logger.error(f"Failed to download image: {e}")
        return None

    async def generate_diagram(
        self,
        diagram_spec: dict,
        course_title: str,
        lesson_title: str
    ) -> Optional[bytes]:
        """
        根据图表规格生成图片

        Args:
            diagram_spec: 图表规格
            course_title: 课程标题
            lesson_title: 课时标题

        Returns:
            图片二进制数据
        """
        # 从 diagram_spec 构建 prompt
        diagram_type = diagram_spec.get("type", "static_diagram")
        description = diagram_spec.get("description", "")
        annotations = diagram_spec.get("annotations", [])
        design_notes = diagram_spec.get("design_notes", "")

        prompt = f"""为教育课程"{course_title}"的"{lesson_title}"课时创建一张{self._get_diagram_type_name(diagram_type)}。

图表描述：{description}

"""
        if annotations:
            prompt += "标注信息：\n"
            for ann in annotations:
                prompt += f"- {ann.get('position', '')}: {ann.get('text', '')}\n"

        if design_notes:
            prompt += f"\n设计说明：{design_notes}"

        return await self.generate_image(prompt, style="diagram")

    def _build_enhanced_prompt(self, prompt: str, style: str) -> str:
        """构建增强的图片生成 prompt"""
        style_prefixes = {
            "educational": "Create a clean, professional educational illustration. Use clear colors and simple shapes. ",
            "diagram": "Create a clear, labeled diagram with professional styling. Use a white background, clean lines, and readable text. ",
            "illustration": "Create a modern, flat-style illustration suitable for educational content. ",
            "flowchart": "Create a professional flowchart with clear boxes, arrows, and labels. Use a clean white background. ",
            "infographic": "Create an informative infographic with icons, charts, and clear visual hierarchy. "
        }

        prefix = style_prefixes.get(style, style_prefixes["educational"])

        # 添加通用的质量要求
        suffix = " High quality, suitable for educational materials, no text watermarks."

        return f"{prefix}{prompt}{suffix}"

    def _get_diagram_type_name(self, diagram_type: str) -> str:
        """获取图表类型的中文名称"""
        type_names = {
            "static_diagram": "静态图表",
            "flowchart": "流程图",
            "line_chart": "折线图",
            "analysis_diagram": "分析图",
            "pyramid": "金字塔图",
            "comparison": "对比图",
            "mind_map": "思维导图",
            "timeline": "时间线图"
        }
        return type_names.get(diagram_type, "图表")


# 全局服务实例
gemini_service = GeminiService()
