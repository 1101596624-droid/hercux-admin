# HERCU 课程打包指南

## 📦 概述

HERCU 采用**"成品包"**模式进行课程接入。课程制作者在外部工具中完成课程开发后，将课程打包成标准格式，通过 API 上传到 HERCU 系统。

### 核心理念

- **生产与消费解耦**：课程制作在外部完成，HERCU 只负责分发和交互
- **标准化接入**：统一的 JSON 格式，确保兼容性
- **即插即用**：前端组件根据配置自动加载，无需修改代码

---

## 📋 课程包结构

### 基本组成

一个完整的课程包包含：

1. **course_manifest.json** - 核心配置文件（必需）
2. **/assets** - 媒体资源文件夹（可选）
   - 视频文件
   - 图片文件
3. **/sim_configs** - 模拟器配置文件（可选）

### 推荐做法

- **小文件**：直接包含在 manifest 中
- **大文件**：上传到云存储（AWS S3/阿里云 OSS），manifest 中只存储 URL

---

## 📝 Manifest 文件格式

### 完整示例

```json
{
  "courseName": "运动生物力学基础",
  "courseDescription": "深入理解人体运动的力学原理",
  "difficulty": "beginner",
  "instructor": "Dr. Zhang Wei",
  "tags": ["biomechanics", "physics"],
  "durationHours": 12.5,
  "thumbnailUrl": "https://example.com/thumbnail.jpg",
  "packageVersion": "1.0",
  "createdAt": "2026-01-17T00:00:00Z",
  "author": "Content Team",
  "nodes": [
    {
      "nodeId": "node_01",
      "type": "video",
      "componentId": "video-player",
      "title": "第1节：力的基本概念",
      "description": "理解力的定义和三要素",
      "sequence": 1,
      "parentId": null,
      "timelineConfig": {
        "steps": [...]
      },
      "unlockCondition": {
        "type": "none"
      },
      "estimatedMinutes": 10,
      "tags": ["video", "fundamentals"]
    }
  ]
}
```

### 字段说明

#### 课程元数据

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| courseName | string | ✅ | 课程名称 |
| courseDescription | string | ❌ | 课程描述 |
| difficulty | string | ✅ | 难度：beginner/intermediate/advanced/expert |
| instructor | string | ❌ | 讲师姓名 |
| tags | string[] | ❌ | 课程标签 |
| durationHours | number | ❌ | 预计总时长（小时） |
| thumbnailUrl | string | ❌ | 课程封面图 URL |
| packageVersion | string | ❌ | 包格式版本（默认 1.0） |
| createdAt | string | ❌ | 创建时间（ISO 8601） |
| author | string | ❌ | 作者 |
| nodes | Node[] | ✅ | 课程节点列表 |

#### 节点配置 (Node)

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| nodeId | string | ✅ | 唯一节点 ID |
| type | string | ✅ | 节点类型（见下表） |
| componentId | string | ✅ | 前端组件 ID |
| title | string | ✅ | 节点标题 |
| description | string | ❌ | 节点描述 |
| sequence | number | ✅ | 同级排序序号 |
| parentId | string | ❌ | 父节点 ID（树形结构） |
| timelineConfig | Timeline | ❌ | 时间轴配置 |
| unlockCondition | Unlock | ❌ | 解锁条件 |
| guidePrompt | string | ❌ | AI 引导语 |
| estimatedMinutes | number | ❌ | 预计完成时间（分钟） |
| tags | string[] | ❌ | 节点标签 |

#### 节点类型 (type)

| 类型 | 说明 | 前端组件示例 |
|------|------|--------------|
| video | 视频课程 | video-player |
| simulator | 交互式模拟器 | force-vector-sim, projectile-motion |
| quiz | 测验/练习 | quiz-panel |
| reading | 文本阅读 | text-reader, markdown-viewer |
| practice | 综合练习 | practice-quiz |

---

## ⏱️ Timeline 配置

Timeline 定义了一个节点内的多步骤学习流程。

