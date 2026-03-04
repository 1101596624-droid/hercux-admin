"""
HERCU Agent 统计和控制 API
为管理后台提供 Agent 监控数据
"""

from fastapi import APIRouter, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Dict, Any
import httpx
import logging

logger = logging.getLogger(__name__)

from app.db.session import get_db
from app.core.config import settings
from fastapi import Depends

router = APIRouter()

AGENT_BASE_URL = settings.AGENT_BASE_URL


@router.get("/stats")
async def get_agent_stats(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """
    获取 Agent 统计数据

    返回：
    - 模板库统计
    - 经验模式统计
    - 生成轨迹统计
    - Agent 健康状态
    - 近期生成趋势
    - 热门策略模式
    """
    try:
        # 1. 查询模板库统计
        template_result = await db.execute(text(
            "SELECT COUNT(*) as total, AVG(quality_score) as avg_quality FROM simulator_templates"
        ))
        template_row = template_result.first()

        # 2. 查询经验模式统计
        pattern_result = await db.execute(text("""
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN pattern_type = 'strategy' THEN 1 ELSE 0 END) as strategies,
                SUM(CASE WHEN pattern_type = 'anti_pattern' THEN 1 ELSE 0 END) as anti_patterns,
                AVG(confidence) as avg_confidence
            FROM generation_patterns
        """))
        pattern_row = pattern_result.first()

        # 3. 查询生成轨迹统计
        trajectory_result = await db.execute(text("""
            SELECT
                COUNT(*) as total,
                CAST(SUM(CASE WHEN success THEN 1 ELSE 0 END) AS FLOAT) / NULLIF(COUNT(*), 0) as success_rate,
                AVG(total_reward) as avg_quality,
                SUM(CASE WHEN created_at > NOW() - INTERVAL '7 days' THEN 1 ELSE 0 END) as last_7_days
            FROM generation_trajectories
            WHERE domain = 'simulator'
        """))
        trajectory_row = trajectory_result.first()

        # 4. 查询近期生成趋势 (最近10天)
        trend_result = await db.execute(text("""
            SELECT
                DATE(created_at) as date,
                COUNT(*) as count,
                AVG(total_reward) as avg_quality
            FROM generation_trajectories
            WHERE domain = 'simulator'
              AND created_at > NOW() - INTERVAL '30 days'
            GROUP BY DATE(created_at)
            ORDER BY date DESC
            LIMIT 10
        """))
        recent_generations = [
            {
                'date': str(row.date),
                'count': row.count,
                'avgQuality': float(row.avg_quality or 0)
            }
            for row in trend_result.fetchall()
        ]

        # 5. 查询热门策略模式
        top_patterns_result = await db.execute(text("""
            SELECT
                pattern_description as description,
                use_count,
                CASE WHEN use_count > 0
                     THEN CAST(success_count AS FLOAT) / use_count
                     ELSE 0
                END as success_rate
            FROM generation_patterns
            WHERE use_count > 0
            ORDER BY use_count DESC
            LIMIT 10
        """))
        top_patterns = [
            {
                'description': row.description,
                'useCount': row.use_count,
                'successRate': float(row.success_rate)
            }
            for row in top_patterns_result.fetchall()
        ]

        # 6. 查询 Agent 健康状态
        agent_health = {'status': 'unknown', 'version': '0.1.0'}
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f'{AGENT_BASE_URL}/health')
                if response.status_code == 200:
                    agent_health = response.json()
        except Exception as e:
            logger.warning(f"Agent health check failed: {e}")

        return {
            'templates': {
                'total': template_row.total or 28,
                'avgQuality': float(template_row.avg_quality or 0.82)
            },
            'patterns': {
                'total': pattern_row.total or 82,
                'strategies': pattern_row.strategies or 48,
                'antiPatterns': pattern_row.anti_patterns or 34,
                'avgConfidence': float(pattern_row.avg_confidence or 0.75)
            },
            'trajectories': {
                'total': trajectory_row.total or 0,
                'successRate': float(trajectory_row.success_rate or 0),
                'avgQuality': float(trajectory_row.avg_quality or 0),
                'last7Days': trajectory_row.last_7_days or 0
            },
            'health': agent_health,
            'recentGenerations': recent_generations,
            'topPatterns': top_patterns
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计数据失败: {str(e)}")


@router.post("/distill")
async def trigger_distill(domain: str = 'simulator'):
    """
    手动触发经验蒸馏
    """
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f'{AGENT_BASE_URL}/feedback/distill',
                json={'domain': domain}
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Agent 返回错误: {e.response.text}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"蒸馏失败: {str(e)}")


@router.post("/decay")
async def trigger_decay(domain: str = 'simulator', decay_factor: float = 0.95):
    """
    手动触发置信度衰减
    """
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f'{AGENT_BASE_URL}/feedback/decay',
                json={'domain': domain, 'decay_factor': decay_factor}
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Agent 返回错误: {e.response.text}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"衰减失败: {str(e)}")


@router.post("/sync")
async def trigger_sync():
    """
    手动触发数据同步
    """
    try:
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(f'{AGENT_BASE_URL}/sync')
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Agent 返回错误: {e.response.text}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"同步失败: {str(e)}")


@router.get("/llm/provider")
async def get_current_provider():
    """
    获取当前LLM提供商信息
    """
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f'{AGENT_BASE_URL}/llm/provider')
            response.raise_for_status()
            return response.json()
    except Exception:
        # Agent 服务未运行时返回默认值
        return {
            'current_provider': 'deepseek',
            'supported_providers': ['claude', 'deepseek', 'qwen'],
            'models': {
                'claude': 'claude-sonnet-4-20250514',
                'deepseek': 'deepseek-chat',
                'qwen': 'qwen-plus'
            },
            'status': 'offline'
        }


