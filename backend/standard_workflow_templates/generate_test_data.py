#!/usr/bin/env python3
"""
智能测试数据生成脚本

功能:
1. 读取系统中的科室信息
2. 读取系统中的收费项目信息
3. 读取维度-收费项目映射关系
4. 生成符合实际业务逻辑的测试数据
5. 插入到外部数据源数据库的源表（TB_MZ_SFMXB、TB_ZY_SFMXB）

数据表:
- TB_MZ_SFMXB: 门诊收费明细表
- TB_ZY_SFMXB: 住院收费明细表
- charge_details: 统一收费明细表（由步骤1从源表生成）
- workload_statistics: 工作量统计表

使用方法:
    python generate_test_data.py --hospital-id 1 --period 2025-10 --record-count 100
    
    # 指定数据源
    python generate_test_data.py --hospital-id 1 --period 2025-11 --record-count 500 --data-source-id 2
    
    # 预览模式（不实际插入）
    python generate_test_data.py --hospital-id 1 --period 2025-11 --record-count 100 --dry-run
"""

import argparse
import random
import sys
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Dict, Any
import os

# 添加父目录到路径以便导入app模块
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.department import Department
from app.models.charge_item import ChargeItem
from app.models.dimension_item_mapping import DimensionItemMapping
from app.models.data_source import DataSource
from app.services.data_source_service import connection_manager


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='生成测试数据')
    parser.add_argument('--hospital-id', type=int, required=True, help='医疗机构ID')
    parser.add_argument('--period', type=str, required=True, help='统计周期(YYYY-MM)')
    parser.add_argument('--record-count', type=int, default=100, help='生成的收费记录数量(默认100)')
    parser.add_argument('--data-source-id', type=int, help='外部数据源ID(不指定则使用默认数据源)')
    parser.add_argument('--patient-count', type=int, default=50, help='患者数量(默认50)')
    parser.add_argument('--dry-run', action='store_true', help='只显示将要生成的数据，不实际插入')
    return parser.parse_args()


def get_departments(db: Session, hospital_id: int) -> List[Department]:
    """获取医疗机构的所有活跃科室"""
    departments = db.query(Department).filter(
        Department.hospital_id == hospital_id,
        Department.is_active == True
    ).all()
    
    if not departments:
        print(f"❌ 错误: 医疗机构 {hospital_id} 没有活跃的科室")
        sys.exit(1)
    
    print(f"✅ 找到 {len(departments)} 个活跃科室")
    for dept in departments[:5]:  # 只显示前5个
        print(f"   - {dept.his_code}: {dept.his_name}")
    if len(departments) > 5:
        print(f"   ... 还有 {len(departments) - 5} 个科室")
    
    return departments


def get_charge_items(db: Session, hospital_id: int) -> List[ChargeItem]:
    """获取医疗机构的收费项目"""
    items = db.query(ChargeItem).filter(
        ChargeItem.hospital_id == hospital_id
    ).all()
    
    if not items:
        print(f"❌ 错误: 医疗机构 {hospital_id} 没有收费项目")
        sys.exit(1)
    
    print(f"✅ 找到 {len(items)} 个收费项目")
    for item in items[:5]:  # 只显示前5个
        price_str = item.unit_price if item.unit_price else "未定价"
        print(f"   - {item.item_code}: {item.item_name} ({price_str}元)")
    if len(items) > 5:
        print(f"   ... 还有 {len(items) - 5} 个收费项目")
    
    return items


