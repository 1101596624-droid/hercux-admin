"""
Template manager - extracted from service.py

Responsible for:
- Saving high-quality simulators as templates
- Saving high-quality chapters as templates
- Extracting canvas APIs and colors from code
"""

import re
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class TemplateManager:
    """
    Manages saving high-quality content as templates for future learning.
    """

    def __init__(self, db=None):
        self.db = db

    async def _save_simulator_as_template(
        self,
        code: str,
        spec: 'HTMLSimulatorSpec',
        quality_score: 'HTMLSimulatorQualityScore',
        subject: str,
        topic: str
    ):
        """
        保存高质量模拟器作为模板，用于future agent学习 (2026-02-11)
        使用独立事务，失败不影响主 session。
        """
        from app.models.models import SimulatorTemplate
        from sqlalchemy import select
        import re

        if not self.db:
            logger.warning("No database session available, cannot save template")
            return

        try:
            # 标准化topic名称
            topic_normalized = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fa5]+', '_', topic).lower().strip('_')

            # 检查是否已存在同名模板
            result = await self.db.execute(
                select(SimulatorTemplate).where(
                    SimulatorTemplate.subject == subject,
                    SimulatorTemplate.topic == topic_normalized
                )
            )
            existing = result.scalar_one_or_none()

            if existing and existing.quality_score >= quality_score.total_score:
                logger.info(f"Template already exists with score {existing.quality_score}, skipping save")
                return

            # 提取代码指标
            code_lines = len([l for l in code.split('\n') if l.strip()])
            has_setup_update = 'requestAnimationFrame' in code
            variable_count = 0

            # 提取视觉元素
            visual_elements = []
            if 'arc(' in code or 'circle' in code.lower():
                visual_elements.append('circles')
            if 'fillRect' in code or 'strokeRect' in code:
                visual_elements.append('rectangles')
            if 'fillText' in code or 'strokeText' in code:
                visual_elements.append('labels')
            if 'beginPath' in code and 'lineTo' in code:
                visual_elements.append('paths')

            # 构建元数据
            metadata = {
                "common_apis": self._extract_canvas_apis(code),
                "color_scheme": self._extract_colors(code),
                "animation_patterns": [],
                "interaction_types": [],
                "structure_insights": f"Score: {quality_score.total_score}/100"
            }

            if 'requestAnimationFrame' in code:
                metadata["animation_patterns"].append("requestAnimationFrame")
            if 'addEventListener' in code:
                if "'mousemove'" in code or '"mousemove"' in code:
                    metadata["interaction_types"].append("mouse_tracking")
                if "'click'" in code or '"click"' in code:
                    metadata["interaction_types"].append("mouse_click")
            if 'type="range"' in code:
                metadata["interaction_types"].append("slider_control")

            # 创建或更新模板
            if existing:
                existing.code = code
                existing.quality_score = quality_score.total_score
                existing.line_count = code_lines
                existing.variable_count = variable_count
                existing.has_setup_update = has_setup_update
                existing.visual_elements = visual_elements
                existing.template_meta = metadata
                existing.template_metadata = metadata
                logger.info(f"Updated template {subject}/{topic_normalized} with improved quality score")
            else:
                new_template = SimulatorTemplate(
                    subject=subject,
                    topic=topic_normalized,
                    code=code,
                    quality_score=quality_score.total_score,
                    line_count=code_lines,
                    variable_count=variable_count,
                    has_setup_update=has_setup_update,
                    visual_elements=visual_elements,
                    template_meta=metadata,
                    template_metadata=metadata,
                    status='pending'
                )
                self.db.add(new_template)
                logger.info(f"Created new template {subject}/{topic_normalized} with score {quality_score.total_score}")

            await self.db.commit()

        except Exception as e:
            logger.warning(f"Failed to save simulator template (non-fatal): {e}")
            try:
                await self.db.rollback()
            except Exception:
                pass


    def _extract_canvas_apis(self, code: str) -> list:
        """提取代码中使用的Canvas API"""
        apis = []
        common_apis = [
            'fillRect', 'strokeRect', 'clearRect', 'arc', 'beginPath', 'closePath',
            'moveTo', 'lineTo', 'stroke', 'fill', 'fillText', 'strokeText',
            'save', 'restore', 'translate', 'rotate', 'scale'
        ]
        for api in common_apis:
            if api + '(' in code:
                apis.append(api)
        return apis[:15]  # 最多15个


    def _extract_colors(self, code: str) -> list:
        """提取代码中使用的颜色值"""
        import re
        # 匹配 #RRGGBB 格式
        hex_colors = re.findall(r'#[0-9A-Fa-f]{6}', code)
        # 匹配 rgb() 格式
        rgb_colors = re.findall(r'rgb\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*\)', code)
        # 去重并限制数量
        all_colors = list(set(hex_colors + rgb_colors))
        return all_colors[:8]  # 最多8个颜色


    async def _save_chapter_as_template(
        self,
        chapter: Dict[str, Any],
        quality_score: 'ChapterQualityScore',
        subject: str,
        topic: str
    ):
        """
        保存高质量章节作为模板，用于future agent学习 (2026-02-11: Phase 3)

        Args:
            chapter: 章节内容字典
            quality_score: ChapterQualityScore对象
            subject: 学科 (如 "physics", "mathematics")
            topic: 主题 (章节标题)
        """
        from app.services.learning import UnifiedTemplateService, ChapterScorer
        import re

        if not self.db:
            logger.warning("No database session available, cannot save chapter template")
            return

        try:
            template_service = UnifiedTemplateService(self.db)
            scorer = ChapterScorer()

            # 标准化topic名称 (移除特殊字符，转为小写下划线)
            topic_normalized = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fa5]+', '_', topic).lower().strip('_')

            # 提取章节元数据用于学习
            metadata = scorer.extract_metadata(chapter)

            # 添加额外的学习insights
            metadata['quality_breakdown'] = {
                'depth_score': quality_score.depth_score,
                'structure_score': quality_score.structure_score,
                'visual_score': quality_score.visual_score,
                'teaching_score': quality_score.teaching_score,
                'simulator_score': quality_score.simulator_score,
            }

            # 保存评分详情
            score_breakdown = {
                'depth_score': quality_score.depth_score,
                'structure_score': quality_score.structure_score,
                'visual_score': quality_score.visual_score,
                'teaching_score': quality_score.teaching_score,
                'simulator_score': quality_score.simulator_score,
            }

            # 保存为模板
            await template_service.save_as_template(
                template_type='chapter_content',
                subject=subject,
                topic=topic_normalized,
                content=chapter,  # 完整章节内容
                quality_score=quality_score.total_score,
                score_breakdown=score_breakdown,
                metadata=metadata,
                difficulty_level=chapter.get('complexity_level', 'standard')
            )

            logger.info(f"Chapter template saved: {subject}/{topic_normalized} (score: {quality_score.total_score:.1f})")

        except Exception as e:
            logger.error(f"Failed to save chapter as template: {e}")
            import traceback
            logger.error(traceback.format_exc())