### 结构

```json
{
  "timelineConfig": {
    "steps": [
      {
        "stepId": "step-1",
        "type": "video",
        "videoUrl": "https://...",
        "duration": 300,
        "pauseAt": [120, 240],
        "aiPromptAtPause": "你理解了吗？"
      },
      {
        "stepId": "step-2",
        "type": "quiz",
        "question": "问题内容",
        "options": ["A", "B", "C"],
        "correctAnswer": 0
      }
    ]
  }
}
```

### Step 类型

#### 1. Video Step

```json
{
  "stepId": "step-1",
  "type": "video",
  "videoUrl": "https://example.com/video.mp4",
  "duration": 300,
  "pauseAt": [120, 240],
  "aiPromptAtPause": "理解了吗？",
  "guidePrompt": "观看视频并思考..."
}
```

#### 2. Simulator Step

```json
{
  "stepId": "step-2",
  "type": "simulator",
  "simulatorId": "force-vector-sim",
  "props": {
    "force1": {"magnitude": 10, "angle": 0},
    "force2": {"magnitude": 10, "angle": 90}
  },
  "completionCriteria": {
    "type": "attempts",
    "minAttempts": 3
  },
  "guidePrompt": "尝试不同的参数..."
}
```

#### 3. Quiz Step

```json
{
  "stepId": "step-3",
  "type": "quiz",
  "question": "什么角度射程最远？",
  "options": ["30°", "45°", "60°", "90°"],
  "correctAnswer": 1,
  "guidePrompt": "回忆刚才的实验结果"
}
```

#### 4. Text Step

```json
{
  "stepId": "step-4",
  "type": "text",
  "content": "# 标题\n\n这是 Markdown 格式的文本内容...",
  "guidePrompt": "仔细阅读这段内容"
}
```

---

## 🔓 解锁条件

控制节点的解锁逻辑。

### 类型

#### 1. 无条件解锁

```json
{
  "unlockCondition": {
    "type": "none"
  }
}
```

#### 2. 完成前一个节点

```json
{
  "unlockCondition": {
    "type": "previous_complete"
  }
}
```

#### 3. 完成所有指定节点

```json
{
  "unlockCondition": {
    "type": "all_complete",
    "nodeIds": ["node_01", "node_02", "node_03"]
  }
}
```

#### 4. 手动解锁（付费等）

```json
{
  "unlockCondition": {
    "type": "manual"
  }
}
```

---

## 🌳 树形结构

使用 `parentId` 创建章节-课程的层级关系。

### 示例

```json
{
  "nodes": [
    {
      "nodeId": "chapter_1",
      "type": "reading",
      "title": "第一章：基础",
      "parentId": null,
      "sequence": 1
    },
    {
      "nodeId": "lesson_1_1",
      "type": "video",
      "title": "1.1 概念介绍",
      "parentId": "chapter_1",
      "sequence": 1
    },
    {
      "nodeId": "lesson_1_2",
      "type": "simulator",
      "title": "1.2 实践练习",
      "parentId": "chapter_1",
      "sequence": 2
    }
  ]
}
```

渲染效果：
```
📖 第一章：基础
  ├─ 🎥 1.1 概念介绍
  └─ 🎮 1.2 实践练习
```

---

## 🚀 上传流程

### 1. 验证包格式

```bash
POST /api/v1/internal/ingestion/validate
Content-Type: application/json

{
  "courseName": "...",
  "difficulty": "beginner",
  "nodes": [...]
}
```

响应：
```json
{
  "isValid": true,
  "errors": [],
  "warnings": ["No thumbnail URL provided"],
  "nodeCount": 20,
  "estimatedDuration": 8.5
}
```

### 2. 上传课程包

```bash
POST /api/v1/internal/ingestion/ingest
Content-Type: application/json

{
  "manifest": {
    "courseName": "...",
    "nodes": [...]
  },
  "publishImmediately": false
}
```