def get_dimension_mappings(db: Session, hospital_id: int) -> List[DimensionItemMapping]:
    """获取维度-收费项目映射关系"""
    mappings = db.query(DimensionItemMapping).filter(
        DimensionItemMapping.hospital_id == hospital_id
    ).all()
    
    if not mappings:
        print(f"⚠️  警告: 医疗机构 {hospital_id} 没有维度-收费项目映射")
        print(f"   将生成随机的收费数据，但可能无法正确计算维度工作量")
    else:
        print(f"✅ 找到 {len(mappings)} 条维度-收费项目映射")
        # 统计每个维度的映射数量
        dimension_counts = {}
        for mapping in mappings:
            dimension_counts[mapping.dimension_code] = dimension_counts.get(mapping.dimension_code, 0) + 1
        
        for dim_code, count in list(dimension_counts.items())[:5]:
            print(f"   - {dim_code}: {count} 个收费项目")
    
    return mappings


def get_external_data_source(db: Session, data_source_id: int = None) -> DataSource:
    """获取外部数据源"""
    if data_source_id:
        data_source = db.query(DataSource).filter(DataSource.id == data_source_id).first()
        if not data_source:
            print(f"❌ 错误: 数据源 {data_source_id} 不存在")
            sys.exit(1)
    else:
        # 使用默认数据源
        data_source = db.query(DataSource).filter(DataSource.is_default == True).first()
        if not data_source:
            print(f"❌ 错误: 没有找到默认数据源")
            print(f"   请在前端配置数据源，或使用 --data-source-id 参数指定")
            sys.exit(1)
    
    print(f"✅ 使用数据源: {data_source.name} ({data_source.db_type})")
    return data_source


