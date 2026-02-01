# HERCU 后台数据库文档

## 一、枚举类型定义

### 1. DifficultyLevel (课程难度)
| 值 | 含义 |
|---|---|
| `beginner` | 初级 |
| `intermediate` | 中级 |
| `advanced` | 高级 |
| `expert` | 专家级 |

### 2. NodeType (节点类型)
| 值 | 含义 |
|---|---|
| `video` | 视频 |
| `simulator` | 模拟器 |
| `quiz` | 测验 |
| `reading` | 阅读材料 |
| `practice` | 练习 |
| `lesson` | 课程 |

### 3. NodeStatus (学习状态)
| 值 | 含义 |
|---|---|
| `locked` | 锁定（未解锁） |
| `unlocked` | 已解锁（可学习） |
| `in_progress` | 学习中 |
| `completed` | 已完成 |

### 4. BadgeCategory (勋章分类)
| 值 | 含义 |
|---|---|
| `learning` | 学习类 |
| `persistence` | 坚持类 |
| `practice` | 练习类 |
| `quiz` | 测验类 |
| `special` | 特殊类 |

### 5. BadgeRarity (勋章稀有度)
| 值 | 含义 |
|---|---|
| `common` | 普通 |
| `rare` | 稀有 |
| `epic` | 史诗 |
| `legendary` | 传说 |

---

## 二、核心数据表

### 1. users (用户表)
| 字段名 | 类型 | 说明 |
|--------|------|------|
| `id` | Integer | 主键，自增ID |
| `email` | String(255) | 邮箱，唯一索引 |
| `username` | String(100) | 用户名，唯一索引 |
| `hashed_password` | String(255) | 加密后的密码 |
| `full_name` | String(255) | 全名/昵称 |
| `avatar_url` | String(500) | 头像URL |
| `is_active` | Integer | 是否激活 (0/1) |
| `is_premium` | Integer | 是否付费用户 (0/1) |
| `is_admin` | Integer | 是否管理员 (0/1) |
| `total_usage_seconds` | Integer | 累计使用时长（秒） |
| `total_tokens_used` | Integer | 累计消耗 Token 数 |
| `total_input_tokens` | Integer | 累计输入 Token |
| `total_output_tokens` | Integer | 累计输出 Token |
| `created_at` | DateTime | 创建时间 |
| `updated_at` | DateTime | 更新时间 |

---

### 2. courses (课程表)
| 字段名 | 类型 | 说明 |
|--------|------|------|
| `id` | Integer | 主键，自增ID |
| `name` | String(255) | 课程名称 |
| `description` | Text | 课程描述 |
| `difficulty` | Enum | 难度等级 (DifficultyLevel) |
| `tags` | JSON | 标签数组，如 `["biomechanics", "strength"]` |
| `instructor` | String(255) | 讲师名称 |
| `duration_hours` | Float | 预计学习时长（小时） |
| `thumbnail_url` | String(500) | 封面图URL |
| `is_published` | Integer | 是否已发布 (0/1) |
| `created_at` | DateTime | 创建时间 |
| `updated_at` | DateTime | 更新时间 |

---

### 3. course_nodes (课程节点表)
| 字段名 | 类型 | 说明 |
|--------|------|------|
| `id` | Integer | 主键，自增ID |
| `course_id` | Integer | 外键，关联 courses.id |
| `parent_id` | Integer | 父节点ID（支持树形结构） |
| `node_id` | String(100) | 节点唯一标识，如 `"node_biomech_01"` |
| `type` | Enum | 节点类型 (NodeType) |
| `component_id` | String(100) | 组件ID，如 `"force-balance-sim"` |
| `title` | String(255) | 节点标题 |
| `description` | Text | 节点描述 |
| `sequence` | Integer | 同级节点排序序号 |
| `content` | JSON | 课程内容（V2格式） |
| `config` | JSON | 课程配置 |
| `timeline_config` | JSON | 时间线配置 `{"steps": [...]}` |
| `unlock_condition` | JSON | 解锁条件，如 `{"type": "previous_complete"}` |
| `created_at` | DateTime | 创建时间 |
| `updated_at` | DateTime | 更新时间 |

---

