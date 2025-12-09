"""
检查护理维度覆盖情况，生成未覆盖维度的CSV报告
"""
import sys
import os
import csv
from dotenv import load_dotenv

load_dotenv('backend/.env')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.model_node import ModelNode
from app.models.dimension_item_mapping import DimensionItemMapping

def check_nursing_coverage():
    """检查护理维度覆盖情况"""
    db = SessionLocal()
    
    try:
        version_id = 26
        
        # 获取所有护理序列的叶子维度
        nursing_dimensions = db.query(ModelNode).filter(
            ModelNode.version_id == version_id,
            ModelNode.code.like('dim-nur%'),
            ModelNode.is_leaf == True
        ).order_by(ModelNode.code).all()
        
        print(f"护理序列共有 {len(nursing_dimensions)} 个叶子维度:\n")
        
        # 步骤2中已覆盖的维度
        covered_dimensions = {
            # 从charge_details统计
            'dim-nur-base',
            'dim-nur-collab',
            'dim-nur-tr-a',
            'dim-nur-tr-b',
            'dim-nur-tr-c',
            'dim-nur-other',
            # 从workload_statistics统计
            'dim-nur-bed-3',
            'dim-nur-bed-4',
            'dim-nur-bed-5',
            'dim-nur-trans-in',
            'dim-nur-trans-intraday',
            'dim-nur-trans-out',
        }
        
        uncovered = []
        
        for dim in nursing_dimensions:
            # 检查是否有映射
            mapping_count = db.query(DimensionItemMapping).filter(
                DimensionItemMapping.dimension_code == dim.code
            ).count()
            
            # 检查是否在步骤中覆盖
            is_covered = dim.code in covered_dimensions
            
            status = "✓ 已覆盖" if is_covered else "✗ 未覆盖"
            data_source = "charge_details" if mapping_count > 0 else "workload_statistics"
            
            print(f"{status} | {dim.code:25} | {dim.name:15} | 权重: {dim.weight:8} | 映射数: {mapping_count:3} | 数据源: {data_source}")
            
            if not is_covered:
                uncovered.append({
                    'code': dim.code,
                    'name': dim.name,
                    'weight': float(dim.weight) if dim.weight else 0,
                    'mapping_count': mapping_count,
                    'suggested_data_source': data_source,
                    'parent_code': db.query(ModelNode.code).filter(ModelNode.id == dim.parent_id).scalar() if dim.parent_id else ''
                })
        
        # 生成CSV报告
        if uncovered:
            csv_file = 'nursing_uncovered_dimensions.csv'
            with open(csv_file, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=['code', 'name', 'weight', 'mapping_count', 'suggested_data_source', 'parent_code'])
                writer.writeheader()
                writer.writerows(uncovered)
            
            print(f"\n⚠ 发现 {len(uncovered)} 个未覆盖的维度")
            print(f"详细信息已保存到: {csv_file}")
        else:
            print(f"\n✓ 所有护理维度均已覆盖!")
        
        # 统计信息
        print(f"\n统计:")
        print(f"  总维度数: {len(nursing_dimensions)}")
        print(f"  已覆盖: {len(covered_dimensions)}")
        print(f"  未覆盖: {len(uncovered)}")
        
    except Exception as e:
        print(f"错误: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    check_nursing_coverage()