def generate_charge_records(
    departments: List[Department],
    charge_items: List[ChargeItem],
    mappings: List[DimensionItemMapping],
    period: str,
    record_count: int,
    patient_count: int
) -> List[Dict[str, Any]]:
    """生成收费明细记录"""
    
    # 解析周期
    year, month = period.split('-')
    start_date = datetime(int(year), int(month), 1)
    
    # 计算月份的最后一天
    if int(month) == 12:
        end_date = datetime(int(year) + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = datetime(int(year), int(month) + 1, 1) - timedelta(days=1)
    
    # 优先使用维度映射中的收费项目
    mapped_item_codes = set(m.item_code for m in mappings)
    mapped_items = [item for item in charge_items if item.item_code in mapped_item_codes]
    
    print(f"\n   📊 数据匹配分析:")
    print(f"   - 维度映射中的收费项目编码数: {len(mapped_item_codes)}")
    print(f"   - 系统收费项目总数: {len(charge_items)}")
    print(f"   - 匹配成功的收费项目数: {len(mapped_items)}")
    
    if mapped_items:
        print(f"   ✅ 将优先使用匹配的 {len(mapped_items)} 个收费项目")
        print(f"   示例匹配项目:")
        for item in mapped_items[:3]:
            print(f"      - {item.item_code}: {item.item_name}")
        # 80% 使用映射的项目，20% 使用随机项目
        use_mapped_ratio = 0.8
    else:
        print(f"   ⚠️  警告: 维度映射中的收费项目在系统中不存在")
        print(f"   维度映射示例编码:")
        for code in list(mapped_item_codes)[:5]:
            print(f"      - {code}")
        print(f"   系统收费项目示例编码:")
        for item in charge_items[:5]:
            print(f"      - {item.item_code}: {item.item_name}")
        print(f"   ❌ 将使用随机收费项目（可能无法被 Step1 统计）")
        mapped_items = charge_items
        use_mapped_ratio = 0
    
    records = []
    
    print(f"\n📝 生成 {record_count} 条收费记录...")
    
    for i in range(record_count):
        # 随机选择科室
        dept = random.choice(departments)
        
        # 优先选择映射的收费项目
        if mapped_items and random.random() < use_mapped_ratio:
            item = random.choice(mapped_items)
        else:
            item = random.choice(charge_items)
        
        # 随机选择患者
        patient_id = f"P{random.randint(1, patient_count):04d}"
        
        # 随机生成收费时间（在月份范围内）
        days_in_month = (end_date - start_date).days + 1
        random_day = random.randint(0, days_in_month - 1)
        random_hour = random.randint(8, 18)  # 工作时间
        random_minute = random.randint(0, 59)
        charge_time = start_date + timedelta(days=random_day, hours=random_hour, minutes=random_minute)
        
        # 随机数量（大部分是1，少数是多个）
        quantity = 1 if random.random() < 0.8 else random.randint(2, 5)
        
        # 计算金额（如果有单价则使用，否则生成随机金额）
        try:
            unit_price = float(item.unit_price) if item.unit_price else random.uniform(10, 500)
        except (ValueError, TypeError):
            unit_price = random.uniform(10, 500)
        
        amount = unit_price * quantity
        
        # 随机生成业务类别（70%门诊，30%住院）
        business_type = '门诊' if random.random() < 0.7 else '住院'
        
        record = {
            'patient_id': patient_id,
            'prescribing_dept_code': dept.his_code,
            'item_code': item.item_code,
            'item_name': item.item_name,
            'amount': amount,
            'quantity': quantity,
            'charge_time': charge_time,
            'business_type': business_type
        }
        
        records.append(record)
    
    # 统计信息
    dept_stats = {}
    for record in records:
        dept_code = record['prescribing_dept_code']
        if dept_code not in dept_stats:
            dept_stats[dept_code] = {'count': 0, 'amount': 0}
        dept_stats[dept_code]['count'] += 1
        dept_stats[dept_code]['amount'] += record['amount']
    
    print(f"✅ 生成完成，涉及 {len(dept_stats)} 个科室")
    for dept_code, stats in list(dept_stats.items())[:5]:
        print(f"   - {dept_code}: {stats['count']} 条记录, 总金额 {stats['amount']:.2f} 元")
    
    return records


def generate_workload_statistics(
    departments: List[Department],
    period: str
) -> List[Dict[str, Any]]:
    """生成工作量统计数据"""
    
    records = []
    
    print(f"\n📊 生成工作量统计数据...")
    
    # 护理床日数统计
    nursing_levels = ['一级护理', '二级护理', '三级护理', '特级护理']
    for dept in departments:
        for level in nursing_levels:
            # 随机生成床日数（根据护理级别调整范围）
            if level == '特级护理':
                value = random.randint(0, 30)  # 特级护理较少
            elif level == '一级护理':
                value = random.randint(20, 100)
            elif level == '二级护理':
                value = random.randint(50, 200)
            else:  # 三级护理
                value = random.randint(30, 150)
            
            if value > 0:  # 只记录有值的
                records.append({
                    'department_code': dept.his_code,
                    'stat_month': period,
                    'stat_type': 'nursing_days',
                    'stat_level': level,
                    'stat_value': value
                })
    
    # 会诊工作量统计
    for dept in departments:
        # 发起会诊
        initiated = random.randint(5, 50)
        records.append({
            'department_code': dept.his_code,
            'stat_month': period,
            'stat_type': 'consultation',
            'stat_level': '发起',
            'stat_value': initiated
        })
        
        # 参与会诊
        participated = random.randint(10, 60)
        records.append({
            'department_code': dept.his_code,
            'stat_month': period,
            'stat_type': 'consultation',
            'stat_level': '参与',
            'stat_value': participated
        })
    
    # 护理床日统计（使用维度code作为stat_type）
    bed_types = ['dim-nur-bed-3', 'dim-nur-bed-4', 'dim-nur-bed-5']
    for dept in departments:
        for bed_type in bed_types:
            value = random.randint(20, 150)
            records.append({
                'department_code': dept.his_code,
                'stat_month': period,
                'stat_type': bed_type,
                'stat_level': None,
                'stat_value': value
            })
    
    # 出入转院统计（使用维度code作为stat_type）
    trans_types = ['dim-nur-trans-in', 'dim-nur-trans-out', 'dim-nur-trans-intraday']
    for dept in departments:
        for trans_type in trans_types:
            value = random.randint(10, 100)
            records.append({
                'department_code': dept.his_code,
                'stat_month': period,
                'stat_type': trans_type,
                'stat_level': None,
                'stat_value': value
            })
    
    # 手术管理统计（使用维度code作为stat_type）
    op_types = ['dim-nur-op-3', 'dim-nur-op-4', 'dim-nur-op-acad', 'dim-nur-op-other']
    for dept in departments:
        for op_type in op_types:
            value = random.randint(5, 50)
            records.append({
                'department_code': dept.his_code,
                'stat_month': period,
                'stat_type': op_type,
                'stat_level': None,
                'stat_value': value
            })
    
    # 手术室护理统计（使用维度code作为stat_type）
    or_types = ['dim-nur-or-large', 'dim-nur-or-mid', 'dim-nur-or-tiny']
    for dept in departments:
        for or_type in or_types:
            value = random.randint(10, 80)
            records.append({
                'department_code': dept.his_code,
                'stat_month': period,
                'stat_type': or_type,
                'stat_level': None,
                'stat_value': value
            })
    
    print(f"✅ 生成 {len(records)} 条工作量统计记录")
    
    return records


def create_tables_if_not_exists(connection):
    """创建表（如果不存在）"""
    
    print(f"\n🔧 检查并创建表...")
    
    # 创建 TB_MZ_SFMXB 表（门诊收费明细表）
    connection.execute(text("""
        CREATE TABLE IF NOT EXISTS "TB_MZ_SFMXB" (
            "YLJGDM" varchar(33),
            "SFMXID" varchar(54),
            "BRZSY" varchar(96),
            "JZLSH" varchar(54),
            "BTFMXID" varchar(54),
            "TFBZ" varchar(2),
            "SFCJBM" varchar(2),
            "YZMXID" varchar(54),
            "SFXMLBBM" varchar(6),
            "FYSRGLBM" varchar(6),
            "FYFSSJ" timestamp,
            "SYJSID" varchar(54),
            "SFJSSJ" timestamp,
            "KDKSBM" varchar(54),
            "KDKSMC" varchar(108),
            "KDYSBH" varchar(54),
            "KDYSXM" varchar(108),
            "KDYSSFZHM" varchar(27),
            "ZXKSBM" varchar(54),
            "ZXKSMC" varchar(108),
            "ZXRYBH" varchar(54),
            "ZXRYXM" varchar(108),
            "ZXRYSFZHM" varchar(27),
            "SFXMBZBM" varchar(3),
            "MXXMBM" varchar(54),
            "MXXMMC" varchar(96),
            "YNSFXMBM" varchar(75),
            "YNSFXMMC" varchar(300),
            "MXXMDW" varchar(18),
            "XMFLBM" varchar(48),
            "XMFLMC" varchar(96),
            "MXXMDJ" numeric(10,4),
            "MXXMSL" numeric(8,3),
            "MXXMYSJE" numeric(10,4),
            "MXXMSSJE" numeric(10,4),
            "TBRQ" timestamp,
            "XGBZ" varchar(2),
            "YLYL1" varchar(192),
            "YLYL2" varchar(192)
        )
    """))
    
    # 创建 TB_ZY_SFMXB 表（住院收费明细表）
    connection.execute(text("""
        CREATE TABLE IF NOT EXISTS "TB_ZY_SFMXB" (
            "YLJGDM" varchar(33),
            "SFMXID" varchar(54),
            "TFBZ" varchar(2),
            "JZLSH" varchar(75),
            "BRZSY" varchar(96),
            "YZMXID" varchar(54),
            "KDKSBM" varchar(54),
            "KDKSMC" varchar(108),
            "KDYSBH" varchar(54),
            "KDYSXM" varchar(108),
            "ZXKSBM" varchar(54),
            "ZXKSMC" varchar(108),
            "ZXRYBH" varchar(54),
            "ZXRYXM" varchar(108),
            "SFXMLBBM" varchar(6),
            "FYSRGLBM" varchar(6),
            "FYFSSJ" timestamp,
            "SFXMBZBM" varchar(3),
            "MXXMBM" varchar(54),
            "MXXMMC" varchar(96),
            "XMFLBM" varchar(48),
            "XMFLMC" varchar(96),
            "MXXMDW" varchar(18),
            "MXXMDJ" numeric(10,4),
            "MXXMSL" numeric(9),
            "MXXMYSJE" numeric(10,4),
            "MXXMSSJE" numeric(10,4),
            "TBRQ" timestamp,
            "XGBZ" varchar(2),
            "YLYL1" varchar(192),
            "YLYL2" varchar(192)
        )
    """))
    
    # 创建 charge_details 表（用于步骤1生成）
    connection.execute(text("""
        CREATE TABLE IF NOT EXISTS charge_details (
            id SERIAL PRIMARY KEY,
            patient_id VARCHAR(50) NOT NULL,
            prescribing_dept_code VARCHAR(50) NOT NULL,
            item_code VARCHAR(100) NOT NULL,
            item_name VARCHAR(200),
            amount DECIMAL(20, 4) NOT NULL DEFAULT 0,
            quantity DECIMAL(20, 4) NOT NULL DEFAULT 0,
            charge_time TIMESTAMP NOT NULL,
            business_type VARCHAR(20),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """))
    
    connection.execute(text("""
        CREATE INDEX IF NOT EXISTS idx_charge_details_dept 
        ON charge_details(prescribing_dept_code)
    """))
    
    connection.execute(text("""
        CREATE INDEX IF NOT EXISTS idx_charge_details_item 
        ON charge_details(item_code)
    """))
    
    connection.execute(text("""
        CREATE INDEX IF NOT EXISTS idx_charge_details_time 
        ON charge_details(charge_time)
    """))
    
    # 创建 workload_statistics 表
    connection.execute(text("""
        CREATE TABLE IF NOT EXISTS workload_statistics (
            id SERIAL PRIMARY KEY,
            department_code VARCHAR(50) NOT NULL,
            stat_month VARCHAR(7) NOT NULL,
            stat_type VARCHAR(50) NOT NULL,
            stat_level VARCHAR(50),
            stat_value DECIMAL(20, 4) NOT NULL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """))
    
    connection.execute(text("""
        CREATE INDEX IF NOT EXISTS idx_workload_dept 
        ON workload_statistics(department_code)
    """))
    
    connection.execute(text("""
        CREATE INDEX IF NOT EXISTS idx_workload_month 
        ON workload_statistics(stat_month)
    """))
    
    connection.execute(text("""
        CREATE INDEX IF NOT EXISTS idx_workload_type 
        ON workload_statistics(stat_type)
    """))
    
    connection.commit()
    print(f"✅ 表检查完成")


def insert_charge_records(connection, records: List[Dict[str, Any]], period: str, departments: List[Department]):
    """插入收费记录到TB_MZ_SFMXB和TB_ZY_SFMXB"""
    
    print(f"\n💾 插入收费记录到源表...")
    
    # 先删除该周期的旧数据
    year, month = period.split('-')
    start_date = f"{period}-01"
    if int(month) == 12:
        end_date = f"{int(year)+1}-01-01"
    else:
        end_date = f"{year}-{int(month)+1:02d}-01"
    
    # 删除门诊表旧数据
    result = connection.execute(text("""
        DELETE FROM "TB_MZ_SFMXB" 
        WHERE "FYFSSJ" >= :start_date 
        AND "FYFSSJ" < :end_date
    """), {'start_date': start_date, 'end_date': end_date})
    mz_deleted = result.rowcount
    
    # 删除住院表旧数据
    result = connection.execute(text("""
        DELETE FROM "TB_ZY_SFMXB" 
        WHERE "FYFSSJ" >= :start_date 
        AND "FYFSSJ" < :end_date
    """), {'start_date': start_date, 'end_date': end_date})
    zy_deleted = result.rowcount
    
    if mz_deleted > 0 or zy_deleted > 0:
        print(f"   删除了旧数据: 门诊 {mz_deleted} 条, 住院 {zy_deleted} 条")
    
    # 创建科室编码到名称的映射
    dept_map = {dept.his_code: dept.his_name for dept in departments}
    
    # 分别插入门诊和住院数据
    mz_count = 0
    zy_count = 0
    
    for i, record in enumerate(records):
        # 生成唯一的收费明细ID
        sfmxid = f"SFMX{period.replace('-', '')}{i+1:06d}"
        jzlsh = f"JZ{period.replace('-', '')}{record['patient_id']}"
        dept_name = dept_map.get(record['prescribing_dept_code'], record['prescribing_dept_code'])
        
        if record['business_type'] == '门诊':
            # 插入到门诊表
            connection.execute(text("""
                INSERT INTO "TB_MZ_SFMXB" 
                ("YLJGDM", "SFMXID", "BRZSY", "JZLSH", "TFBZ", "FYFSSJ",
                 "KDKSBM", "KDKSMC", "MXXMBM", "MXXMMC", 
                 "MXXMDJ", "MXXMSL", "MXXMYSJE", "MXXMSSJE", "TBRQ")
                VALUES 
                (:yljgdm, :sfmxid, :brzsy, :jzlsh, :tfbz, :fyfssj,
                 :kdksbm, :kdksmc, :mxxmbm, :mxxmmc,
                 :mxxmdj, :mxxmsl, :mxxmysje, :mxxmssje, :tbrq)
            """), {
                'yljgdm': 'HOSPITAL001',
                'sfmxid': sfmxid,
                'brzsy': record['patient_id'],
                'jzlsh': jzlsh,
                'tfbz': '0',  # 非退费
                'fyfssj': record['charge_time'],
                'kdksbm': record['prescribing_dept_code'],
                'kdksmc': dept_name,
                'mxxmbm': record['item_code'],
                'mxxmmc': record['item_name'],
                'mxxmdj': record['amount'] / record['quantity'],
                'mxxmsl': record['quantity'],
                'mxxmysje': record['amount'],
                'mxxmssje': record['amount'],
                'tbrq': datetime.now()
            })
            mz_count += 1
        else:
            # 插入到住院表
            connection.execute(text("""
                INSERT INTO "TB_ZY_SFMXB" 
                ("YLJGDM", "SFMXID", "BRZSY", "JZLSH", "TFBZ", "FYFSSJ",
                 "KDKSBM", "KDKSMC", "MXXMBM", "MXXMMC",
                 "MXXMDJ", "MXXMSL", "MXXMYSJE", "MXXMSSJE", "TBRQ")
                VALUES 
                (:yljgdm, :sfmxid, :brzsy, :jzlsh, :tfbz, :fyfssj,
                 :kdksbm, :kdksmc, :mxxmbm, :mxxmmc,
                 :mxxmdj, :mxxmsl, :mxxmysje, :mxxmssje, :tbrq)
            """), {
                'yljgdm': 'HOSPITAL001',
                'sfmxid': sfmxid,
                'brzsy': record['patient_id'],
                'jzlsh': jzlsh,
                'tfbz': '0',  # 非退费
                'fyfssj': record['charge_time'],
                'kdksbm': record['prescribing_dept_code'],
                'kdksmc': dept_name,
                'mxxmbm': record['item_code'],
                'mxxmmc': record['item_name'],
                'mxxmdj': record['amount'] / record['quantity'],
                'mxxmsl': record['quantity'],
                'mxxmysje': record['amount'],
                'mxxmssje': record['amount'],
                'tbrq': datetime.now()
            })
            zy_count += 1
    
    connection.commit()
    print(f"✅ 插入完成: 门诊 {mz_count} 条, 住院 {zy_count} 条")


def insert_workload_statistics(connection, records: List[Dict[str, Any]], period: str):
    """插入工作量统计"""
    
    print(f"\n💾 插入工作量统计...")
    
    # 先删除该周期的旧数据
    result = connection.execute(text("""
        DELETE FROM workload_statistics 
        WHERE stat_month = :period
    """), {'period': period})
    
    deleted_count = result.rowcount
    if deleted_count > 0:
        print(f"   删除了 {deleted_count} 条旧数据")
    
    # 批量插入新数据
    for record in records:
        connection.execute(text("""
            INSERT INTO workload_statistics 
            (department_code, stat_month, stat_type, stat_level, stat_value)
            VALUES 
            (:department_code, :stat_month, :stat_type, :stat_level, :stat_value)
        """), record)
    
    connection.commit()
    print(f"✅ 插入了 {len(records)} 条工作量统计")


def verify_data(connection, period: str):
    """验证插入的数据"""
    
    print(f"\n🔍 验证数据...")
    
    # 计算正确的结束日期
    from calendar import monthrange
    year, month = period.split('-')
    last_day = monthrange(int(year), int(month))[1]
    start_date = f"{period}-01"
    end_date = f"{period}-{last_day}"
    
    # 验证门诊收费记录
    result = connection.execute(text("""
        SELECT 
            "KDKSBM" as dept_code,
            COUNT(*) as record_count,
            COUNT(DISTINCT "BRZSY") as patient_count,
            SUM("MXXMSSJE") as total_amount
        FROM "TB_MZ_SFMXB"
        WHERE "FYFSSJ" >= :start_date 
        AND "FYFSSJ" <= :end_date
        GROUP BY "KDKSBM"
        ORDER BY "KDKSBM"
    """), {
        'start_date': start_date,
        'end_date': end_date + ' 23:59:59'
    })
    
    print(f"\n门诊收费明细汇总:")
    mz_total_records = 0
    mz_total_amount = 0
    for row in result:
        mz_total_records += row.record_count
        mz_total_amount += float(row.total_amount or 0)
        print(f"  {row.dept_code}: {row.record_count} 条记录, "
              f"{row.patient_count} 个患者, 总金额 {float(row.total_amount or 0):.2f} 元")
    print(f"  合计: {mz_total_records} 条记录, 总金额 {mz_total_amount:.2f} 元")
    
    # 验证住院收费记录
    result = connection.execute(text("""
        SELECT 
            "KDKSBM" as dept_code,
            COUNT(*) as record_count,
            COUNT(DISTINCT "BRZSY") as patient_count,
            SUM("MXXMSSJE") as total_amount
        FROM "TB_ZY_SFMXB"
        WHERE "FYFSSJ" >= :start_date 
        AND "FYFSSJ" <= :end_date
        GROUP BY "KDKSBM"
        ORDER BY "KDKSBM"
    """), {
        'start_date': start_date,
        'end_date': end_date + ' 23:59:59'
    })
    
    print(f"\n住院收费明细汇总:")
    zy_total_records = 0
    zy_total_amount = 0
    for row in result:
        zy_total_records += row.record_count
        zy_total_amount += float(row.total_amount or 0)
        print(f"  {row.dept_code}: {row.record_count} 条记录, "
              f"{row.patient_count} 个患者, 总金额 {float(row.total_amount or 0):.2f} 元")
    print(f"  合计: {zy_total_records} 条记录, 总金额 {zy_total_amount:.2f} 元")
    
    print(f"\n总计: {mz_total_records + zy_total_records} 条记录, "
          f"总金额 {mz_total_amount + zy_total_amount:.2f} 元")
    
    # 验证工作量统计
    result = connection.execute(text("""
        SELECT 
            department_code,
            stat_type,
            COUNT(*) as record_count,
            SUM(stat_value) as total_value
        FROM workload_statistics
        WHERE stat_month = :period
        GROUP BY department_code, stat_type
        ORDER BY department_code, stat_type
    """), {'period': period})
    
    print(f"\n工作量统计汇总:")
    for row in result:
        print(f"  {row.department_code} - {row.stat_type}: "
              f"{row.record_count} 条记录, 总值 {float(row.total_value):.2f}")


def main():
    """主函数"""
    args = parse_args()
    
    print(f"=" * 80)
    print(f"智能测试数据生成脚本")
    print(f"=" * 80)
    print(f"医疗机构ID: {args.hospital_id}")
    print(f"统计周期: {args.period}")
    print(f"收费记录数: {args.record_count}")
    print(f"患者数量: {args.patient_count}")
    print(f"模式: {'预览模式 (不实际插入)' if args.dry_run else '执行模式'}")
    print(f"=" * 80)
    
    # 连接系统数据库
    print(f"\n🔌 连接系统数据库...")
    db = SessionLocal()
    
    try:
        # 1. 获取科室信息
        print(f"\n📋 步骤 1/6: 读取科室信息")
        departments = get_departments(db, args.hospital_id)
        
        # 2. 获取收费项目
        print(f"\n📋 步骤 2/6: 读取收费项目")
        charge_items = get_charge_items(db, args.hospital_id)
        
        # 3. 获取维度映射
        print(f"\n📋 步骤 3/6: 读取维度-收费项目映射")
        mappings = get_dimension_mappings(db, args.hospital_id)
        
        # 4. 获取外部数据源
        print(f"\n📋 步骤 4/6: 连接外部数据源")
        data_source = get_external_data_source(db, args.data_source_id)
        
        # 5. 生成测试数据
        print(f"\n📋 步骤 5/6: 生成测试数据")
        charge_records = generate_charge_records(
            departments, charge_items, mappings, args.period, 
            args.record_count, args.patient_count
        )
        workload_records = generate_workload_statistics(departments, args.period)
        
        if args.dry_run:
            print(f"\n⚠️  预览模式: 不实际插入数据")
            print(f"\n将生成:")
            print(f"  - {len(charge_records)} 条收费记录")
            print(f"  - {len(workload_records)} 条工作量统计")
            return
        
        # 6. 插入数据到外部数据源
        print(f"\n📋 步骤 6/6: 插入数据到外部数据源")
        
        # 获取或创建连接池
        pool = connection_manager.get_pool(data_source.id)
        if not pool:
            pool = connection_manager.create_pool(data_source)
        
        with pool.connect() as connection:
            # 创建表
            create_tables_if_not_exists(connection)
            
            # 插入数据
            insert_charge_records(connection, charge_records, args.period, departments)
            insert_workload_statistics(connection, workload_records, args.period)
            
            # 验证数据
            verify_data(connection, args.period)
        
        print(f"\n" + "=" * 80)
        print(f"✅ 测试数据生成完成!")
        print(f"=" * 80)
        print(f"\n数据已插入到源表:")
        print(f"  - TB_MZ_SFMXB (门诊收费明细表)")
        print(f"  - TB_ZY_SFMXB (住院收费明细表)")
        print(f"  - workload_statistics (工作量统计表)")
        print(f"\n下一步:")
        print(f"  1. 在前端创建计算任务")
        print(f"  2. 选择医疗机构 {args.hospital_id}")
        print(f"  3. 选择周期 {args.period}")
        print(f"  4. 运行标准计算流程（包含步骤1：数据准备）")
        print(f"     - 步骤1会从TB_MZ_SFMXB和TB_ZY_SFMXB生成charge_details")
        print(f"     - 步骤2-4会基于charge_details进行计算")
        
    except Exception as e:
        print(f"\n❌ 错误: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()


if __name__ == '__main__':
    main()