### 4. learning_progress (学习进度表) - 勋章解锁核心数据源
| 字段名 | 类型 | 说明 |
|--------|------|------|
| `id` | Integer | 主键，自增ID |
| `user_id` | Integer | 外键，关联 users.id |
| `node_id` | Integer | 外键，关联 course_nodes.id |
| `status` | Enum | 学习状态 (NodeStatus) |
| `completion_percentage` | Float | 完成百分比 (0.0-100.0) |
| `time_spent_seconds` | Integer | 学习时长（秒） |
| `last_accessed` | DateTime | 最后访问时间 |
| `completed_at` | DateTime | 完成时间 |
| `created_at` | DateTime | 创建时间 |
| `updated_at` | DateTime | 更新时间 |

**勋章解锁可计算的指标：**
- `completed_nodes` - 从 status=completed 的记录数计算
- `total_hours` - 从 time_spent_seconds 汇总计算
- `total_learning_days` - 从 last_accessed 去重日期计算
- `current_streak` / `max_streak` - 从 last_accessed 连续日期计算

---

### 5. user_courses (用户课程关联表)
| 字段名 | 类型 | 说明 |
|--------|------|------|
| `id` | Integer | 主键，自增ID |
| `user_id` | Integer | 外键，关联 users.id |
| `course_id` | Integer | 外键，关联 courses.id |
| `enrolled_at` | DateTime | 报名时间 |
| `last_accessed` | DateTime | 最后访问时间 |
| `completed_at` | DateTime | 课程完成时间 |
| `is_favorite` | Integer | 是否收藏 (0/1) |

---

### 6. learning_statistics (每日学习统计表)
| 字段名 | 类型 | 说明 |
|--------|------|------|
| `id` | Integer | 主键，自增ID |
| `user_id` | Integer | 外键，关联 users.id |
| `date` | DateTime | 统计日期 |
| `total_time_seconds` | Integer | 当日学习时长（秒） |
| `nodes_completed` | Integer | 当日完成节点数 |
| `streak_days` | Integer | 连续学习天数 |

---

### 7. simulator_results (模拟器结果表)
| 字段名 | 类型 | 说明 |
|--------|------|------|
| `id` | Integer | 主键，自增ID |
| `user_id` | Integer | 外键，关联 users.id |
| `node_id` | Integer | 外键，关联 course_nodes.id |
| `session_id` | String(100) | 会话唯一标识 |
| `result_data` | JSON | 模拟器结果数据 |
| `score` | Float | 得分 (0-100) |
| `time_spent_seconds` | Integer | 耗时（秒） |
| `completed` | Integer | 是否完成 (0/1) |
| `created_at` | DateTime | 创建时间 |
| `updated_at` | DateTime | 更新时间 |

---

### 8. chat_history (AI对话历史表)
| 字段名 | 类型 | 说明 |
|--------|------|------|
| `id` | Integer | 主键，自增ID |
| `user_id` | Integer | 外键，关联 users.id |
| `node_id` | Integer | 外键，关联 course_nodes.id |
| `role` | String(20) | 角色：`user` 或 `assistant` |
| `content` | Text | 消息内容 |
| `created_at` | DateTime | 创建时间 |

---

### 9. training_plans (训练计划表)
| 字段名 | 类型 | 说明 |
|--------|------|------|
| `id` | Integer | 主键，自增ID |
| `user_id` | Integer | 外键，关联 users.id |
| `title` | String(255) | 计划标题 |
| `plan_data` | JSON | 计划数据（周期、周、训练内容） |
| `status` | String(50) | 状态：`active`/`completed`/`archived` |
| `start_date` | DateTime | 开始日期 |
| `end_date` | DateTime | 结束日期 |
| `created_at` | DateTime | 创建时间 |
| `updated_at` | DateTime | 更新时间 |

---

### 10. token_usage (Token使用记录表)
| 字段名 | 类型 | 说明 |
|--------|------|------|
| `id` | Integer | 主键，自增ID |
| `user_id` | Integer | 外键，关联 users.id（可为空） |
| `feature` | String(100) | 功能名称：`ai_training_plan`, `ai_tutor` 等 |
| `model` | String(100) | 模型名称，如 `claude-sonnet-4-20250514` |
| `input_tokens` | Integer | 输入 Token 数 |
| `output_tokens` | Integer | 输出 Token 数 |
| `total_tokens` | Integer | 总 Token 数 |
| `plan_id` | String(100) | 关联的计划ID |
| `extra_data` | JSON | 额外元数据 |
| `created_at` | DateTime | 创建时间 |

