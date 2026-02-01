#!/bin/bash

# 恢复原始文件的脚本

echo "↩️  HERCU 前端优化恢复脚本"
echo "================================"
echo ""

# 检查是否在正确的目录
if [ ! -f "package.json" ]; then
  echo "❌ 错误: 请在项目根目录运行此脚本"
  exit 1
fi

echo "🔄 恢复原始文件..."

# 恢复配置
if [ -f "next.config.original.js" ]; then
  cp next.config.original.js next.config.js
  echo "✅ 已恢复 next.config.js"
fi

# 恢复页面文件
if [ -f "backups/courses-page.original.tsx" ]; then
  cp "backups/courses-page.original.tsx" "app/(main)/courses/page.tsx"
  echo "✅ 已恢复 courses/page.tsx"
fi

if [ -f "backups/learn-page.original.tsx" ]; then
  cp "backups/learn-page.original.tsx" "app/(main)/courses/[courseId]/learn/page.tsx"
  echo "✅ 已恢复 learn/page.tsx"
fi

if [ -f "backups/training-page.original.tsx" ]; then
  cp "backups/training-page.original.tsx" "app/(main)/training/page.tsx"
  echo "✅ 已恢复 training/page.tsx"
fi

echo ""
echo "✅ 已恢复原始文件"
echo ""
