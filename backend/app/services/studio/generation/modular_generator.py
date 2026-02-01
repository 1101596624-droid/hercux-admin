# ============================================
# generation/modular_generator.py - 模块化生成器
# ============================================

from typing import AsyncGenerator, Optional
from prompts import build_structure_prompt, build_node_content_prompt, build_layer_prompt
from json_utils import safe_parse_json
from styles import get_style_prompt


class ModularGenerator:
    """模块化课程生成器 - 分阶段生成课程内容"""

    def __init__(self, provider):
        self.provider = provider

    async def generate_stream(
        self,
        source_material: str,
        course_title: str,
        style: str = "rcs",
        source_info: str = ""
    ) -> AsyncGenerator[dict, None]:
        """
        分模块流式生成课程内容
        第一阶段：生成课程结构
        第二阶段：逐个生成每个节点的详细内容

        Yields dict with:
        - type: "phase" | "structure" | "node_start" | "chunk" | "node_complete" | "complete" | "error"
        - data: 相关数据
        """
        try:
            # ========== 第一阶段：生成课程结构 ==========
            yield {"type": "phase", "data": {"phase": 1, "message": "正在分析素材，设计课程结构..."}}

            structure_prompt = build_structure_prompt(source_material, style, course_title)
            structure_content = ""

            async for chunk in self.provider.generate_stream(structure_prompt, max_tokens=16000):
                structure_content += chunk
                yield {"type": "chunk", "data": {"content": chunk, "phase": 1}}

            # 解析结构
            structure = safe_parse_json(structure_content)
            if not structure:
                yield {"type": "error", "data": {"message": "无法解析课程结构，请重试"}}
                return

            nodes_outline = structure.get("nodes", [])
            meta = structure.get("meta", {})
            total_nodes = len(nodes_outline)

            yield {"type": "structure", "data": {
                "meta": meta,
                "nodes_count": total_nodes,
                "nodes_outline": nodes_outline
            }}

            # ========== 第二阶段：逐个生成节点内容 ==========
            yield {"type": "phase", "data": {"phase": 2, "message": f"开始生成 {total_nodes} 个节点的详细内容..."}}

            completed_nodes = []
            previous_summary = ""

            for i, node_outline in enumerate(nodes_outline):
                yield {"type": "node_start", "data": {
                    "index": i,
                    "total": total_nodes,
                    "title": node_outline.get("title", f"节点 {i+1}")
                }}

                # 生成节点内容（带重试逻辑）
                max_retries = 2
                node_data = None
                use_compact = False

                for attempt in range(max_retries):
                    # 构建 prompt，第二次尝试使用 compact 模式
                    node_prompt = build_node_content_prompt(
                        source_material=source_material,
                        style=style,
                        course_title=course_title,
                        node_info=node_outline,
                        node_index=i,
                        total_nodes=total_nodes,
                        previous_node_summary=previous_summary,
                        compact=use_compact
                    )

                    # 根据模式调整 max_tokens
                    tokens_limit = 6000 if use_compact else 8000

                    node_content = ""
                    async for chunk in self.provider.generate_stream(node_prompt, max_tokens=tokens_limit):
                        node_content += chunk
                        yield {"type": "chunk", "data": {"content": chunk, "phase": 2, "node_index": i}}

                    # 解析节点内容
                    node_data = safe_parse_json(node_content)

                    if node_data:
                        break  # 解析成功，退出重试循环
                    elif attempt < max_retries - 1:
                        # 解析失败，准备重试
                        use_compact = True
                        yield {"type": "chunk", "data": {
                            "content": "\n\n[检测到内容截断，正在使用精简模式重新生成...]\n\n",
                            "phase": 2,
                            "node_index": i
                        }}
                        print(f"[DEBUG] 节点 {i+1} JSON 解析失败，使用 compact 模式重试")

                if node_data:
                    # 保存摘要用于下一节点衔接
                    previous_summary = node_data.get("summary", "")

                    # 合并节点大纲和详细内容
                    full_node = {
                        "title": node_outline.get("title"),
                        "estimated_minutes": node_outline.get("estimated_minutes", 30),
                        "prerequisites": node_outline.get("prerequisites", []),
                        "learning_objectives": node_outline.get("learning_objectives", []),
                        "content": node_data.get("content", {}),
                        "timeline": node_data.get("timeline", []),
                        "quiz": node_data.get("quiz", {}),
                        "ai_tutor": node_data.get("ai_tutor", {})
                    }
                    completed_nodes.append(full_node)

                    yield {"type": "node_complete", "data": {
                        "index": i,
                        "total": total_nodes,
                        "node": full_node
                    }}
                else:
                    # 两次尝试都失败，尝试分层生成（第三次尝试）
                    yield {"type": "chunk", "data": {
                        "content": "\n\n[尝试分层生成模式...]\n\n",
                        "phase": 2,
                        "node_index": i
                    }}
                    print(f"[DEBUG] 节点 {i+1} 使用分层生成模式")

                    chunked_node = await self._generate_node_chunked(
                        course_title=course_title,
                        node_info=node_outline,
                        node_index=i,
                        total_nodes=total_nodes,
                        style=style,
                        previous_summary=previous_summary
                    )

                    if chunked_node:
                        previous_summary = chunked_node.get("summary", "")
                        full_node = {
                            "title": node_outline.get("title"),
                            "estimated_minutes": node_outline.get("estimated_minutes", 30),
                            "prerequisites": node_outline.get("prerequisites", []),
                            "learning_objectives": node_outline.get("learning_objectives", []),
                            "content": chunked_node.get("content", {}),
                            "timeline": chunked_node.get("timeline", []),
                            "quiz": chunked_node.get("quiz", {}),
                            "ai_tutor": chunked_node.get("ai_tutor", {})
                        }
                        completed_nodes.append(full_node)
                        yield {"type": "node_complete", "data": {
                            "index": i,
                            "total": total_nodes,
                            "node": full_node,
                            "warning": "使用分层生成模式完成"
                        }}
                    else:
                        # 分层生成也失败，使用基本结构
                        basic_node = {
                            "title": node_outline.get("title"),
                            "estimated_minutes": node_outline.get("estimated_minutes", 30),
                            "prerequisites": node_outline.get("prerequisites", []),
                            "learning_objectives": node_outline.get("learning_objectives", []),
                            "content": {},
                            "timeline": [],
                            "quiz": {},
                            "ai_tutor": {}
                        }
                        completed_nodes.append(basic_node)
                        yield {"type": "node_complete", "data": {
                            "index": i,
                            "total": total_nodes,
                            "node": basic_node,
                            "warning": "节点内容解析失败（已重试3次），使用基本结构"
                        }}

            # ========== 组装最终课程包 ==========
            final_raw = {
                "meta": meta,
                "nodes": completed_nodes
            }

            yield {"type": "complete", "data": {"raw": final_raw}}

        except Exception as e:
            yield {"type": "error", "data": {"message": str(e)}}

    async def _generate_node_chunked(
        self,
        course_title: str,
        node_info: dict,
        node_index: int,
        total_nodes: int,
        style: str,
        previous_summary: str = ""
    ) -> Optional[dict]:
        """
        分层生成节点内容 - 每个层独立生成以避免截断
        生成顺序: L1 → L2 → L3 → timeline → quiz → ai_tutor
        """
        style_prompt = get_style_prompt(style) or get_style_prompt("rcs")
        layers = ["L1", "L2", "L3", "timeline", "quiz", "ai_tutor"]
        results = {}

        print(f"[DEBUG] 节点 {node_index + 1} 开始分层生成")

        for layer in layers:
            try:
                prompt = build_layer_prompt(
                    layer=layer,
                    course_title=course_title,
                    node_info=node_info,
                    node_index=node_index,
                    total_nodes=total_nodes,
                    style_prompt=style_prompt,
                    previous_node_summary=previous_summary
                )

                # 每层使用较小的 token 限制
                layer_content = ""
                async for chunk in self.provider.generate_stream(prompt, max_tokens=2000):
                    layer_content += chunk

                # 解析该层的 JSON
                layer_data = safe_parse_json(layer_content)
                if layer_data:
                    results[layer] = layer_data
                    print(f"[DEBUG] 节点 {node_index + 1} 层 {layer} 生成成功")
                else:
                    print(f"[WARNING] 节点 {node_index + 1} 层 {layer} 解析失败，使用默认值")
                    results[layer] = self._get_default_layer(layer)

            except Exception as e:
                print(f"[ERROR] 节点 {node_index + 1} 层 {layer} 生成异常: {e}")
                results[layer] = self._get_default_layer(layer)

        # 组装完整节点
        assembled_node = {
            "content": {
                "L1_intuition": results.get("L1", {}),
                "L2_mechanism": results.get("L2", {}),
                "L3_essence": results.get("L3", {})
            },
            "timeline": results.get("timeline", []),
            "quiz": results.get("quiz", {}),
            "ai_tutor": results.get("ai_tutor", {}),
            "summary": f"节点 {node_index + 1}: {node_info.get('title', '')}"
        }

        print(f"[DEBUG] 节点 {node_index + 1} 分层生成完成")
        return assembled_node

    def _get_default_layer(self, layer: str) -> dict:
        """获取层的默认值"""
        defaults = {
            "L1": {"text": "内容生成中...", "analogy_source": ""},
            "L2": {"text": "内容生成中...", "key_points": []},
            "L3": {"formulas": [], "core_insight": "内容生成中..."},
            "timeline": [],
            "quiz": {"questions": []},
            "ai_tutor": {"on_enter": "", "on_complete": "", "hints": []}
        }
        return defaults.get(layer, {})