---

## 三、勋章中心表

### 11. badge_configs (勋章配置表) - 管理员配置
| 字段名 | 类型 | 说明 |
|--------|------|------|
| `id` | String(50) | 主键，snake_case 唯一标识，如 `"first_step"` |
| `name` | String(100) | 勋章名称（中文） |
| `name_en` | String(100) | 勋章名称（英文） |
| `icon` | String(10) | 图标（emoji），如 `"🎯"` |
| `description` | Text | 勋章描述 |
| `category` | Enum | 分类 (BadgeCategory) |
| `rarity` | Enum | 稀有度 (BadgeRarity) |
| `points` | Integer | 积分值 |
| `condition` | JSON | 解锁条件（见下方说明） |
| `is_active` | Integer | 是否启用 (0/1) |
| `sort_order` | Integer | 排序序号 |
| `created_at` | DateTime | 创建时间 |
| `updated_at` | DateTime | 更新时间 |
| `created_by` | String(50) | 创建者 |

**condition 字段格式：**
```json
// 计数器类型 - 完成节点数
{"type": "counter", "metric": "completed_nodes", "target": 10}

// 连续天数类型 - 当前连续学习天数
{"type": "streak", "target": 7}

// 历史最长连续天数
{"type": "max_streak", "target": 30}

// 时间类型 - 学习时长（小时）
{"type": "time_based", "target": 10}

// 累计天数类型 - 总学习天数
{"type": "days", "target": 30}

// 课程类型 - 完成课程数
{"type": "courses", "target": 3}

// 通用阈值类型
{"type": "threshold", "metric": "completed_quizzes", "target": 5}
```

**支持的 metric 值：**
| metric | 含义 | 数据来源 |
|--------|------|----------|
| `completed_nodes` | 完成的节点数 | learning_progress |
| `nodes_completed` | 同上（别名） | learning_progress |
| `total_hours` | 学习时长（小时） | learning_progress.time_spent_seconds |
| `learning_hours` | 同上（别名） | learning_progress.time_spent_seconds |
| `total_learning_days` | 累计学习天数 | learning_progress.last_accessed |
| `learning_days` | 同上（别名） | learning_progress.last_accessed |
| `current_streak` | 当前连续天数 | learning_progress.last_accessed |
| `streak_days` | 同上（别名） | learning_progress.last_accessed |
| `max_streak` | 历史最长连续天数 | learning_progress.last_accessed |
| `completed_courses` | 完成的课程数 | learning_progress + course_nodes |
| `courses_completed` | 同上（别名） | learning_progress + course_nodes |
| `enrolled_courses` | 已报名课程数 | learning_progress + course_nodes |
| `completed_quizzes` | 完成的测验数 | learning_progress + course_nodes.type |
| `quizzes_completed` | 同上（别名） | learning_progress + course_nodes.type |
| `completed_simulators` | 完成的模拟器数 | learning_progress + course_nodes.type |
| `simulators_completed` | 同上（别名） | learning_progress + course_nodes.type |

---

### 12. user_badges (用户勋章解锁记录表)
| 字段名 | 类型 | 说明 |
|--------|------|------|
| `id` | Integer | 主键，自增ID |
| `user_id` | Integer | 外键，关联 users.id |
| `badge_id` | String(50) | 外键，关联 badge_configs.id |
| `unlocked_at` | DateTime | 解锁时间 |

**唯一索引：** `(user_id, badge_id)`

---

### 13. skill_tree_configs (技能树配置表)
| 字段名 | 类型 | 说明 |
|--------|------|------|
| `id` | String(50) | 主键，如 `"biomechanics"` |
| `name` | String(100) | 技能树名称（中文） |
| `name_en` | String(100) | 技能树名称（英文） |
| `icon` | String(10) | 图标（emoji） |
| `color` | String(20) | 颜色（hex），如 `"#3B82F6"` |
| `description` | Text | 描述 |
| `match_rules` | JSON | 匹配规则 |
| `level_thresholds` | JSON | 等级阈值，默认 `[0, 50, 150, 300, 500]` |
| `prerequisites` | JSON | 前置依赖 |
| `unlocks` | JSON | 解锁的技能树 |
| `is_advanced` | Integer | 是否高级技能树 (0/1) |
| `is_active` | Integer | 是否启用 (0/1) |
| `sort_order` | Integer | 排序序号 |
| `created_at` | DateTime | 创建时间 |
| `updated_at` | DateTime | 更新时间 |

