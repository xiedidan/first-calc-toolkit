"""
清理测试导向规则数据
"""
import sys
sys.path.insert(0, 'backend')

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.orientation_rule import OrientationRule

def cleanup():
    """清理所有测试导向规则"""
    db: Session = SessionLocal()
    
    try:
        # 删除所有导向规则
        rules = db.query(OrientationRule).all()
        count = len(rules)
        
        for rule in rules:
            db.delete(rule)
        
        db.commit()
        print(f"✓ 清理完成，删除了 {count} 条导向规则")
        
    except Exception as e:
        print(f"✗ 清理失败: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    cleanup()
