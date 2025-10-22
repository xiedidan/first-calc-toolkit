# 数据库性能优化脚本

Write-Host "================================" -ForegroundColor Cyan
Write-Host "数据库性能优化" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# 1. 运行数据库迁移（添加索引）
Write-Host "步骤 1: 应用数据库迁移（添加索引）..." -ForegroundColor Yellow
try {
    Set-Location backend
    C:\software\anaconda3\Scripts\conda.exe run -n hospital-backend alembic upgrade head
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ 数据库迁移成功" -ForegroundColor Green
    } else {
        Write-Host "✗ 数据库迁移失败" -ForegroundColor Red
        Set-Location ..
        exit 1
    }
    Set-Location ..
} catch {
    Write-Host "✗ 数据库迁移失败: $_" -ForegroundColor Red
    Set-Location ..
    exit 1
}

Write-Host ""

# 2. 分析表统计信息
Write-Host "步骤 2: 更新表统计信息..." -ForegroundColor Yellow
$analyzeScript = @"
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv('backend/.env')

# 连接数据库
conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

# 分析表
tables = ['charge_items', 'dimension_items', 'dimension_item_mappings', 'departments']
for table in tables:
    print(f'分析表: {table}')
    cur.execute(f'ANALYZE {table}')
    conn.commit()

# 获取表大小
cur.execute('''
    SELECT 
        schemaname,
        tablename,
        pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size,
        n_live_tup as row_count
    FROM pg_stat_user_tables
    WHERE schemaname = 'public'
    ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
''')

print('\n表大小统计:')
print('-' * 60)
for row in cur.fetchall():
    print(f'{row[1]:30} {row[2]:15} {row[3]:10} 行')

# 获取索引信息
cur.execute('''
    SELECT 
        tablename,
        indexname,
        indexdef
    FROM pg_indexes
    WHERE schemaname = 'public' AND tablename = 'charge_items'
    ORDER BY tablename, indexname;
''')

print('\ncharge_items 表索引:')
print('-' * 60)
for row in cur.fetchall():
    print(f'{row[1]}')

cur.close()
conn.close()
print('\n✓ 统计信息更新完成')
"@

try {
    $analyzeScript | C:\software\anaconda3\Scripts\conda.exe run -n hospital-backend python
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ 统计信息更新成功" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠ 统计信息更新失败（可选步骤）: $_" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "优化完成！" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "建议:" -ForegroundColor Yellow
Write-Host "1. 重启 FastAPI 服务以应用代码优化" -ForegroundColor White
Write-Host "2. 测试收费项目列表查询性能" -ForegroundColor White
Write-Host "3. 观察后端日志中的响应时间" -ForegroundColor White
Write-Host ""
