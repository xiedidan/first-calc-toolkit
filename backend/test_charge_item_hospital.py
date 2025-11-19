"""
测试收费项目的医疗机构隔离功能
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.database import SessionLocal
from app.models.charge_item import ChargeItem
from app.models.hospital import Hospital
from app.models.user import User


def test_charge_item_hospital_isolation():
    """测试收费项目的医疗机构隔离"""
    db = SessionLocal()
    
    try:
        print("=" * 60)
        print("测试收费项目的医疗机构隔离功能")
        print("=" * 60)
        
        # 1. 获取所有医疗机构
        hospitals = db.query(Hospital).all()
        print(f"\n1. 系统中的医疗机构数量: {len(hospitals)}")
        for h in hospitals:
            print(f"   - {h.name} (ID: {h.id}, 编码: {h.code})")
        
        if len(hospitals) < 2:
            print("\n⚠️  警告：系统中少于2个医疗机构，无法充分测试隔离功能")
            print("   建议先运行医疗机构迁移脚本创建测试数据")
            return
        
        # 2. 查看每个医疗机构的收费项目
        print("\n2. 各医疗机构的收费项目统计:")
        for hospital in hospitals:
            count = db.query(ChargeItem).filter(
                ChargeItem.hospital_id == hospital.id
            ).count()
            print(f"   - {hospital.name}: {count} 个收费项目")
            
            # 显示前3个收费项目
            items = db.query(ChargeItem).filter(
                ChargeItem.hospital_id == hospital.id
            ).limit(3).all()
            
            for item in items:
                print(f"     * {item.item_code} - {item.item_name}")
        
        # 3. 测试跨医疗机构查询
        print("\n3. 测试数据隔离:")
        hospital1 = hospitals[0]
        hospital2 = hospitals[1]
        
        # 查询医疗机构1的收费项目
        items1 = db.query(ChargeItem).filter(
            ChargeItem.hospital_id == hospital1.id
        ).all()
        
        # 查询医疗机构2的收费项目
        items2 = db.query(ChargeItem).filter(
            ChargeItem.hospital_id == hospital2.id
        ).all()
        
        print(f"   - {hospital1.name} 有 {len(items1)} 个收费项目")
        print(f"   - {hospital2.name} 有 {len(items2)} 个收费项目")
        
        # 检查是否有重复的item_code
        codes1 = {item.item_code for item in items1}
        codes2 = {item.item_code for item in items2}
        common_codes = codes1 & codes2
        
        if common_codes:
            print(f"   ✓ 发现 {len(common_codes)} 个相同的收费项目编码（不同医疗机构可以有相同编码）")
            print(f"     示例: {list(common_codes)[:3]}")
        else:
            print("   - 两个医疗机构没有相同的收费项目编码")
        
        # 4. 测试用户关联
        print("\n4. 测试用户与收费项目的关联:")
        users = db.query(User).limit(5).all()
        for user in users:
            if user.hospital_id:
                hospital = db.query(Hospital).filter(Hospital.id == user.hospital_id).first()
                item_count = db.query(ChargeItem).filter(
                    ChargeItem.hospital_id == user.hospital_id
                ).count()
                print(f"   - 用户 {user.username} 属于 {hospital.name if hospital else '未知'}")
                print(f"     可访问 {item_count} 个收费项目")
        
        print("\n" + "=" * 60)
        print("✓ 测试完成")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    test_charge_item_hospital_isolation()