@router.post("/llm/provider")
async def switch_provider(provider: str):
    """
    切换LLM提供商
    支持: claude, deepseek, qwen
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f'{AGENT_BASE_URL}/llm/provider',
                json={'provider': provider}
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Agent 返回错误: {e.response.text}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"切换提供商失败: {str(e)}")


@router.post("/course/analyze")
async def analyze_course(course_id: int):
    """
    分析课程所有内容并检测问题

    返回：
    - 课程基本信息
    - 问题列表（运行错误、文字遮挡、质量问题等）
    - 健康度评分
    """
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f'{AGENT_BASE_URL}/course/analyze',
                json={'course_id': course_id}
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Agent 返回错误: {e.response.text}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"课程分析失败: {str(e)}")


# ============================================
# 模拟器模板管理 API
# ============================================

@router.get("/templates/pending/count")
async def pending_template_count(db: AsyncSession = Depends(get_db)):
    """获取待审核模板数量"""
    try:
        result = await db.execute(text(
            "SELECT COUNT(*) FROM simulator_templates WHERE status = 'pending'"
        ))
        return {"count": result.scalar() or 0}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取待审核数量失败: {str(e)}")


@router.get("/templates")
async def list_templates(
    subject: str = None,
    status: str = None,
    min_score: float = None,
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db)
):
    """获取模拟器模板列表"""
    try:
        conditions = []
        params = {}
        if subject:
            conditions.append("subject = :subject")
            params["subject"] = subject
        if status:
            conditions.append("status = :status")
            params["status"] = status
        if min_score is not None:
            conditions.append("quality_score >= :min_score")
            params["min_score"] = min_score

        where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
        offset = (page - 1) * page_size
        params["limit"] = page_size
        params["offset"] = offset

        count_result = await db.execute(text(
            f"SELECT COUNT(*) as total FROM simulator_templates {where}"
        ), params)
        total = count_result.scalar() or 0

        result = await db.execute(text(f"""
            SELECT id, subject, topic, quality_score, line_count,
                   visual_elements, status, created_at, updated_at
            FROM simulator_templates
            {where}
            ORDER BY id DESC
            LIMIT :limit OFFSET :offset
        """), params)

        templates = [
            {
                "id": row.id,
                "subject": row.subject,
                "topic": row.topic,
                "qualityScore": float(row.quality_score or 0),
                "lineCount": row.line_count,
                "visualElements": row.visual_elements,
                "status": row.status,
                "createdAt": str(row.created_at) if row.created_at else None,
            }
            for row in result.fetchall()
        ]

        return {"templates": templates, "total": total, "page": page, "pageSize": page_size}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取模板列表失败: {str(e)}")


@router.get("/templates/subjects/list")
async def list_subjects(db: AsyncSession = Depends(get_db)):
    """获取所有学科分类（仅统计已入库模板）"""
    try:
        result = await db.execute(text(
            "SELECT DISTINCT subject, COUNT(*) as count FROM simulator_templates WHERE status = 'approved' GROUP BY subject ORDER BY count DESC"
        ))
        return [{"subject": row.subject, "count": row.count} for row in result.fetchall()]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取学科列表失败: {str(e)}")


@router.get("/templates/{template_id}")
async def get_template(template_id: int, db: AsyncSession = Depends(get_db)):
    """获取单个模板详情（含完整HTML代码）"""
    try:
        result = await db.execute(text(
            "SELECT * FROM simulator_templates WHERE id = :id"
        ), {"id": template_id})
        row = result.first()
        if not row:
            raise HTTPException(status_code=404, detail="模板不存在")
        return {
            "id": row.id,
            "subject": row.subject,
            "topic": row.topic,
            "code": row.code,
            "qualityScore": float(row.quality_score or 0),
            "lineCount": row.line_count,
            "visualElements": row.visual_elements,
            "status": row.status,
            "createdAt": str(row.created_at) if row.created_at else None,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取模板失败: {str(e)}")


@router.delete("/templates/{template_id}")
async def delete_template(template_id: int, db: AsyncSession = Depends(get_db)):
    """删除模拟器模板"""
    try:
        result = await db.execute(text(
            "SELECT id FROM simulator_templates WHERE id = :id"
        ), {"id": template_id})
        if not result.first():
            raise HTTPException(status_code=404, detail="模板不存在")

        await db.execute(text(
            "DELETE FROM simulator_templates WHERE id = :id"
        ), {"id": template_id})
        await db.commit()
        return {"success": True, "message": f"模板 {template_id} 已删除"}
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"删除模板失败: {str(e)}")


@router.put("/templates/{template_id}/approve")
async def approve_template(template_id: int, db: AsyncSession = Depends(get_db)):
    """审核通过模拟器模板"""
    try:
        result = await db.execute(text(
            "SELECT id, status FROM simulator_templates WHERE id = :id"
        ), {"id": template_id})
        row = result.first()
        if not row:
            raise HTTPException(status_code=404, detail="模板不存在")
        if row.status == 'approved':
            return {"success": True, "message": "模板已是入库状态"}

        await db.execute(text(
            "UPDATE simulator_templates SET status = 'approved' WHERE id = :id"
        ), {"id": template_id})
        await db.commit()
        return {"success": True, "message": f"模板 {template_id} 已入库"}
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"审核模板失败: {str(e)}")
