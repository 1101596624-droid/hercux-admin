# HERCU 课程管理 API 文档

## 📋 概述

HERCU 课程管理系统提供完整的 CRUD API，支持课程和节点的创建、读取、更新和删除操作。

---

## 🔑 API 端点总览

### 课程包上传
- `POST /api/v1/internal/ingestion/validate` - 验证课程包
- `POST /api/v1/internal/ingestion/ingest` - 上传课程包（完整版）
- `POST /api/v1/internal/ingestion/ingest-simple` - 上传课程包（简化版）

### 课程管理 (CRUD)
- `GET /api/v1/internal/ingestion/course/{course_id}` - 获取课程详情
- `PUT /api/v1/internal/ingestion/course/{course_id}` - 更新课程
- `DELETE /api/v1/internal/ingestion/course/{course_id}` - 删除课程
- `PATCH /api/v1/internal/ingestion/course/{course_id}/publish` - 发布/取消发布课程
- `GET /api/v1/internal/ingestion/course/{course_name}/exists` - 检查课程是否存在

### 节点管理 (CRUD)
- `GET /api/v1/internal/ingestion/node/{node_id}` - 获取节点详情
- `PUT /api/v1/internal/ingestion/node/{node_id}` - 更新节点
- `DELETE /api/v1/internal/ingestion/node/{node_id}` - 删除节点
- `POST /api/v1/internal/ingestion/course/{course_id}/node` - 添加新节点

---

## 📖 详细 API 说明

### 1. 获取课程详情

**GET** `/api/v1/internal/ingestion/course/{course_id}`

获取课程的完整信息，包括所有节点。

**响应示例：**
```json
{
  "id": 1,
  "name": "运动生物力学进阶",
  "description": "深入学习人体运动的力学原理",
  "difficulty": "intermediate",
  "instructor": "Dr. Zhang Wei",
  "tags": ["biomechanics", "physics"],
  "durationHours": 8.5,
  "thumbnailUrl": "https://example.com/thumb.jpg",
  "isPublished": true,
  "createdAt": "2026-01-17T00:00:00Z",
  "nodeCount": 10,
  "nodes": [
    {
      "id": 1,
      "nodeId": "chapter_1",
      "type": "reading",
      "componentId": "chapter-intro",
      "title": "第一章：力学基础回顾",
      "description": "回顾基础力学概念",
      "sequence": 1,
      "parentId": null,
      "timelineConfig": {...},
      "unlockCondition": {"type": "none"}
    }
  ]
}
```

---

### 2. 更新课程

**PUT** `/api/v1/internal/ingestion/course/{course_id}`

更新课程的元数据。所有字段都是可选的，只更新提供的字段。

**请求体：**
```json
{
  "courseName": "运动生物力学进阶 (更新版)",
  "courseDescription": "新的课程描述",
  "difficulty": "advanced",
  "instructor": "Prof. Zhang Wei",
  "tags": ["biomechanics", "physics", "updated"],
  "durationHours": 10.0,
  "thumbnailUrl": "https://example.com/new-thumb.jpg",
  "isPublished": true
}
```

**响应示例：**
```json
{
  "success": true,
  "message": "Course 1 updated successfully",
  "course": {
    "id": 1,
    "name": "运动生物力学进阶 (更新版)",
    "difficulty": "advanced",
    ...
  }
}
```

---

### 3. 发布/取消发布课程

**PATCH** `/api/v1/internal/ingestion/course/{course_id}/publish?publish=true`

快速发布或取消发布课程。

**查询参数：**
- `publish` (boolean): `true` 发布，`false` 取消发布

**响应示例：**
```json
{
  "success": true,
  "message": "Course 1 published successfully",
  "isPublished": true
}
```

---

### 4. 删除课程

**DELETE** `/api/v1/internal/ingestion/course/{course_id}`

删除课程及其所有节点。⚠️ **此操作不可逆！**

**响应示例：**
```json
{
  "success": true,
  "message": "Course 1 deleted successfully"
}
```

---

### 5. 获取节点详情

**GET** `/api/v1/internal/ingestion/node/{node_id}`

获取单个节点的详细信息。

**响应示例：**
```json
{
  "id": 5,
  "nodeId": "lesson_1_1",
  "courseId": 1,
  "type": "video",
  "componentId": "video-player",
  "title": "1.1 力的基本概念",
  "description": "理解力的定义、单位和表示方法",
  "sequence": 1,
  "parentId": 1,
  "timelineConfig": {
    "steps": [
      {
        "stepId": "step-1",
        "type": "video",
        "videoUrl": "https://example.com/video.mp4",
        "duration": 300
      }
    ]
  },
  "unlockCondition": {"type": "previous_complete"},
  "createdAt": "2026-01-17T00:00:00Z"
}
```

---

### 6. 更新节点

**PUT** `/api/v1/internal/ingestion/node/{node_id}`

更新节点的配置。所有字段都是可选的。

**请求体：**
```json
{
  "title": "1.1 力的基本概念 (更新版)",
  "description": "新的描述",
  "sequence": 10,
  "parentId": "chapter_1",
  "timelineConfig": {
    "steps": [
      {
        "stepId": "step-1",
        "type": "video",
        "videoUrl": "https://example.com/new-video.mp4",
        "duration": 400
      }
    ]
  },
  "unlockCondition": {"type": "none"},
  "guidePrompt": "新的AI引导语",
  "estimatedMinutes": 15,
  "tags": ["updated", "video"]
}
```

**响应示例：**
```json
{
  "success": true,
  "message": "Node 'lesson_1_1' updated successfully",
  "node": {
    "id": 5,
    "nodeId": "lesson_1_1",
    "title": "1.1 力的基本概念 (更新版)",
    ...
  }
}
```

