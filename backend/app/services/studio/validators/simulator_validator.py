# ============================================
# validators/simulator_validator.py - 模拟器内容验证器
# 检查生成的模拟器内容是否完整、格式正确、质量达标
# ============================================

from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass, field


@dataclass
class ValidationResult:
    """验证结果"""
    is_valid: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    missing_fields: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)


class SimulatorValidator:
    """模拟器内容验证器"""

    # 各类型模拟器的必填字段
    REQUIRED_FIELDS = {
        "custom": {
            "base": ["simulator_id", "name", "description", "type"],
            "inputs": ["id", "name", "label", "type"],
            "outputs": ["id", "name", "label", "formula"]
        },
        "timeline": {
            "base": ["simulator_id", "name", "description", "type", "timeline"],
            "timeline": ["title", "events"],
            "event": ["id", "year", "title", "description"]
        },
        "decision": {
            "base": ["simulator_id", "name", "description", "type", "decision"],
            "decision": ["title", "scenario", "question", "options"],
            "option": ["id", "label", "result"]
        },
        "comparison": {
            "base": ["simulator_id", "name", "description", "type", "comparison"],
            "comparison": ["title", "dimensions", "items"],
            "item": ["id", "name", "attributes"]
        },
        "concept-map": {
            "base": ["simulator_id", "name", "description", "type", "concept_map"],
            "concept_map": ["title", "nodes", "relations"],
            "node": ["id", "label"],
            "relation": ["from_id", "to", "label"]
        }
    }

    # 内容质量要求
    MIN_DESCRIPTION_LENGTH = 10
    MIN_TIMELINE_EVENTS = 3
    MIN_DECISION_OPTIONS = 2
    MIN_COMPARISON_ITEMS = 2
    MIN_COMPARISON_DIMENSIONS = 2
    MIN_CONCEPT_NODES = 3
    MIN_CONCEPT_RELATIONS = 2

    def validate(self, simulator_spec: Dict[str, Any]) -> ValidationResult:
        """
        验证模拟器规格

        Args:
            simulator_spec: 模拟器规格字典

        Returns:
            ValidationResult 验证结果
        """
        result = ValidationResult()

        if not simulator_spec:
            result.is_valid = False
            result.errors.append("模拟器规格为空")
            return result

        sim_type = simulator_spec.get("type", "")

        # 1. 检查基础字段
        self._check_base_fields(simulator_spec, sim_type, result)

        # 2. 根据类型检查特定字段
        if sim_type == "custom":
            self._validate_custom_simulator(simulator_spec, result)
        elif sim_type == "timeline":
            self._validate_timeline_simulator(simulator_spec, result)
        elif sim_type == "decision":
            self._validate_decision_simulator(simulator_spec, result)
        elif sim_type == "comparison":
            self._validate_comparison_simulator(simulator_spec, result)
        elif sim_type == "concept-map":
            self._validate_concept_map_simulator(simulator_spec, result)
        else:
            result.warnings.append(f"未知的模拟器类型: {sim_type}")

        # 3. 检查内容质量
        self._check_content_quality(simulator_spec, sim_type, result)

        # 设置最终验证状态
        result.is_valid = len(result.errors) == 0

        return result

    def _check_base_fields(self, spec: Dict, sim_type: str, result: ValidationResult):
        """检查基础必填字段"""
        required = self.REQUIRED_FIELDS.get(sim_type, {}).get("base", [])
        if not required:
            required = ["simulator_id", "name", "description", "type"]

        for field in required:
            if field not in spec or not spec[field]:
                result.missing_fields.append(field)
                result.errors.append(f"缺少必填字段: {field}")

    def _validate_custom_simulator(self, spec: Dict, result: ValidationResult):
        """验证理科模拟器（参数计算型）"""
        inputs = spec.get("inputs", [])
        outputs = spec.get("outputs", [])

        # 检查是否有输入输出
        if not inputs:
            result.errors.append("理科模拟器缺少 inputs 配置")
            result.suggestions.append("添加至少一个输入参数（如滑块控制）")

        if not outputs:
            result.errors.append("理科模拟器缺少 outputs 配置")
            result.suggestions.append("添加至少一个输出结果（带计算公式）")

        # 检查每个 input 的字段
        required_input_fields = self.REQUIRED_FIELDS["custom"]["inputs"]
        for i, inp in enumerate(inputs):
            for field in required_input_fields:
                if field not in inp or inp[field] is None:
                    result.errors.append(f"inputs[{i}] 缺少字段: {field}")

            # 检查滑块类型的范围
            if inp.get("type") == "slider":
                if inp.get("min") is None or inp.get("max") is None:
                    result.warnings.append(f"inputs[{i}] 滑块缺少 min/max 范围")

        # 检查每个 output 的字段
        required_output_fields = self.REQUIRED_FIELDS["custom"]["outputs"]
        for i, out in enumerate(outputs):
            for field in required_output_fields:
                if field not in out or not out[field]:
                    result.errors.append(f"outputs[{i}] 缺少字段: {field}")

            # 检查公式是否引用了有效的输入
            formula = out.get("formula", "")
            if formula and "input." not in formula:
                result.warnings.append(f"outputs[{i}] 公式可能未正确引用输入参数")

    def _validate_timeline_simulator(self, spec: Dict, result: ValidationResult):
        """验证时间线模拟器"""
        timeline = spec.get("timeline", {})

        if not timeline:
            result.errors.append("时间线模拟器缺少 timeline 配置")
            return

        # 检查 timeline 字段
        for field in self.REQUIRED_FIELDS["timeline"]["timeline"]:
            if field not in timeline or not timeline[field]:
                result.errors.append(f"timeline 缺少字段: {field}")

        # 检查事件
        events = timeline.get("events", [])
        if len(events) < self.MIN_TIMELINE_EVENTS:
            result.warnings.append(f"时间线事件数量不足，建议至少 {self.MIN_TIMELINE_EVENTS} 个")
            result.suggestions.append("添加更多时间线事件以丰富内容")

        # 检查每个事件的字段
        required_event_fields = self.REQUIRED_FIELDS["timeline"]["event"]
        for i, event in enumerate(events):
            for field in required_event_fields:
                if field not in event or not event[field]:
                    result.errors.append(f"timeline.events[{i}] 缺少字段: {field}")

    def _validate_decision_simulator(self, spec: Dict, result: ValidationResult):
        """验证决策情景模拟器"""
        decision = spec.get("decision", {})

        if not decision:
            result.errors.append("决策模拟器缺少 decision 配置")
            return

        # 检查 decision 字段
        for field in self.REQUIRED_FIELDS["decision"]["decision"]:
            if field not in decision or not decision[field]:
                result.errors.append(f"decision 缺少字段: {field}")

        # 检查选项
        options = decision.get("options", [])
        if len(options) < self.MIN_DECISION_OPTIONS:
            result.errors.append(f"决策选项数量不足，至少需要 {self.MIN_DECISION_OPTIONS} 个")

        # 检查是否有最优选项
        has_optimal = any(opt.get("isOptimal", False) for opt in options)
        if not has_optimal:
            result.warnings.append("决策选项中没有标记最优选项 (isOptimal)")
            result.suggestions.append("标记一个最优选项以提供学习指导")

        # 检查每个选项的字段
        required_option_fields = self.REQUIRED_FIELDS["decision"]["option"]
        for i, opt in enumerate(options):
            for field in required_option_fields:
                if field not in opt or not opt[field]:
                    result.errors.append(f"decision.options[{i}] 缺少字段: {field}")

    def _validate_comparison_simulator(self, spec: Dict, result: ValidationResult):
        """验证对比分析模拟器"""
        comparison = spec.get("comparison", {})

        if not comparison:
            result.errors.append("对比模拟器缺少 comparison 配置")
            return

        # 检查 comparison 字段
        for field in self.REQUIRED_FIELDS["comparison"]["comparison"]:
            if field not in comparison or not comparison[field]:
                result.errors.append(f"comparison 缺少字段: {field}")

        # 检查维度数量
        dimensions = comparison.get("dimensions", [])
        if len(dimensions) < self.MIN_COMPARISON_DIMENSIONS:
            result.warnings.append(f"对比维度数量不足，建议至少 {self.MIN_COMPARISON_DIMENSIONS} 个")

        # 检查对比项数量
        items = comparison.get("items", [])
        if len(items) < self.MIN_COMPARISON_ITEMS:
            result.errors.append(f"对比项数量不足，至少需要 {self.MIN_COMPARISON_ITEMS} 个")

        # 检查每个对比项的字段和属性完整性
        for i, item in enumerate(items):
            for field in self.REQUIRED_FIELDS["comparison"]["item"]:
                if field not in item or not item[field]:
                    result.errors.append(f"comparison.items[{i}] 缺少字段: {field}")

            # 检查属性是否覆盖所有维度
            attrs = item.get("attributes", {})
            for dim in dimensions:
                if dim not in attrs:
                    result.warnings.append(f"comparison.items[{i}] 缺少维度 '{dim}' 的属性值")

    def _validate_concept_map_simulator(self, spec: Dict, result: ValidationResult):
        """验证概念关系图模拟器"""
        concept_map = spec.get("concept_map", {})

        if not concept_map:
            result.errors.append("概念图模拟器缺少 concept_map 配置")
            return

        # 检查 concept_map 字段
        for field in self.REQUIRED_FIELDS["concept-map"]["concept_map"]:
            if field not in concept_map or not concept_map[field]:
                result.errors.append(f"concept_map 缺少字段: {field}")

        # 检查节点数量
        nodes = concept_map.get("nodes", [])
        if len(nodes) < self.MIN_CONCEPT_NODES:
            result.warnings.append(f"概念节点数量不足，建议至少 {self.MIN_CONCEPT_NODES} 个")

        # 检查关系数量
        relations = concept_map.get("relations", [])
        if len(relations) < self.MIN_CONCEPT_RELATIONS:
            result.warnings.append(f"概念关系数量不足，建议至少 {self.MIN_CONCEPT_RELATIONS} 个")

        # 收集所有节点 ID
        node_ids = {node.get("id") for node in nodes}

        # 检查每个节点的字段
        for i, node in enumerate(nodes):
            for field in self.REQUIRED_FIELDS["concept-map"]["node"]:
                if field not in node or not node[field]:
                    result.errors.append(f"concept_map.nodes[{i}] 缺少字段: {field}")

        # 检查每个关系的字段和引用有效性
        for i, rel in enumerate(relations):
            # 处理 from/from_id 字段名差异
            from_id = rel.get("from_id") or rel.get("from")
            to_id = rel.get("to")

            if not from_id:
                result.errors.append(f"concept_map.relations[{i}] 缺少 from/from_id 字段")
            elif from_id not in node_ids:
                result.errors.append(f"concept_map.relations[{i}] 引用了不存在的节点: {from_id}")

            if not to_id:
                result.errors.append(f"concept_map.relations[{i}] 缺少 to 字段")
            elif to_id not in node_ids:
                result.errors.append(f"concept_map.relations[{i}] 引用了不存在的节点: {to_id}")

    def _check_content_quality(self, spec: Dict, sim_type: str, result: ValidationResult):
        """检查内容质量"""
        # 检查描述长度
        description = spec.get("description", "")
        if len(description) < self.MIN_DESCRIPTION_LENGTH:
            result.warnings.append(f"模拟器描述过短（{len(description)}字），建议至少 {self.MIN_DESCRIPTION_LENGTH} 字")
            result.suggestions.append("提供更详细的模拟器描述，说明其教学目的和使用方法")

        # 检查名称是否有意义
        name = spec.get("name", "")
        if not name or name in ["模拟器", "simulator", "test", "测试"]:
            result.warnings.append("模拟器名称不够具体")
            result.suggestions.append("使用更具描述性的名称，如'牛顿第二定律计算器'")

        # 检查说明是否存在
        instructions = spec.get("instructions", [])
        if not instructions:
            result.warnings.append("缺少使用说明 (instructions)")
            result.suggestions.append("添加使用说明帮助学生理解如何操作模拟器")