响应：
```json
{
  "success": true,
  "courseId": 123,
  "nodesCreated": 20,
  "message": "Successfully ingested course '...' with 20 nodes"
}
```

### 3. 检查课程是否存在

```bash
GET /api/v1/internal/ingestion/course/{courseName}/exists
```

### 4. 删除课程（谨慎）

```bash
DELETE /api/v1/internal/ingestion/course/{courseId}
```

---

## 📚 完整示例

查看 `examples/` 目录：

1. **course_package_example.json** - 10个节点的示例课程
2. **course_package_20_nodes.json** - 20个节点的完整课程

### 使用示例

```bash
# 1. 验证
curl -X POST http://localhost:8000/api/v1/internal/ingestion/validate \
  -H "Content-Type: application/json" \
  -d @examples/course_package_20_nodes.json

# 2. 上传
curl -X POST http://localhost:8000/api/v1/internal/ingestion/ingest-simple \
  -H "Content-Type: application/json" \
  -d @examples/course_package_20_nodes.json
```

---

## ✅ 最佳实践

### 1. 命名规范

- **nodeId**: 使用有意义的 ID，如 `chapter_1`, `lesson_1_1`
- **componentId**: 与前端组件名称对应
- **stepId**: 使用 `step-1`, `step-2` 等

### 2. 资源管理

- **视频**: 上传到 CDN，使用 HTTPS URL
- **图片**: 压缩后上传，推荐 WebP 格式
- **大小**: 单个视频不超过 500MB

### 3. 内容组织

- **章节**: 使用 `reading` 类型作为章节介绍
- **顺序**: 合理设置 `sequence` 确保学习路径清晰
- **时长**: 单个节点控制在 5-20 分钟

### 4. AI 引导

- 每个节点设置 `guidePrompt`
- 视频暂停点设置 `aiPromptAtPause`
- 提示语要具体、有针对性

### 5. 解锁逻辑

- 第一个节点使用 `type: "none"`
- 后续节点使用 `type: "previous_complete"`
- 章节测试使用 `type: "all_complete"`

---

## 🐛 常见问题

### Q: 如何处理大型视频文件？

A: 不要将视频包含在 JSON 中。上传到云存储后，在 `videoUrl` 中使用 URL。

### Q: 可以修改已上传的课程吗？

A: 目前需要删除后重新上传。未来会支持增量更新。

### Q: 如何测试课程包？

A: 使用 `/validate` 端点先验证，确保没有错误后再上传。

### Q: 支持哪些视频格式？

A: 推荐 MP4 (H.264)，前端播放器支持大多数常见格式。

### Q: 节点数量有限制吗？

A: 没有硬性限制，但建议单个课程不超过 50 个节点。

---

## 📖 相关文档

- [API 文档](http://localhost:8000/docs) - 完整的 API 参考
- [DATABASE.md](DATABASE.md) - 数据库结构说明
- [工程师执行手册](../HERCU-工程师执行手册.md) - 开发指南

---

## 🔧 开发工具

### Python 脚本示例

```python
import requests
import json

# 读取课程包
with open('course_package.json', 'r', encoding='utf-8') as f:
    manifest = json.load(f)

# 验证
response = requests.post(
    'http://localhost:8000/api/v1/internal/ingestion/validate',
    json=manifest
)
print(response.json())

# 上传
if response.json()['isValid']:
    response = requests.post(
        'http://localhost:8000/api/v1/internal/ingestion/ingest-simple',
        json=manifest
    )
    print(response.json())
```

### JavaScript 示例

```javascript
const fs = require('fs');
const axios = require('axios');

// 读取课程包
const manifest = JSON.parse(
  fs.readFileSync('course_package.json', 'utf8')
);

// 上传
axios.post(
  'http://localhost:8000/api/v1/internal/ingestion/ingest-simple',
  manifest
).then(response => {
  console.log(response.data);
}).catch(error => {
  console.error(error.response.data);
});
```

---

**需要帮助？** 查看 [API 文档](http://localhost:8000/docs) 或联系开发团队。
