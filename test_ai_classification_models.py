"""
测试AI分类模型
"""
import sys
sys.path.insert(0, 'backend')

from app.database import SessionLocal
from app.models import (
    Hospital, User, ModelVersion, ChargeItem,
    AIConfig, ClassificationTask, ClassificationPlan, PlanItem, TaskProgress, APIUsageLog,
    TaskStatus, PlanStatus, ProcessingStatus, ProgressStatus
)
from datetime import datetime


def test_ai_classification_models():
    """测试AI分类模型的创建和关系"""
    db = SessionLocal()
    
    try:
        # 1. 获取测试医疗机构
        hospital = db.query(Hospital).first()
        if not hospital:
            print("❌ 没有找到医疗机构")
            return False
        print(f"✓ 找到医疗机构: {hospital.name}")
        
        # 2. 获取测试用户
        user = db.query(User).first()
        if not user:
            print("❌ 没有找到用户")
            return False
        print(f"✓ 找到用户: {user.username}")
        
        # 3. 获取测试模型版本
        version = db.query(ModelVersion).filter_by(hospital_id=hospital.id).first()
        if not version:
            print("❌ 没有找到模型版本")
            return False
        print(f"✓ 找到模型版本: {version.name}")
        
        # 4. 删除已存在的AI配置（如果有）
        existing_config = db.query(AIConfig).filter_by(hospital_id=hospital.id).first()
        if existing_config:
            db.delete(existing_config)
            db.commit()
            print("✓ 删除已存在的AI配置")
        
        # 5. 创建AI配置
        ai_config = AIConfig(
            hospital_id=hospital.id,
            api_endpoint="https://api.deepseek.com/v1",
            api_key_encrypted="test_encrypted_key_12345",
            prompt_template="请对以下医技项目进行分类：{item_name}\n可选维度：{dimensions}",
            call_delay=1.0,
            daily_limit=10000,
            batch_size=100
        )
        db.add(ai_config)
        db.commit()
        print(f"✓ 创建AI配置成功，ID: {ai_config.id}")
        
        # 6. 创建分类任务
        task = ClassificationTask(
            hospital_id=hospital.id,
            task_name="测试分类任务",
            model_version_id=version.id,
            charge_categories=["检查费", "化验费"],
            status="pending",  # 使用小写字符串
            total_items=10,
            processed_items=0,
            failed_items=0,
            created_by=user.id
        )
        db.add(task)
        db.commit()
        print(f"✓ 创建分类任务成功，ID: {task.id}")
        
        # 7. 创建分类预案
        plan = ClassificationPlan(
            hospital_id=hospital.id,
            task_id=task.id,
            plan_name="测试预案",
            status="draft"  # 使用小写字符串
        )
        db.add(plan)
        db.commit()
        print(f"✓ 创建分类预案成功，ID: {plan.id}")
        
        # 8. 获取收费项目
        charge_item = db.query(ChargeItem).filter_by(hospital_id=hospital.id).first()
        if not charge_item:
            print("⚠ 没有找到收费项目，跳过预案项目测试")
        else:
            # 9. 创建预案项目
            plan_item = PlanItem(
                hospital_id=hospital.id,
                plan_id=plan.id,
                charge_item_id=charge_item.id,
                charge_item_name=charge_item.item_name,
                ai_confidence=0.85,
                processing_status="completed"  # 使用小写字符串
            )
            db.add(plan_item)
            db.commit()
            print(f"✓ 创建预案项目成功，ID: {plan_item.id}")
            
            # 10. 创建任务进度记录
            progress = TaskProgress(
                task_id=task.id,
                charge_item_id=charge_item.id,
                status="completed",  # 使用小写字符串
                processed_at=datetime.utcnow()
            )
            db.add(progress)
            db.commit()
            print(f"✓ 创建任务进度记录成功，ID: {progress.id}")
            
            # 11. 创建API使用日志
            log = APIUsageLog(
                hospital_id=hospital.id,
                task_id=task.id,
                charge_item_id=charge_item.id,
                request_data={"item_name": charge_item.item_name},
                response_data={"dimension_id": 1, "confidence": 0.85},
                status_code=200,
                call_duration=0.5
            )
            db.add(log)
            db.commit()
            print(f"✓ 创建API使用日志成功，ID: {log.id}")
        
        # 12. 测试关系
        print("\n测试模型关系:")
        
        # 测试Hospital关系
        hospital_configs = db.query(AIConfig).filter_by(hospital_id=hospital.id).all()
        print(f"✓ 医疗机构的AI配置数量: {len(hospital_configs)}")
        
        hospital_tasks = db.query(ClassificationTask).filter_by(hospital_id=hospital.id).all()
        print(f"✓ 医疗机构的分类任务数量: {len(hospital_tasks)}")
        
        # 测试Task关系
        task_plan = db.query(ClassificationPlan).filter_by(task_id=task.id).first()
        print(f"✓ 任务的预案: {task_plan.plan_name if task_plan else 'None'}")
        
        task_progress_records = db.query(TaskProgress).filter_by(task_id=task.id).all()
        print(f"✓ 任务的进度记录数量: {len(task_progress_records)}")
        
        # 测试Plan关系
        plan_items = db.query(PlanItem).filter_by(plan_id=plan.id).all()
        print(f"✓ 预案的项目数量: {len(plan_items)}")
        
        # 13. 清理测试数据
        print("\n清理测试数据:")
        db.query(APIUsageLog).filter_by(task_id=task.id).delete()
        db.query(TaskProgress).filter_by(task_id=task.id).delete()
        db.query(PlanItem).filter_by(plan_id=plan.id).delete()
        db.query(ClassificationPlan).filter_by(id=plan.id).delete()
        db.query(ClassificationTask).filter_by(id=task.id).delete()
        db.query(AIConfig).filter_by(id=ai_config.id).delete()
        db.commit()
        print("✓ 测试数据清理完成")
        
        print("\n✅ 所有测试通过！")
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    success = test_ai_classification_models()
    sys.exit(0 if success else 1)
