# Quiz Learning Integration

## 概述

Quiz题目学习集成系统,使题目生成能够从高质量示例中学习并持续改进。

## 核心文件

- `quiz_generator.py` - EnhancedQuizGenerator (核心学习逻辑)
- `service.py` - QuizService (高级API)
- `test_integration.py` - 集成测试脚本

## 使用方法

### 基本使用

```python
from app.services.quiz import EnhancedQuizGenerator

generator = EnhancedQuizGenerator(db_session)
questions = await generator.generate_quiz_with_learning(
    node_title="Python变量",
    learning_objectives=["理解变量"],
    content="变量存储数据...",
    difficulty="easy",
    subject="programming",
    topic="python_basics",
    num_questions=13
)
```

### 生成完整题库

```python
quiz_bank = await generator.generate_full_quiz_bank(
    node_title="面向对象编程",
    learning_objectives=[...],
    content="...",
    subject="programming",
    topic="oop_basics"
)
# 返回: {"easy": [...], "medium": [...], "hard": [...]}
```

### 使用QuizService

```python
from app.services.quiz import QuizService

service = QuizService(db_session)
result = await service.generate_quiz_for_node(
    node_id=1,
    node_title="算法入门",
    learning_objectives=[...],
    content="...",
    subject="computer_science",
    topic="algorithms"
)
```

## 质量评分

- 难度准确性: 25分
- 选项质量: 30分
- 解析质量: 20分
- 知识准确性: 15分
- 教学价值: 10分

质量阈值:
- 75分: 基线可接受
- 85+分: 高质量,保存为模板

## 学习流程

1. 检索同难度高质量题目(85+分)
2. 分析题目模式和最佳实践
3. 注入学习上下文到生成prompt
4. 生成新题目并评分
5. 85+分题目保存为模板供未来学习

## 测试

```bash
python -m app.services.quiz.test_integration
```

## 参考资料

- 统一学习框架: `app/services/learning/`
- 质量评分类: `quality_scorers.py`
- 模板服务: `template_service.py`
