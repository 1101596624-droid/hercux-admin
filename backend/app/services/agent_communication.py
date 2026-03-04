"""
hercu-agent 通信服务
版本: 1.0.0
创建日期: 2026-02-10

职责：
1. 与 hercu-agent 服务通信
2. 同步标准文档
3. 请求 Agent 生成高质量模拟器代码
4. 获取 Agent 的美学评分
"""

import logging
import httpx
from typing import Dict, Any, Optional, List
from app.services.course_generation.standards_loader import get_standards_loader

logger = logging.getLogger(__name__)


class AgentCommunicationService:
    """
    Agent 通信服务

    负责与 hercu-agent 服务的所有通信
    """

    def __init__(self, agent_url: str = "http://localhost:8001"):
        self.agent_url = agent_url
        self.standards_loader = get_standards_loader()
        self.client = httpx.AsyncClient(timeout=60.0)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    async def ping_agent(self) -> bool:
        """检查 Agent 服务是否可用"""
        try:
            response = await self.client.get(f"{self.agent_url}/health")
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Agent service not available: {e}")
            return False

    async def sync_standards(self) -> Dict[str, Any]:
        """
        同步标准文档到 Agent

        Returns:
            同步结果
        """
        try:
            # 准备标准数据
            standards_data = {
                'simulator_standards': self.standards_loader.get_simulator_standards(),
                'course_standards': self.standards_loader.get_course_standards(),
                'canvas_config': self.standards_loader.get_canvas_config(),
                'visualization_elements': self.standards_loader.get_visualization_elements(),
                'color_systems': self.standards_loader.get_color_systems(),
                'visual_best_practices': self.standards_loader.get_visual_best_practices(),
                'interaction_types': self.standards_loader.get_interaction_types(),
                'api_reference': self.standards_loader.get_api_reference(),
                'animation_easing': self.standards_loader.get_animation_easing()
            }

            # 发送到 Agent
            response = await self.client.post(
                f"{self.agent_url}/api/standards/sync",
                json=standards_data
            )

            if response.status_code == 200:
                logger.info("Standards synced to Agent successfully")
                return {
                    'success': True,
                    'message': 'Standards synced successfully',
                    'synced_count': len(standards_data)
                }
            else:
                logger.error(f"Failed to sync standards: {response.text}")
                return {
                    'success': False,
                    'message': f'Sync failed: {response.status_code}',
                    'error': response.text
                }

        except Exception as e:
            logger.error(f"Failed to sync standards to Agent: {e}")
            return {
                'success': False,
                'message': str(e),
                'error': str(e)
            }

    async def generate_simulator_code(
        self,
        simulator_name: str,
        simulator_description: str,
        variables: List[Dict[str, Any]],
        subject: str,
        chapter_context: str = ""
    ) -> Dict[str, Any]:
        """
        请求 Agent 生成高质量模拟器代码

        Args:
            simulator_name: 模拟器名称
            simulator_description: 模拟器描述
            variables: 变量列表
            subject: 学科
            chapter_context: 章节上下文

        Returns:
            {
                'success': bool,
                'code': str,
                'quality_score': int,
                'metadata': dict
            }
        """
        try:
            # 获取学科配色方案
            color_scheme = self.standards_loader.get_subject_color_scheme(subject)

            # 获取推荐元素
            recommended_elements = self.standards_loader.get_recommended_elements_for_subject(subject)

            # 构建请求
            request_data = {
                'simulator_name': simulator_name,
                'simulator_description': simulator_description,
                'variables': variables,
                'subject': subject,
                'chapter_context': chapter_context,
                'color_scheme': color_scheme,
                'recommended_elements': recommended_elements[:5],  # 只传前5个
                'canvas_width': 1000,  # 学生端尺寸
                'canvas_height': 650
            }

            # 请求 Agent
            response = await self.client.post(
                f"{self.agent_url}/api/simulator/generate",
                json=request_data,
                timeout=120.0  # 生成代码可能需要较长时间
            )

            if response.status_code == 200:
                result = response.json()
                logger.info(f"Agent generated code for '{simulator_name}' (quality: {result.get('quality_score', 0)})")
                return {
                    'success': True,
                    'code': result['code'],
                    'quality_score': result.get('quality_score', 0),
                    'metadata': result.get('metadata', {})
                }
            else:
                logger.error(f"Agent code generation failed: {response.text}")
                return {
                    'success': False,
                    'error': response.text
                }

        except Exception as e:
            logger.error(f"Failed to request code from Agent: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def evaluate_aesthetic_quality(
        self,
        code: str,
        simulator_name: str,
        subject: str
    ) -> Dict[str, Any]:
        """
        请求 Agent 评估代码的美学质量

        Args:
            code: 模拟器代码
            simulator_name: 模拟器名称
            subject: 学科

        Returns:
            {
                'overall_score': int (0-100),
                'color_score': int (0-25),
                'composition_score': int (0-25),
                'animation_score': int (0-25),
                'refinement_score': int (0-25),
                'issues': List[str],
                'suggestions': List[str]
            }
        """
        try:
            # 构建请求
            request_data = {
                'code': code,
                'simulator_name': simulator_name,
                'subject': subject
            }

            # 请求 Agent
            response = await self.client.post(
                f"{self.agent_url}/api/simulator/evaluate",
                json=request_data,
                timeout=30.0
            )

            if response.status_code == 200:
                result = response.json()
                logger.info(f"Agent evaluated '{simulator_name}': {result['overall_score']}/100")
                return result
            else:
                logger.error(f"Agent evaluation failed: {response.text}")
                return {
                    'overall_score': 0,
                    'color_score': 0,
                    'composition_score': 0,
                    'animation_score': 0,
                    'refinement_score': 0,
                    'issues': [f'Evaluation failed: {response.text}'],
                    'suggestions': []
                }

        except Exception as e:
            logger.error(f"Failed to evaluate with Agent: {e}")
            return {
                'overall_score': 0,
                'color_score': 0,
                'composition_score': 0,
                'animation_score': 0,
                'refinement_score': 0,
                'issues': [str(e)],
                'suggestions': []
            }

    async def get_visualization_recommendations(
        self,
        subject: str,
        simulator_description: str
    ) -> Dict[str, Any]:
        """
        请求 Agent 推荐可视化方案

        Args:
            subject: 学科
            simulator_description: 模拟器描述

        Returns:
            推荐方案
        """
        try:
            request_data = {
                'subject': subject,
                'simulator_description': simulator_description
            }

            response = await self.client.post(
                f"{self.agent_url}/api/visualization/recommend",
                json=request_data,
                timeout=15.0
            )

            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Agent recommendation failed: {response.text}")
                return {
                    'recommended_elements': [],
                    'color_scheme': {},
                    'error': response.text
                }

        except Exception as e:
            logger.error(f"Failed to get recommendations from Agent: {e}")
            return {
                'recommended_elements': [],
                'color_scheme': {},
                'error': str(e)
            }


# ==================== 全局实例 ====================

_agent_service: Optional[AgentCommunicationService] = None


def get_agent_service(agent_url: str = "http://localhost:8001") -> AgentCommunicationService:
    """获取 Agent 通信服务的全局实例"""
    global _agent_service
    if _agent_service is None:
        _agent_service = AgentCommunicationService(agent_url)
    return _agent_service
