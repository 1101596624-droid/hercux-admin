"""
测试脚本: Grinder学习集成

验证：
1. 题目生成和审核
2. QuizScorer质量评分
3. 85+分题目自动保存为模板
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.db.session import AsyncSessionLocal
from app.services.grinder.service import get_grinder_service


async def test_grinder_learning_integration():
    """测试Grinder学习集成"""

    async with AsyncSessionLocal() as db:
        try:
            print("=" * 60)
            print("测试: Grinder学习集成")
            print("=" * 60)

            # 创建service
            grinder_service = get_grinder_service(db)

            # 测试题目生成
            topic = "Python编程基础"
            question_count = 3

            print(f"\n1. 生成题目...")
            print(f"   主题: {topic}")
            print(f"   数量: {question_count}")

            result = await grinder_service.generate_exam(
                topic=topic,
                question_count=question_count,
                focus_categories=["变量", "函数", "数据类型"]
            )

            # 检查结果
            exam = result.get('exam', {})
            review = result.get('review', {})
            quality_results = review.get('quality_results', {})

            print(f"\n2. 审核结果:")
            print(f"   审核通过: {review.get('approved', False)}")
            print(f"   审核分数: {review.get('score', 0)}")
            print(f"   问题数: {len(review.get('issues', []))}")

            if review.get('issues'):
                for issue in review['issues']:
                    print(f"   - {issue}")

            print(f"\n3. 质量评分结果:")
            print(f"   评估题目数: {quality_results.get('total_evaluated', 0)}")
            print(f"   高质量题目数(75+): {quality_results.get('high_quality_count', 0)}")
            print(f"   保存为模板数(85+): {quality_results.get('saved_as_template', 0)}")

            # 显示每道题的质量分数
            quality_scores = quality_results.get('quality_scores', [])
            if quality_scores:
                print(f"\n4. 各题质量分数:")
                for score_info in quality_scores:
                    qid = score_info.get('question_id')
                    score = score_info.get('score')
                    passed = score_info.get('passed')
                    status = "✓ 通过" if passed else "✗ 未通过"
                    template_status = " [已保存为模板]" if score >= 85 else ""
                    print(f"   题目 #{qid}: {score:.1f}/100 ({status}){template_status}")

            # 显示保存的模板信息
            saved_questions = quality_results.get('saved_questions', [])
            if saved_questions:
                print(f"\n5. 保存的学习模板:")
                for saved in saved_questions:
                    print(f"   题目 #{saved.get('question_id')} -> 模板ID: {saved.get('template_id')}, 质量分: {saved.get('quality_score'):.1f}")

            print(f"\n6. 元数据:")
            print(f"   使用最新信息: {result.get('latest_info_used', False)}")
            print(f"   生成尝试次数: {result.get('attempts', 1)}")

            print("\n" + "=" * 60)
            print("✓ 测试完成")
            print("=" * 60)

            # 验证数据库
            from app.models.models import ContentTemplate
            from sqlalchemy import select

            result_query = await db.execute(
                select(ContentTemplate).filter(
                    ContentTemplate.template_type == 'quiz_question'
                )
            )
            template_count = len(result_query.scalars().all())

            print(f"\n数据库验证:")
            print(f"   quiz_question模板总数: {template_count}")

        except Exception as e:
            print(f"\n✗ 测试失败: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_grinder_learning_integration())
