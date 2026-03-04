"""
StandardsLoader 测试文件
版本: v3
创建日期: 2026-02-10
"""

import pytest
from app.services.course_generation.standards_loader import (
    StandardsLoader,
    get_standards_loader,
    get_simulator_standards,
    get_course_standards
)


class TestStandardsLoader:
    """StandardsLoader 单元测试"""

    def test_singleton_pattern(self):
        """测试单例模式"""
        loader1 = get_standards_loader()
        loader2 = get_standards_loader()
        assert loader1 is loader2, "StandardsLoader should be singleton"

    def test_load_simulator_standards(self):
        """测试加载模拟器标准"""
        loader = get_standards_loader()
        standards = loader.get_simulator_standards()

        assert standards is not None, "Simulator standards should not be None"
        assert 'version' in standards, "Should have version field"
        assert 'code_quality' in standards, "Should have code_quality field"
        assert 'visual_quality' in standards, "Should have visual_quality field"

    def test_load_course_standards(self):
        """测试加载课程标准"""
        standards = get_course_standards()

        assert standards is not None
        assert 'version' in standards
        assert standards.get('version') == 'v3'
        assert 'course_level' in standards
        assert 'chapter_level' in standards

    def test_course_standards_hard_constraints_only(self):
        """课程标准仅保留硬约束，不应包含 recommended 字段"""
        standards = get_course_standards()
        course_level = standards.get('course_level', {})

        assert standards.get('standard_name') == 'v3'
        assert course_level.get('min_chapters') == 2
        assert 'max_chapters' not in course_level

        def has_recommended_key(value):
            if isinstance(value, dict):
                for k, v in value.items():
                    if 'recommended' in str(k).lower():
                        return True
                    if has_recommended_key(v):
                        return True
            elif isinstance(value, list):
                for item in value:
                    if has_recommended_key(item):
                        return True
            return False

        assert not has_recommended_key(standards), "course_standards.yaml should not contain recommended fields"

    def test_load_visualization_elements(self):
        """测试加载可视化元素"""
        loader = get_standards_loader()
        viz_elements = loader.get_visualization_elements()

        assert viz_elements is not None
        assert 'version' in viz_elements
        assert 'visualization_elements' in viz_elements

        elements = viz_elements['visualization_elements']
        assert len(elements) >= 20, "Should have at least 20 visualization elements"

        # 检查基本元素
        element_ids = [e['id'] for e in elements]
        assert 'circles' in element_ids
        assert 'rectangles' in element_ids
        assert 'lines' in element_ids

    def test_load_color_systems(self):
        """测试加载颜色系统"""
        loader = get_standards_loader()
        color_systems = loader.get_color_systems()

        assert color_systems is not None
        assert 'version' in color_systems
        assert 'subject_color_schemes' in color_systems

        schemes = color_systems['subject_color_schemes']
        assert len(schemes) >= 8, "Should have at least 8 color schemes"

        # 检查学科
        scheme_ids = [s['id'] for s in schemes]
        assert 'physics' in scheme_ids
        assert 'chemistry' in scheme_ids
        assert 'biology' in scheme_ids

    def test_get_subject_color_scheme(self):
        """测试获取学科配色方案"""
        loader = get_standards_loader()

        # 测试物理学配色
        physics_color = loader.get_subject_color_scheme('physics')
        assert physics_color is not None
        assert 'philosophy' in physics_color
        assert 'base_colors' in physics_color
        assert 'primary' in physics_color['base_colors']

    def test_get_visualization_element(self):
        """测试获取可视化元素"""
        loader = get_standards_loader()

        # 测试圆形元素
        circles = loader.get_visualization_element('circles')
        assert circles is not None
        assert circles['name'] == '圆形'
        assert 'description' in circles
        assert 'use_cases' in circles

    def test_get_interaction_types(self):
        """测试获取交互类型"""
        loader = get_standards_loader()
        interaction_types = loader.get_interaction_types()

        assert interaction_types is not None
        assert 'interaction_types' in interaction_types

        types = interaction_types['interaction_types']
        assert len(types) >= 12, "Should have at least 12 interaction types"

        # 检查基本交互类型
        type_ids = [t['id'] for t in types]
        assert 'click' in type_ids
        assert 'drag' in type_ids
        assert 'hover' in type_ids

    def test_get_animation_easing(self):
        """测试获取动画缓动函数"""
        loader = get_standards_loader()
        easing = loader.get_animation_easing()

        assert easing is not None
        assert 'easing_functions' in easing

        functions = easing['easing_functions']
        assert len(functions) >= 8, "Should have at least 8 easing functions"

        # 检查基本缓动函数
        function_ids = [f['id'] for f in functions]
        assert 'linear' in function_ids
        assert 'easeInOut' in function_ids
        assert 'easeOutBack' in function_ids

    def test_version_consistency(self):
        """测试版本一致性"""
        loader = get_standards_loader()
        is_consistent = loader.check_version_consistency()

        assert is_consistent, "All standard documents should have consistent versions"

    def test_validate_all_standards(self):
        """测试验证所有标准文档"""
        loader = get_standards_loader()
        results = loader.validate_all_standards()

        assert results is not None
        assert len(results) >= 9, "Should validate at least 9 standard documents"

        # 检查所有文档是否加载成功
        for name, result in results.items():
            assert result['status'] in ['ok', 'warning'], f"Standard '{name}' failed to load"

    def test_get_recommended_elements_for_subject(self):
        """测试获取学科推荐元素"""
        loader = get_standards_loader()

        # 测试物理学推荐元素
        physics_elements = loader.get_recommended_elements_for_subject('physics')
        assert physics_elements is not None
        assert len(physics_elements) >= 3, "Should recommend at least 3 elements"


class TestStandardsIntegration:
    """StandardsLoader 集成测试"""

    def test_supervisor_has_standards_loader(self):
        """测试监督者是否集成了StandardsLoader"""
        from app.services.course_generation.supervisor import CourseSupervisor

        supervisor = CourseSupervisor()
        assert hasattr(supervisor, 'standards_loader'), "Supervisor should have standards_loader"
        assert supervisor.standards_loader is not None

    def test_generator_has_standards_loader(self):
        """测试生成器是否集成了StandardsLoader"""
        from app.services.course_generation.generator import ChapterGenerator

        generator = ChapterGenerator()
        assert hasattr(generator, 'standards_loader'), "Generator should have standards_loader"
        assert generator.standards_loader is not None

    def test_service_has_standards_loader(self):
        """测试服务是否集成了StandardsLoader"""
        from app.services.course_generation.service import CourseGenerationService

        service = CourseGenerationService()
        assert hasattr(service, 'standards_loader'), "Service should have standards_loader"
        assert service.standards_loader is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
