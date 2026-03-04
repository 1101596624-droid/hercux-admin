"""
Subject classifier - extracted from service.py

Responsible for:
- Course subject detection via preset DB matching
- LLM fallback classification
- Auto-classify and update course
"""

import json
import logging
from typing import Dict, Any, Optional

from .models import CourseOutline
from .standards_loader import get_standards_loader

logger = logging.getLogger(__name__)


class SubjectClassifier:
    """
    Subject classifier

    Uses preset subject DB for matching, falls back to LLM.
    """

    def __init__(self, llm_service=None, standards_loader=None):
        self.llm_service = llm_service
        self.standards_loader = standards_loader or get_standards_loader()

    SUBJECT_DB = {
        # ---- 中小学理科 ----
        'mathematics': {
            'name': '数学', 'is_science': True,
            'terms': ['数学', '算术', '几何', '代数', '高等数学', '线性代数',
                      '概率论', '数理统计', '微积分', '数学分析', '离散数学',
                      '解析几何', '初等数学']
        },
        'physics': {
            'name': '物理', 'is_science': True,
            'terms': ['物理', '力学', '电磁', '光学', '热学', '声学',
                      '大学物理', '理论力学', '材料力学', '量子力学',
                      '电动力学', '热力学与统计物理', '天文', '天文学']
        },
        'chemistry': {
            'name': '化学', 'is_science': True,
            'terms': ['化学', '有机化学', '无机化学', '分析化学', '物理化学',
                      '大学化学', '结构化学', '高分子化学']
        },
        'biology': {
            'name': '生物', 'is_science': True,
            'terms': ['生物', '生命科学', '生物化学', '分子生物学',
                      '细胞生物学', '遗传学', '生态学', '微生物学',
                      '生理学', '植物学', '动物学']
        },
        'science': {
            'name': '科学', 'is_science': True,
            'terms': ['科学', '自然科学', '小学科学']
        },
        'information_technology': {
            'name': '信息技术', 'is_science': True,
            'terms': ['信息技术', '信息科技', '计算机', '编程', '程序设计',
                      '计算机基础', '数据结构', '算法', '操作系统',
                      '计算机网络', '数据库', '软件工程', '人工智能',
                      'python', 'java', 'c语言']
        },
        # ---- 中小学文科 ----
        'chinese': {
            'name': '语文', 'is_science': False,
            'terms': ['语文', '阅读', '作文', '写作', '文学', '古文',
                      '诗词', '名著', '大学语文']
        },
        'english': {
            'name': '英语', 'is_science': False,
            'terms': ['英语', '大学英语', '英文', '外语', '日语', '法语',
                      '德语', '俄语', '韩语', '西班牙语', '翻译']
        },
        'history': {
            'name': '历史', 'is_science': False,
            'terms': ['历史', '中国近现代史', '世界史', '中国史',
                      '中国近现代史纲要']
        },
        'geography': {
            'name': '地理', 'is_science': False,
            'terms': ['地理', '人文地理', '自然地理', '地球科学']
        },
        'politics': {
            'name': '道德与法治', 'is_science': False,
            'terms': ['政治', '道法', '道德与法治', '思想政治', '思想品德',
                      '思想道德', '品德与社会', '品德与生活',
                      '马克思主义基本原理', '毛泽东思想', '形势与政策',
                      '中国特色社会主义', '思想道德与法治']
        },
        'music': {
            'name': '音乐', 'is_science': False,
            'terms': ['音乐', '乐理', '声乐', '器乐', '合唱', '作曲']
        },
        'art': {
            'name': '美术', 'is_science': False,
            'terms': ['美术', '绘画', '书法', '素描', '色彩', '雕塑',
                      '摄影', '艺术']
        },
        'pe': {
            'name': '体育', 'is_science': False,
            'terms': ['体育', '体育与健康', '大学体育', '健身', '田径',
                      '篮球', '足球', '游泳', '武术']
        },
        # ---- 大学通识/必修 ----
        'military': {
            'name': '军事理论', 'is_science': False,
            'terms': ['军事理论', '军事', '国防教育']
        },
        'engineering': {
            'name': '工程', 'is_science': True,
            'terms': ['工程', '机械', '电气', '电子', '自动化', '通信',
                      '土木', '建筑', '材料', '电路', '信号与系统',
                      '自动控制', '模拟电子', '数字电子']
        },
        'medicine': {
            'name': '医学', 'is_science': True,
            'terms': ['医学', '解剖', '药理', '临床', '护理', '病理',
                      '药学', '中医', '诊断学']
        },
        'economics': {
            'name': '经济学', 'is_science': False,
            'terms': ['经济', '金融', '会计', '财务', '审计', '税收',
                      '微观经济', '宏观经济', '国际贸易']
        },
        'law': {
            'name': '法学', 'is_science': False,
            'terms': ['法律', '法学', '宪法', '民法', '刑法', '行政法',
                      '国际法', '诉讼', '司法']
        },
        'management': {
            'name': '管理学', 'is_science': False,
            'terms': ['管理', '管理学', '营销', '人力资源', '项目管理',
                      '企业管理', '工商管理', '行政管理']
        },
        'psychology': {
            'name': '心理学', 'is_science': False,
            'terms': ['心理', '心理学', '心理健康', '教育心理']
        },
        'education': {
            'name': '教育学', 'is_science': False,
            'terms': ['教育', '教育学', '教学法', '课程论']
        },
        'philosophy': {
            'name': '哲学', 'is_science': False,
            'terms': ['哲学', '伦理', '逻辑学', '美学']
        },
        'agriculture': {
            'name': '农学', 'is_science': True,
            'terms': ['农学', '农业', '种植', '养殖', '园艺', '畜牧',
                      '兽医', '水产', '土壤学']
        },
        'sociology': {
            'name': '社会学', 'is_science': False,
            'terms': ['社会学', '社会工作', '社会保障']
        },
        'journalism': {
            'name': '新闻传播', 'is_science': False,
            'terms': ['新闻', '传播', '广告', '媒体', '出版']
        },
    }

    async def detect_course_subject(self, course_title: str, outline: Optional[CourseOutline] = None) -> Dict[str, Any]:
        """
        识别课程所属科目

        优先使用预置科目数据库匹配，匹配失败时调用 LLM 兜底判断。

        Returns:
            {
                'subject_id': 科目ID,
                'subject_name': 科目中文名,
                'is_science': 是否理科（决定是否生成模拟器）,
                'confidence': 置信度 (0-1),
                'color_scheme': 配色方案,
                'visualization_elements': 可视化元素
            }
        """
        # 收集文本
        text = course_title.lower()
        if outline:
            text += " " + outline.description.lower()
            text += " " + " ".join(outline.core_concepts).lower()
            for ch in outline.chapters[:5]:
                text += " " + ch.title.lower()

        # === 阶段1：预置科目库匹配 ===
        scores = {}
        for subject_id, info in self.SUBJECT_DB.items():
            score = sum(1 for term in info['terms'] if term in text)
            if score > 0:
                scores[subject_id] = score

        if scores:
            best_id = max(scores, key=scores.get)
            best_info = self.SUBJECT_DB[best_id]
            total_terms = len(best_info['terms'])
            confidence = min(1.0, scores[best_id] / max(1, total_terms * 0.3))

            logger.info(f"Subject matched: '{best_id}' for '{course_title}' (score={scores[best_id]}, confidence={confidence:.2f})")
            return {
                'subject_id': best_id,
                'subject_name': best_info['name'],
                'is_science': best_info['is_science'],
                'confidence': confidence,
                'color_scheme': self.standards_loader.get_subject_color_scheme(best_id),
                'visualization_elements': self.standards_loader.get_recommended_elements_for_subject(best_id)
            }

        # === 阶段2：LLM 兜底分类 ===
        logger.info(f"No subject matched for '{course_title}', falling back to LLM classification")
        try:
            context = f"课程标题：{course_title}"
            if outline:
                chapter_titles = [ch.title for ch in outline.chapters[:6]]
                context += f"\n章节：{', '.join(chapter_titles)}"

            prompt = f"""{context}

请判断这门课属于什么科目，以及是否属于理科（理科课程会生成交互式模拟器，如物理实验、化学反应、数学图形等）。

用JSON回答：
{{"subject_id": "英文ID", "subject_name": "中文科目名", "is_science": true或false}}
只返回JSON。"""

            response = await self.llm_service.generate_raw_response(
                prompt=prompt,
                system_prompt="你是学科分类助手，只返回JSON。",
                temperature=0.1,
                max_tokens=150
            )

            # 解析JSON
            json_str = response.strip()
            if '```' in json_str:
                json_str = json_str.split('```')[1].replace('json', '', 1).strip()
            if '{' in json_str:
                json_str = json_str[json_str.index('{'):json_str.rindex('}') + 1]

            data = json.loads(json_str)
            subject_id = data.get('subject_id', 'general')
            subject_name = data.get('subject_name', '通用')
            is_science = data.get('is_science', False)

            logger.info(f"LLM classified '{course_title}' as '{subject_name}' (is_science={is_science})")
            return {
                'subject_id': subject_id,
                'subject_name': subject_name,
                'is_science': is_science,
                'confidence': 0.7,
                'color_scheme': self.standards_loader.get_subject_color_scheme(subject_id),
                'visualization_elements': self.standards_loader.get_recommended_elements_for_subject(subject_id)
            }

        except Exception as e:
            logger.error(f"LLM classification failed: {e}")
            return {
                'subject_id': 'general',
                'subject_name': '通用',
                'is_science': False,
                'confidence': 0.0,
                'color_scheme': self.standards_loader.get_subject_color_scheme('physics'),
                'visualization_elements': self.standards_loader.get_recommended_elements_for_subject('physics')
            }


    async def auto_classify_and_update_course(
        self,
        course_id: str,
        course_title: str,
        outline: Optional[CourseOutline] = None
    ) -> Dict[str, Any]:
        """
        自动识别课程学科并更新到数据库

        Args:
            course_id: 课程ID
            course_title: 课程标题
            outline: 课程大纲（可选）

        Returns:
            分类结果字典
        """
        # 识别学科
        classification = await self.detect_course_subject(course_title, outline)

        # TODO: 将分类结果保存到数据库
        # 示例代码（需要根据实际数据库结构调整）:
        # await db.update_course_subject(course_id, classification['subject_id'])

        logger.info(f"Course '{course_id}' classified as '{classification['subject_name']}' (confidence: {classification['confidence']:.2f})")

        return classification

