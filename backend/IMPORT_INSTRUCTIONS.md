# HTML模板库导入说明

## 状态
- ✅ SQL文件已生成: `import_templates.sql` (19,903行)
- ✅ 24个HTML模板准备就绪
- ⏳ 等待导入到数据库

## 问题
从本地客户端无法直接连接到数据库服务器 (106.14.180.66:5432)
- 可能原因: 防火墙限制、需要在服务器本地执行

## 导入方案

### 方案1: 在服务器本地执行 (推荐)

如果您有服务器SSH访问权限:

```bash
# 1. 上传SQL文件到服务器
scp F:/9/hercux-admin/backend/import_templates.sql user@106.14.180.66:/tmp/

# 2. SSH登录到服务器
ssh user@106.14.180.66

# 3. 在服务器上执行导入
PGPASSWORD='Hercu2026Secure' psql -U hercu -d hercu_db -h localhost -f /tmp/import_templates.sql

# 4. 验证导入
PGPASSWORD='Hercu2026Secure' psql -U hercu -d hercu_db -h localhost -c "
SELECT subject, COUNT(*) as count, AVG(quality_score) as avg_score
FROM simulator_templates
WHERE quality_score = 75
GROUP BY subject
ORDER BY subject;
"
```

### 方案2: 使用SSH隧道

如果您可以SSH但需要本地工具:

```bash
# 1. 建立SSH隧道 (在新终端保持运行)
ssh -L 5432:localhost:5432 user@106.14.180.66

# 2. 在另一个终端使用本地PostgreSQL客户端
PGPASSWORD='Hercu2026Secure' psql -U hercu -d hercu_db -h localhost -f F:/9/hercux-admin/backend/import_templates.sql
```

### 方案3: 使用pgAdmin或其他GUI工具

1. 打开pgAdmin
2. 连接到数据库: `hercu_db@106.14.180.66`
3. 右键数据库 → Query Tool
4. 打开文件 `F:\9\hercux-admin\backend\import_templates.sql`
5. 点击执行按钮 ▶️

### 方案4: 使用Python脚本 (需要网络访问)

如果配置了SSH隧道或VPN:

```bash
cd F:/9/hercux-admin/backend
python import_via_python.py
```

## 验证查询

导入成功后,运行以下查询验证:

```sql
-- 检查总数
SELECT COUNT(*) as total FROM simulator_templates WHERE quality_score = 75;
-- 预期: 24

-- 按学科统计
SELECT subject, COUNT(*) as count, AVG(quality_score) as avg_score
FROM simulator_templates
WHERE quality_score = 75
GROUP BY subject
ORDER BY subject;
-- 预期: 8个学科,每个3条记录

-- 查看所有模板名称
SELECT id, name, subject, difficulty, quality_score
FROM simulator_templates
ORDER BY subject, id;
```

## 预期结果

成功导入后应该看到:

| Subject | Count | Avg Score |
|---------|-------|-----------|
| biology | 3 | 75.0 |
| chemistry | 3 | 75.0 |
| computer_science | 3 | 75.0 |
| geography | 3 | 75.0 |
| history | 3 | 75.0 |
| mathematics | 3 | 75.0 |
| medicine | 3 | 75.0 |
| physics | 3 | 75.0 |

**总计**: 24个模板

## 导入失败排查

如果导入失败,检查:

1. **数据库连接**
   ```bash
   PGPASSWORD='Hercu2026Secure' psql -U hercu -d hercu_db -h 106.14.180.66 -c "SELECT version();"
   ```

2. **表是否存在**
   ```sql
   SELECT table_name FROM information_schema.tables
   WHERE table_name = 'simulator_templates';
   ```

3. **检查表结构**
   ```sql
   \d simulator_templates
   ```

4. **清空现有数据** (如果需要重新导入)
   ```sql
   DELETE FROM simulator_templates WHERE quality_score = 75;
   ```

## 下一步

导入成功后:
1. ✅ 模板库已建立
2. ⏳ 修改课程生成器 (generator.py)
3. ⏳ 实现模板选择功能
4. ⏳ 更新相关文档

---

**文件生成**: 2026-02-11
**导入文件**: F:\9\hercux-admin\backend\import_templates.sql (19,903行)
