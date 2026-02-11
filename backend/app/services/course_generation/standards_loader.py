"""
标准加载器 - 负责加载和管理YAML标准文档
版本: 1.0.0
创建日期: 2026-02-10
"""

import os
import yaml
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from functools import lru_cache
from pathlib import Path

logger = logging.getLogger(__name__)


class StandardsLoader:
    """
    标准加载器（单例模式）

    职责：
    1. 从 YAML 文件加载所有标准文档
    2. 提供标准查询接口
    3. 缓存标准数据（LRU缓存）
    4. 标准版本管理
    """

    _instance = None
    _initialized = False

    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super(StandardsLoader, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """初始化标准加载器"""
        if StandardsLoader._initialized:
            return

        # 标准文件目录
        self.standards_dir = Path(__file__).parent / "standards"

        # 标准文档缓存
        self._cache: Dict[str, Dict[str, Any]] = {}

        # 加载时间戳
        self._load_timestamps: Dict[str, datetime] = {}

        # 标记为已初始化
        StandardsLoader._initialized = True

        logger.info(f"StandardsLoader initialized, standards_dir: {self.standards_dir}")

    def _load_yaml_file(self, filename: str) -> Dict[str, Any]:
        """
        加载单个YAML文件

        Args:
            filename: YAML文件名（不含路径）

        Returns:
            解析后的YAML内容（字典）
        """
        file_path = self.standards_dir / filename

        if not file_path.exists():
            logger.error(f"Standard file not found: {file_path}")
            raise FileNotFoundError(f"Standard file not found: {filename}")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)

            self._load_timestamps[filename] = datetime.now()
            logger.info(f"Loaded standard: {filename}")
            return data

        except yaml.YAMLError as e:
            logger.error(f"Failed to parse YAML file {filename}: {e}")
            raise ValueError(f"Invalid YAML format in {filename}: {e}")

        except Exception as e:
            logger.error(f"Failed to load {filename}: {e}")
            raise

    @lru_cache(maxsize=32)
    def get_standard(self, standard_name: str) -> Dict[str, Any]:
        """
        获取标准文档（带LRU缓存）

        Args:
            standard_name: 标准名称（不含.yaml后缀）
                          如: "simulator_standards", "visualization_elements"

        Returns:
            标准文档内容（字典）
        """
        filename = f"{standard_name}.yaml"

        # 检查缓存
        if filename in self._cache:
            return self._cache[filename]

        # 加载并缓存
        data = self._load_yaml_file(filename)
        self._cache[filename] = data

        return data

    def reload_standard(self, standard_name: str) -> Dict[str, Any]:
        """
        重新加载指定标准（清除缓存）

        Args:
            standard_name: 标准名称

        Returns:
            重新加载的标准内容
        """
        filename = f"{standard_name}.yaml"

        # 清除缓存
        if filename in self._cache:
            del self._cache[filename]

        # 清除 LRU 缓存
        self.get_standard.cache_clear()

        # 重新加载
        return self.get_standard(standard_name)

    def reload_all_standards(self):
        """重新加载所有标准文档"""
        logger.info("Reloading all standards...")

        self._cache.clear()
        self.get_standard.cache_clear()

        # 重新加载所有已知标准
        standard_names = [
            "course_standards",
            "simulator_standards",
            "canvas_config",
            "visualization_elements",
            "color_systems",
            "visual_best_practices",
            "interaction_types",
            "api_reference",
            "animation_easing"
        ]

        for name in standard_names:
            try:
                self.get_standard(name)
            except Exception as e:
                logger.warning(f"Failed to reload {name}: {e}")

        logger.info("All standards reloaded")

    # ==================== 便捷查询方法 ====================

    def get_simulator_standards(self) -> Dict[str, Any]:
        """获取模拟器质量标准"""
        return self.get_standard("simulator_standards")

    def get_course_standards(self) -> Dict[str, Any]:
        """获取课程质量标准"""
        return self.get_standard("course_standards")

    def get_canvas_config(self) -> Dict[str, Any]:
        """获取画布配置"""
        return self.get_standard("canvas_config")

    def get_visualization_elements(self) -> Dict[str, Any]:
        """获取可视化元素库"""
        return self.get_standard("visualization_elements")

    def get_color_systems(self) -> Dict[str, Any]:
        """获取学科颜色系统"""
        return self.get_standard("color_systems")

    def get_visual_best_practices(self) -> Dict[str, Any]:
        """获取视觉最佳实践"""
        return self.get_standard("visual_best_practices")

    def get_interaction_types(self) -> Dict[str, Any]:
        """获取交互类型库"""
        return self.get_standard("interaction_types")

    def get_api_reference(self) -> Dict[str, Any]:
        """获取API参考文档"""
        return self.get_standard("api_reference")

    def get_animation_easing(self) -> Dict[str, Any]:
        """获取动画缓动函数库"""
        return self.get_standard("animation_easing")

    # ==================== 查询辅助方法 ====================

    def get_subject_color_scheme(self, subject: str) -> Optional[Dict[str, Any]]:
        """
        获取指定学科的颜色方案

        Args:
            subject: 学科名称（physics, chemistry, biology, mathematics, etc.）

        Returns:
            学科颜色方案（包含 name, philosophy, primary, secondary, accent, use_cases等）
        """
        color_systems_data = self.get_color_systems()

        # 新格式：color_systems是字典，key为学科ID
        color_systems = color_systems_data.get('color_systems', {})

        if subject in color_systems:
            scheme = color_systems[subject]
            # 添加id字段以保持一致性
            scheme['id'] = subject
            return scheme

        # 未找到，返回默认颜色方案（physics）
        logger.warning(f"Color scheme for '{subject}' not found, using default (physics)")
        default_scheme = color_systems.get('physics', {})
        if default_scheme:
            default_scheme['id'] = 'physics'
        return default_scheme

    def get_visualization_element(self, element_id: str) -> Optional[Dict[str, Any]]:
        """
        获取指定可视化元素的定义

        Args:
            element_id: 元素ID（如 "circles", "rectangles", "curves"）

        Returns:
            元素定义（包含 name, description, apis, use_cases, best_practices）
        """
        viz_elements = self.get_visualization_elements()
        elements = viz_elements.get('visualization_elements', [])

        for elem in elements:
            if elem.get('id') == element_id:
                return elem

        logger.warning(f"Visualization element '{element_id}' not found")
        return None

    def get_interaction_type(self, type_id: str) -> Optional[Dict[str, Any]]:
        """
        获取指定交互类型的定义

        Args:
            type_id: 交互类型ID（如 "click", "drag", "hover"）

        Returns:
            交互类型定义
        """
        interaction_types = self.get_interaction_types()
        types = interaction_types.get('interaction_types', [])

        for itype in types:
            if itype.get('id') == type_id:
                return itype

        logger.warning(f"Interaction type '{type_id}' not found")
        return None

    def get_easing_function(self, easing_id: str) -> Optional[Dict[str, Any]]:
        """
        获取指定缓动函数的定义

        Args:
            easing_id: 缓动函数ID（如 "easeInOut", "easeOutBack"）

        Returns:
            缓动函数定义（包含公式、代码、使用场景）
        """
        easing_funcs = self.get_animation_easing()
        functions = easing_funcs.get('easing_functions', [])

        for func in functions:
            if func.get('id') == easing_id:
                return func

        logger.warning(f"Easing function '{easing_id}' not found")
        return None

    def get_recommended_elements_for_subject(self, subject: str) -> List[str]:
        """
        获取推荐给指定学科使用的可视化元素

        Args:
            subject: 学科名称

        Returns:
            推荐元素ID列表
        """
        viz_elements = self.get_visualization_elements()
        combos = viz_elements.get('recommended_combinations', [])

        for combo in combos:
            # 将学科名称映射到推荐组合
            combo_name = combo.get('name', '')
            if subject in combo_name or combo_name in subject:
                return combo.get('elements', [])

        # 默认返回基础组合
        return ['circles', 'rectangles', 'lines', 'labels', 'position_animation']

    # ==================== 版本管理 ====================

    def get_standard_version(self, standard_name: str) -> str:
        """获取标准文档的版本号"""
        data = self.get_standard(standard_name)
        return data.get('version', 'unknown')

    def get_all_versions(self) -> Dict[str, str]:
        """获取所有标准文档的版本号"""
        standard_names = [
            "course_standards",
            "simulator_standards",
            "canvas_config",
            "visualization_elements",
            "color_systems",
            "visual_best_practices",
            "interaction_types",
            "api_reference",
            "animation_easing"
        ]

        versions = {}
        for name in standard_names:
            try:
                versions[name] = self.get_standard_version(name)
            except Exception as e:
                logger.warning(f"Failed to get version for {name}: {e}")
                versions[name] = "error"

        return versions

    def check_version_consistency(self) -> bool:
        """检查所有标准文档的版本是否一致"""
        versions = self.get_all_versions()
        unique_versions = set(v for v in versions.values() if v != "error")

        if len(unique_versions) > 1:
            logger.warning(f"Version inconsistency detected: {versions}")
            return False

        return True

    # ==================== 诊断工具 ====================

    def get_load_info(self) -> Dict[str, Any]:
        """获取加载信息（用于诊断）"""
        return {
            'standards_dir': str(self.standards_dir),
            'cached_files': list(self._cache.keys()),
            'load_timestamps': {
                filename: ts.isoformat()
                for filename, ts in self._load_timestamps.items()
            },
            'versions': self.get_all_versions(),
            'version_consistent': self.check_version_consistency()
        }

    def validate_all_standards(self) -> Dict[str, Any]:
        """验证所有标准文档的完整性"""
        results = {}

        standard_names = [
            "course_standards",
            "simulator_standards",
            "canvas_config",
            "visualization_elements",
            "color_systems",
            "visual_best_practices",
            "interaction_types",
            "api_reference",
            "animation_easing"
        ]

        for name in standard_names:
            try:
                data = self.get_standard(name)

                # 基本验证
                has_version = 'version' in data
                has_content = len(data) > 1  # 不只有version字段

                results[name] = {
                    'status': 'ok' if (has_version and has_content) else 'warning',
                    'has_version': has_version,
                    'field_count': len(data),
                    'version': data.get('version', 'missing')
                }

            except Exception as e:
                results[name] = {
                    'status': 'error',
                    'error': str(e)
                }

        return results


# ==================== 全局实例 ====================

# 创建全局单例实例
_standards_loader = StandardsLoader()


def get_standards_loader() -> StandardsLoader:
    """获取标准加载器的全局实例"""
    return _standards_loader


# ==================== 便捷函数 ====================

def get_simulator_standards() -> Dict[str, Any]:
    """快速获取模拟器标准（便捷函数）"""
    return _standards_loader.get_simulator_standards()


def get_course_standards() -> Dict[str, Any]:
    """快速获取课程标准（便捷函数）"""
    return _standards_loader.get_course_standards()


def get_subject_color_scheme(subject: str) -> Optional[Dict[str, Any]]:
    """快速获取学科颜色方案（便捷函数）"""
    return _standards_loader.get_subject_color_scheme(subject)


def get_visualization_element(element_id: str) -> Optional[Dict[str, Any]]:
    """快速获取可视化元素（便捷函数）"""
    return _standards_loader.get_visualization_element(element_id)