**match_rules 格式：**
```json
{"domains": ["biomechanics"], "subdomains": ["joint", "muscle"]}
```

**prerequisites 格式：**
```json
[{"treeId": "biomechanics", "requiredLevel": 2}]
```

---

### 14. user_skill_progress (用户技能进度表)
| 字段名 | 类型 | 说明 |
|--------|------|------|
| `id` | Integer | 主键，自增ID |
| `user_id` | Integer | 外键，关联 users.id |
| `skill_tree_id` | String(50) | 外键，关联 skill_tree_configs.id |
| `current_points` | Integer | 当前积分 |
| `current_level` | Integer | 当前等级 |
| `sub_skills` | JSON | 子技能进度 |
| `last_updated` | DateTime | 最后更新时间 |

**唯一索引：** `(user_id, skill_tree_id)`

---

### 15. skill_achievement_configs (技能成就配置表)
| 字段名 | 类型 | 说明 |
|--------|------|------|
| `id` | String(50) | 主键 |
| `name` | String(100) | 成就名称（中文） |
| `name_en` | String(100) | 成就名称（英文） |
| `icon` | String(10) | 图标（emoji） |
| `description` | Text | 描述 |
| `points` | Integer | 积分值，默认 50 |
| `condition` | JSON | 解锁条件 |
| `is_active` | Integer | 是否启用 (0/1) |
| `sort_order` | Integer | 排序序号 |
| `created_at` | DateTime | 创建时间 |
| `updated_at` | DateTime | 更新时间 |

---

### 16. user_skill_achievements (用户技能成就解锁记录表)
| 字段名 | 类型 | 说明 |
|--------|------|------|
| `id` | Integer | 主键，自增ID |
| `user_id` | Integer | 外键，关联 users.id |
| `achievement_id` | String(50) | 外键，关联 skill_achievement_configs.id |
| `unlocked_at` | DateTime | 解锁时间 |

**唯一索引：** `(user_id, achievement_id)`

---

## 四、标签与领域管理表

### 17. tag_dictionary (标签字典表)
| 字段名 | 类型 | 说明 |
|--------|------|------|
| `id` | String(50) | 主键 |
| `type` | String(20) | 类型：`domain` 或 `subdomain` |
| `name` | String(100) | 标签名称（中文） |
| `name_en` | String(100) | 标签名称（英文） |
| `icon` | String(10) | 图标（仅 domain） |
| `color` | String(20) | 颜色（仅 domain） |
| `parent_id` | String(50) | 父标签ID（subdomain 关联 domain） |
| `description` | Text | 描述 |
| `is_registered` | Integer | 是否已关联技能树 (0/1) |
| `is_active` | Integer | 是否启用 (0/1) |
| `created_at` | DateTime | 创建时间 |

---

### 18. pending_domains (待审核领域表)
| 字段名 | 类型 | 说明 |
|--------|------|------|
| `domain` | String(50) | 主键，领域名称 |
| `node_count` | Integer | 相关节点数量 |
| `completed_users` | Integer | 完成该领域的用户数 |
| `first_seen` | DateTime | 首次发现时间 |
| `status` | String(20) | 状态：`pending`/`approved`/`rejected` |
| `reviewed_at` | DateTime | 审核时间 |
| `reviewed_by` | String(50) | 审核人 |
| `reject_reason` | Text | 拒绝原因 |

---

## 五、Studio 课程生成表

### 19. studio_processors (Studio处理器表)
| 字段名 | 类型 | 说明 |
|--------|------|------|
| `id` | String(100) | 主键，如 `"default"`, `"academic"` |
| `name` | String(255) | 处理器名称 |
| `description` | Text | 描述 |
| `version` | String(50) | 版本号 |
| `author` | String(255) | 作者 |
| `tags` | JSON | 标签数组 |
| `color` | String(50) | 颜色 |
| `icon` | String(50) | 图标名称 |
| `system_prompt` | Text | AI系统提示词 |
| `enabled` | Integer | 是否启用 (0/1) |
| `display_order` | Integer | 显示顺序 |
| `is_official` | Integer | 是否官方 (0/1) |
| `is_custom` | Integer | 是否自定义 (0/1) |
| `created_at` | DateTime | 创建时间 |
| `updated_at` | DateTime | 更新时间 |

