# 🎛️ HERCU 后台管理系统

HERCU 系统的管理后台，用于管理课程、用户、进度和系统配置。

---

## 🚀 快速启动

### 方式一：使用启动脚本（推荐）

双击运行 `start-admin.bat`

### 方式二：命令行启动

```bash
cd C:\Users\11015\Desktop\项目核心\hercux-admin
npm run dev
```

---

## 📊 系统信息

- **端口**: 3001
- **访问地址**: http://localhost:3001
- **后端 API**: http://localhost:8001/api/v1
- **框架**: Next.js 14 + TypeScript

---

## 🔧 功能模块

### 1. 仪表板 (Dashboard)
- 系统概览
- 关键指标统计
- 最近活动

**路径**: `/admin/dashboard`

### 2. 课程管理 (Courses)
- 课程列表
- 创建/编辑课程
- 课程节点管理
- 课程发布状态

**路径**: `/admin/courses`

### 3. 用户管理 (Users)
- 用户列表
- 用户详情
- 权限管理
- 学习进度查看

**路径**: `/admin/users`

### 4. 进度管理 (Progress)
- 学习进度统计
- 完成率分析
- 用户活跃度

**路径**: `/admin/progress`

---

## 🔐 认证说明

后台管理系统使用与主应用相同的认证系统：

1. **登录**: 访问 http://localhost:3001/admin/login
2. **账号**: 使用主应用的账号和密码登录
3. **Token**: 自动存储在 localStorage 的 `auth_token` 中
4. **共享认证**: 与主应用共享登录状态
5. **权限**: 登录后即可访问管理功能

---

## 📁 项目结构

```
hercux-admin/
├── app/                    # Next.js 应用目录
│   ├── admin/             # 管理页面
│   │   ├── dashboard/     # 仪表板
│   │   ├── courses/       # 课程管理
│   │   ├── users/         # 用户管理
│   │   └── progress/      # 进度管理
│   ├── layout.tsx         # 根布局
│   └── page.tsx           # 首页（重定向）
├── components/            # React 组件
├── lib/                   # 工具库
│   ├── api/              # API 客户端
│   └── utils/            # 工具函数
├── stores/               # Zustand 状态管理
├── types/                # TypeScript 类型定义
└── .env.local            # 环境配置

```

---

## 🔌 API 集成

### 配置

环境变量在 `.env.local` 中配置：

```env
NEXT_PUBLIC_API_URL=http://localhost:8001/api/v1
```

### API 客户端

使用统一的 API 客户端 (`lib/api/client.ts`)：

```typescript
import { apiClient } from '@/lib/api/client';

// GET 请求
const courses = await apiClient.get('/courses');

// POST 请求
const newCourse = await apiClient.post('/courses', courseData);

// PUT 请求
await apiClient.put(`/courses/${id}`, updates);

// DELETE 请求
await apiClient.delete(`/courses/${id}`);
```

### 认证

API 客户端自动处理认证：
- 从 localStorage 读取 `auth_token`
- 自动添加 `Authorization: Bearer <token>` 头
- Token 过期时自动跳转登录

---

## 🎨 UI 组件

使用 Tailwind CSS 构建的自定义组件库：

- **Button**: 按钮组件
- **Card**: 卡片容器
- **Table**: 数据表格
- **Modal**: 模态对话框
- **Form**: 表单组件
- **Loading**: 加载状态
- **Toast**: 消息提示

---

## 📊 状态管理

使用 Zustand 进行状态管理：

```typescript
// stores/useAdminStore.ts
import { create } from 'zustand';

export const useAdminStore = create((set) => ({
  courses: [],
  users: [],
  fetchCourses: async () => {
    const courses = await apiClient.get('/courses');
    set({ courses });
  },
}));
```

---

## 🔄 与主应用的关系

### 共享后端

- 主应用 (hercux): http://localhost:3000
- 后台管理 (hercux-admin): http://localhost:3001
- 共享后端 API: http://localhost:8001

### 数据同步

- 使用相同的数据库
- 使用相同的 API 端点
- 实时数据更新

### 认证共享

- 使用相同的 JWT token
- 共享 localStorage 中的认证信息
- 统一的权限系统

---

## 🛠️ 开发指南

### 添加新页面

1. 在 `app/admin/` 下创建新目录
2. 创建 `page.tsx` 文件
3. 添加路由和导航

### 添加新 API

1. 在 `lib/api/` 下创建新文件
2. 使用 `apiClient` 封装请求
3. 导出 API 函数

### 添加新组件

1. 在 `components/` 下创建组件
2. 使用 TypeScript 定义 props
3. 导出组件

---

## 🐛 故障排除

### 端口被占用

```bash
# 查找占用 3001 端口的进程
netstat -ano | findstr :3001

# 结束进程
taskkill //F //PID <进程ID>
```

### API 连接失败

1. 确认后端服务运行在 8001 端口
2. 检查 `.env.local` 配置
3. 查看浏览器控制台错误

### 认证失败

1. 确认已登录主应用
2. 检查 localStorage 中的 `auth_token`
3. Token 可能已过期，重新登录

---

## 📝 待办事项

- [ ] 添加课程内容编辑器
- [ ] 实现批量操作功能
- [ ] 添加数据导出功能
- [ ] 实现实时通知
- [ ] 添加系统日志查看
- [ ] 优化移动端适配

---

## 🎯 系统要求

- Node.js 18+
- npm 或 yarn
- 现代浏览器（Chrome, Firefox, Edge）

---

## 📞 技术支持

如遇问题，请查看：
1. 主项目 README.md
2. 后端 API 文档: http://localhost:8001/docs
3. 浏览器开发者工具控制台

---

**版本**: 1.0.0
**最后更新**: 2026-01-19
**状态**: ✅ 开发中
