#!/bin/bash

# 启用性能优化的快速脚本

echo "🚀 HERCU 前端性能优化启用脚本"
echo "================================"
echo ""

# 检查是否在正确的目录
if [ ! -f "package.json" ]; then
  echo "❌ 错误: 请在项目根目录运行此脚本"
  exit 1
fi

echo "📦 备份原始文件..."

# 备份原始配置
if [ -f "next.config.js" ]; then
  cp next.config.js next.config.original.js
  echo "✅ 已备份 next.config.js"
fi

# 备份页面文件
mkdir -p backups

if [ -f "app/(main)/courses/page.tsx" ]; then
  cp "app/(main)/courses/page.tsx" "backups/courses-page.original.tsx"
  echo "✅ 已备份 courses/page.tsx"
fi

if [ -f "app/(main)/courses/[courseId]/learn/page.tsx" ]; then
  cp "app/(main)/courses/[courseId]/learn/page.tsx" "backups/learn-page.original.tsx"
  echo "✅ 已备份 learn/page.tsx"
fi

if [ -f "app/(main)/training/page.tsx" ]; then
  cp "app/(main)/training/page.tsx" "backups/training-page.original.tsx"
  echo "✅ 已备份 training/page.tsx"
fi

echo ""
echo "🔄 启用优化版本..."

# 启用优化配置
if [ -f "next.config.optimized.js" ]; then
  cp next.config.optimized.js next.config.js
  echo "✅ 已启用优化后的 Next.js 配置"
fi

# 启用优化页面
if [ -f "app/(main)/courses/page.optimized.tsx" ]; then
  cp "app/(main)/courses/page.optimized.tsx" "app/(main)/courses/page.tsx"
  echo "✅ 已启用优化后的课程中心"
fi

if [ -f "app/(main)/courses/[courseId]/learn/page.optimized.tsx" ]; then
  cp "app/(main)/courses/[courseId]/learn/page.optimized.tsx" "app/(main)/courses/[courseId]/learn/page.tsx"
  echo "✅ 已启用优化后的学习工作站"
fi

if [ -f "app/(main)/training/page.optimized.tsx" ]; then
  cp "app/(main)/training/page.optimized.tsx" "app/(main)/training/page.tsx"
  echo "✅ 已启用优化后的训练计划"
fi

echo ""
echo "✨ 优化已启用！"
echo ""
echo "📝 下一步:"
echo "  1. 重新构建项目: npm run build"
echo "  2. 分析 bundle: ANALYZE=true npm run build"
echo "  3. 启动开发服务器: npm run dev"
echo ""
echo "💡 提示:"
echo "  - 原始文件已备份到 backups/ 和 *.original.* 文件"
echo "  - 查看详细文档: PERFORMANCE-OPTIMIZATION.md"
echo ""