---

### 7. 删除节点

**DELETE** `/api/v1/internal/ingestion/node/{node_id}`

删除单个节点。如果节点有子节点，子节点的 `parent_id` 会被设置为 `null`。

**响应示例：**
```json
{
  "success": true,
  "message": "Node 'lesson_1_1' deleted successfully"
}
```

---

### 8. 添加新节点

**POST** `/api/v1/internal/ingestion/course/{course_id}/node`

向现有课程添加新节点。

**请求体：**
```json
{
  "nodeId": "new_lesson",
  "type": "reading",
  "componentId": "text-reader",
  "title": "新增课程：额外内容",
  "description": "这是动态添加的节点",
  "sequence": 100,
  "parentId": "chapter_1",
  "timelineConfig": {
    "steps": [
      {
        "stepId": "step-1",
        "type": "text",
        "content": "# 新内容\n\n这是新增的内容。"
      }
    ]
  },
  "unlockCondition": {"type": "previous_complete"},
  "estimatedMinutes": 10,
  "tags": ["new", "extra"]
}
```

**响应示例：**
```json
{
  "success": true,
  "message": "Node 'new_lesson' added to course 1",
  "node": {
    "id": 15,
    "nodeId": "new_lesson",
    "courseId": 1,
    ...
  }
}
```

---

## 🔄 典型使用场景

### 场景 1：更新课程标题和讲师

```bash
curl -X PUT http://localhost:8000/api/v1/internal/ingestion/course/1 \
  -H "Content-Type: application/json" \
  -d '{
    "courseName": "运动生物力学进阶 (2026版)",
    "instructor": "Prof. Li Ming"
  }'
```

### 场景 2：修改节点的时间轴配置

```bash
curl -X PUT http://localhost:8000/api/v1/internal/ingestion/node/lesson_1_1 \
  -H "Content-Type: application/json" \
  -d '{
    "timelineConfig": {
      "steps": [
        {
          "stepId": "step-1",
          "type": "video",
          "videoUrl": "https://cdn.example.com/new-video.mp4",
          "duration": 600,
          "pauseAt": [200, 400],
          "aiPromptAtPause": "你理解了吗？"
        }
      ]
    }
  }'
```

### 场景 3：发布课程

```bash
curl -X PATCH http://localhost:8000/api/v1/internal/ingestion/course/1/publish?publish=true
```

### 场景 4：添加新的练习节点

```bash
curl -X POST http://localhost:8000/api/v1/internal/ingestion/course/1/node \
  -H "Content-Type: application/json" \
  -d '{
    "nodeId": "extra_quiz",
    "type": "quiz",
    "componentId": "quiz-panel",
    "title": "额外测验",
    "sequence": 999,
    "timelineConfig": {
      "steps": [
        {
          "stepId": "q1",
          "type": "quiz",
          "question": "什么是力？",
          "options": ["矢量", "标量", "常量", "变量"],
          "correctAnswer": 0
        }
      ]
    }
  }'
```

---

## ⚠️ 注意事项

### 1. 节点 ID 唯一性
- `nodeId` 在整个系统中必须唯一
- 添加新节点时，如果 `nodeId` 已存在会返回 400 错误

### 2. 父节点引用
- 更新 `parentId` 时，必须使用 `nodeId`（字符串），不是数据库 ID
- 设置 `parentId` 为空字符串 `""` 可以移除父节点关系

### 3. 删除操作
- 删除课程会级联删除所有节点
- 删除节点会将其子节点的 `parent_id` 设置为 `null`
- 删除操作不可逆，请谨慎使用

### 4. 发布状态
- 只有 `isPublished=true` 的课程才会在前端显示
- 可以先上传课程（`publishImmediately=false`），测试后再发布

### 5. 时间轴配置
- 更新 `timelineConfig` 会完全替换原有配置
- 确保提供完整的 steps 数组

---

## 🧪 测试脚本

运行完整的 CRUD 测试：

```bash
cd backend
python scripts/test_crud_api.py
```

测试包括：
1. ✅ 创建课程
2. ✅ 读取课程
3. ✅ 更新课程
4. ✅ 读取节点
5. ✅ 更新节点
6. ✅ 添加新节点
7. ✅ 删除节点
8. ✅ 删除课程

---

## 📚 相关文档

- [课程打包指南](COURSE-PACKAGING-GUIDE.md) - 课程包格式说明
- [数据库文档](DATABASE.md) - 数据库结构
- [API 文档](http://localhost:8000/docs) - 完整的 OpenAPI 文档

---

## 🔧 Python 客户端示例

```python
import requests

BASE_URL = "http://localhost:8000/api/v1/internal/ingestion"

# 1. 获取课程
response = requests.get(f"{BASE_URL}/course/1")
course = response.json()
print(f"Course: {course['name']}")

# 2. 更新课程
response = requests.put(
    f"{BASE_URL}/course/1",
    json={
        "courseName": "新课程名称",
        "isPublished": True
    }
)
print(response.json())

# 3. 更新节点
response = requests.put(
    f"{BASE_URL}/node/lesson_1_1",
    json={
        "title": "新标题",
        "sequence": 5
    }
)
print(response.json())

# 4. 添加节点
response = requests.post(
    f"{BASE_URL}/course/1/node",
    json={
        "nodeId": "new_node",
        "type": "reading",
        "componentId": "text-reader",
        "title": "新节点",
        "sequence": 100,
        "timelineConfig": {
            "steps": [
                {
                    "stepId": "step-1",
                    "type": "text",
                    "content": "内容"
                }
            ]
        }
    }
)
print(response.json())
```

---

**需要帮助？** 访问 [API 文档](http://localhost:8000/docs) 或查看测试脚本示例。