def validate_simulator_spec(spec: Dict[str, Any]) -> Tuple[bool, ValidationResult]:
    """
    便捷函数：验证模拟器规格

    Args:
        spec: 模拟器规格

    Returns:
        (是否有效, 验证结果)
    """
    validator = SimulatorValidator()
    result = validator.validate(spec)
    return result.is_valid, result


def get_fix_prompt(result: ValidationResult, original_spec: Dict[str, Any]) -> str:
    """
    生成修复提示，用于让 AI 补充缺失内容

    Args:
        result: 验证结果
        original_spec: 原始模拟器规格

    Returns:
        修复提示字符串
    """
    prompt_parts = ["请修复以下模拟器规格中的问题：\n"]

    if result.errors:
        prompt_parts.append("【错误（必须修复）】")
        for error in result.errors:
            prompt_parts.append(f"- {error}")
        prompt_parts.append("")

    if result.missing_fields:
        prompt_parts.append("【缺失字段】")
        for field in result.missing_fields:
            prompt_parts.append(f"- {field}")
        prompt_parts.append("")

    if result.warnings:
        prompt_parts.append("【警告（建议修复）】")
        for warning in result.warnings:
            prompt_parts.append(f"- {warning}")
        prompt_parts.append("")

    if result.suggestions:
        prompt_parts.append("【改进建议】")
        for suggestion in result.suggestions:
            prompt_parts.append(f"- {suggestion}")
        prompt_parts.append("")

    prompt_parts.append("【原始规格】")
    import json
    prompt_parts.append(json.dumps(original_spec, ensure_ascii=False, indent=2))

    prompt_parts.append("\n请输出修复后的完整 JSON 规格，确保所有必填字段都有值，内容质量达标。")

    return "\n".join(prompt_parts)