---

### 20. studio_packages (Studio课程包表)
| 字段名 | 类型 | 说明 |
|--------|------|------|
| `id` | String(100) | 主键，UUID |
| `title` | String(255) | 课程包标题 |
| `description` | Text | 描述 |
| `source_info` | Text | 源材料信息 |
| `style` | String(100) | 生成风格 |
| `status` | Enum | 状态：`draft`/`published`/`archived` |
| `meta` | JSON | 元数据（V2格式） |
| `lessons` | JSON | 课程数组 |
| `edges` | JSON | 边（依赖关系）数组 |
| `global_ai_config` | JSON | AI配置 |
| `total_lessons` | Integer | 总课程数 |
| `estimated_hours` | Float | 预计时长 |
| `processor_id` | String(100) | 外键，关联 studio_processors.id |
| `course_id` | Integer | 外键，关联 courses.id（导入后） |
| `created_at` | DateTime | 创建时间 |
| `updated_at` | DateTime | 更新时间 |

---

## 六、用户画像表

### 21. user_profiles (用户特征画像表)
| 字段名 | 类型 | 说明 |
|--------|------|------|
| `id` | Integer | 主键，自增ID |
| `user_id` | Integer | 外键，关联 users.id（唯一） |
| `learning_style` | JSON | 学习风格，如 `{"visual": 0.3, "auditory": 0.2, ...}` |
| `knowledge_levels` | JSON | 知识水平，如 `{"biomechanics": "intermediate", ...}` |
| `interests` | JSON | 兴趣领域数组 |
| `strengths` | JSON | 优势数组 |
| `weaknesses` | JSON | 弱点数组 |
| `communication_style` | String(50) | 沟通风格：`detailed`/`concise`/`questioning`/`passive` |
| `engagement_level` | String(50) | 参与度：`high`/`medium`/`low` |
| `question_patterns` | JSON | 提问模式统计 |
| `learning_pace` | String(50) | 学习节奏：`fast`/`moderate`/`slow` |
| `personality_traits` | JSON | 性格特征数组 |
| `recommended_approach` | Text | AI建议的教学方式 |
| `analysis_summary` | Text | AI分析总结 |
| `messages_analyzed` | Integer | 已分析消息数 |
| `last_analyzed_at` | DateTime | 最后分析时间 |
| `analysis_version` | String(20) | 分析算法版本 |
| `created_at` | DateTime | 创建时间 |
| `updated_at` | DateTime | 更新时间 |

---

## 七、旧版成就表（已弃用）

### 22. achievements (旧版成就表)
| 字段名 | 类型 | 说明 |
|--------|------|------|
| `id` | Integer | 主键，自增ID |
| `user_id` | Integer | 外键，关联 users.id |
| `badge_id` | String(100) | 勋章ID |
| `badge_name` | String(255) | 勋章名称 |
| `badge_description` | Text | 勋章描述 |
| `rarity` | String(50) | 稀有度 |
| `icon_url` | String(500) | 图标URL |
| `unlocked_at` | DateTime | 解锁时间 |

> **注意：** 此表已被 `badge_configs` + `user_badges` 替代，保留仅为兼容性。

---

## 八、表关系图

```
users
  ├── learning_progress (1:N)
  ├── user_courses (1:N)
  ├── training_plans (1:N)
  ├── chat_history (1:N)
  ├── learning_statistics (1:N)
  ├── simulator_results (1:N)
  ├── token_usage (1:N)
  ├── user_badges (1:N)
  ├── user_skill_progress (1:N)
  ├── user_skill_achievements (1:N)
  ├── user_profiles (1:1)
  └── achievements (1:N, 已弃用)

courses
  ├── course_nodes (1:N)
  ├── user_courses (1:N)
  └── studio_packages (1:1)

course_nodes
  ├── learning_progress (1:N)
  ├── chat_history (1:N)
  ├── simulator_results (1:N)
  └── course_nodes (自关联, parent_id)

badge_configs
  └── user_badges (1:N)

skill_tree_configs
  └── user_skill_progress (1:N)

skill_achievement_configs
  └── user_skill_achievements (1:N)

tag_dictionary
  └── tag_dictionary (自关联, parent_id)

studio_processors
  └── studio_packages (1:N)
```
