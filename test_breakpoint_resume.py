"""
断点续传场景测试

测试流程:
1. 创建任务
2. 模拟中断（部分处理后停止）
3. 验证进度保存
4. 继续处理
5. 验证不重复处理
"""

import sys
import os
from unittest.mock import patch, MagicMock

# 添加backend目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.database import SessionLocal
from app.models import (
    Hospital, User, ModelVersion, ModelNode, ChargeItem,
    AIConfig, ClassificationTask, ClassificationPlan, PlanItem
)
from app.services.ai_config_service import AIConfigService
from app.services.classification_task_service import ClassificationTaskService


def setup_test_data(db):
    """设置测试数据"""
    print("设置测试数据...")
    
    # 创建医疗机构
    hospital = Hospital(
        name="测试医院断点",
        code="TEST_BP_001",
        is_active=True
    )
    db.add(hospital)
    db.flush()
    
    # 创建用户
    user = User(
        username="test_bp_user",
        email="test_bp@example.com",
        hashed_password="hashed_password",
        role="admin",
        hospital_id=hospital.id
    )
    db.add(user)
    db.flush()
    
    # 创建模型版本
    version = ModelVersion(
        hospital_id=hospital.id,
        version="v1.0",
        name="测试版本断点",
        is_active=True
    )
    db.add(version)
    db.flush()
    
    # 创建维度节点
    dimensions = []
    for i in range(3):
        node = ModelNode(
            version_id=version.id,
            name=f"维度{i+1}",
            code=f"DIM_{i+1}",
            node_type="dimension",
            is_leaf=True,
            sort_order=i + 1
        )
        db.add(node)
        db.flush()
        dimensions.append(node)
    
    # 创建20个收费项目用于测试断点续传
    charge_items = []
    for i in range(20):
        item = ChargeItem(
            hospital_id=hospital.id,
            item_code=f"ITEM_BP_{i+1:03d}",
            item_name=f"断点测试项目{i+1}",
            charge_category="检查费",
            unit_price=100.0 + i * 10
        )
        db.add(item)
        db.flush()
        charge_items.append(item)
    
    db.commit()
    
    return {
        "hospital": hospital,
        "user": user,
        "version": version,
        "dimensions": dimensions,
        "charge_items": charge_items
    }


def cleanup_test_data(db, test_data):
    """清理测试数据"""
    print("清理测试数据...")
    
    try:
        # 删除预案项目
        db.query(PlanItem).filter(
            PlanItem.hospital_id == test_data["hospital"].id
        ).delete()
        
        # 删除预案
        db.query(ClassificationPlan).filter(
            ClassificationPlan.hospital_id == test_data["hospital"].id
        ).delete()
        
        # 删除任务
        db.query(ClassificationTask).filter(
            ClassificationTask.hospital_id == test_data["hospital"].id
        ).delete()
        
        # 删除AI配置
        db.query(AIConfig).filter(
            AIConfig.hospital_id == test_data["hospital"].id
        ).delete()
        
        # 删除收费项目
        db.query(ChargeItem).filter(
            ChargeItem.hospital_id == test_data["hospital"].id
        ).delete()
        
        # 删除维度节点
        db.query(ModelNode).filter(
            ModelNode.version_id == test_data["version"].id
        ).delete()
        
        # 删除模型版本
        db.query(ModelVersion).filter(
            ModelVersion.hospital_id == test_data["hospital"].id
        ).delete()
        
        # 删除用户
        db.query(User).filter(
            User.id == test_data["user"].id
        ).delete()
        
        # 删除医疗机构
        db.query(Hospital).filter(
            Hospital.id == test_data["hospital"].id
        ).delete()
        
        db.commit()
        print("测试数据清理完成")
    except Exception as e:
        print(f"清理测试数据时出错: {e}")
        db.rollback()


@patch('app.tasks.classification_tasks.call_ai_classification')
@patch('app.tasks.classification_tasks.time.sleep')
def test_breakpoint_resume(mock_sleep, mock_ai_call):
    """
    断点续传场景测试
    
    验证需求: 3.7, 4.3-4.5
    """
    print("\n" + "="*80)
    print("开始断点续传场景测试")
    print("="*80)
    
    db = SessionLocal()
    test_data = None
    
    try:
        # 步骤1: 设置测试数据
        test_data = setup_test_data(db)
        hospital_id = test_data["hospital"].id
        user_id = test_data["user"].id
        version_id = test_data["version"].id
        dimensions = test_data["dimensions"]
        charge_items = test_data["charge_items"]
        
        print(f"\n✓ 测试数据设置完成")
        print(f"  - 收费项目数量: {len(charge_items)}")
        
        # 配置AI接口
        ai_service = AIConfigService(db)
        config_data = {
            "api_endpoint": "https://api.deepseek.com/v1",
            "api_key": "test-api-key-bp",
            "prompt_template": "分类项目：{item_name}\n维度：{dimensions}",
            "call_delay": 0.1,
            "daily_limit": 1000,
            "batch_size": 100
        }
        ai_service.create_or_update_config(hospital_id, config_data)
        
        # 步骤2: 创建任务
        print("\n步骤1: 创建分类任务...")
        task_service = ClassificationTaskService(db)
        
        task_data = {
            "task_name": "断点续传测试任务",
            "model_version_id": version_id,
            "charge_categories": ["检查费"]
        }
        
        task = task_service.create_task(hospital_id, user_id, task_data)
        print(f"✓ 任务创建成功，ID: {task.id}")
        print(f"  - 总项目数: {task.total_items}")
        
        # 步骤3: 模拟中断 - 只处理前10个项目
        print("\n步骤2: 模拟中断（处理前10个项目后停止）...")
        
        call_count = [0]  # 使用列表以便在闭包中修改
        
        def mock_ai_response_with_interrupt(*args, **kwargs):
            call_count[0] += 1
            
            # 处理前10个后抛出异常模拟中断
            if call_count[0] > 10:
                raise Exception("模拟Celery worker中断")
            
            # 返回正常结果
            import random
            dimension = random.choice(dimensions)
            return {
                "dimension_id": dimension.id,
                "confidence": round(random.uniform(0.6, 0.95), 4)
            }
        
        mock_ai_call.side_effect = mock_ai_response_with_interrupt
        
        # 执行任务（会在第11个项目时中断）
        from app.tasks.classification_tasks import classify_items_task
        
        try:
            classify_items_task(task.id, hospital_id)
        except Exception as e:
            print(f"✓ 任务按预期中断: {e}")
        
        # 步骤4: 验证进度保存
        print("\n步骤3: 验证进度保存...")
        
        db.refresh(task)
        print(f"✓ 任务状态: {task.status}")
        print(f"  - 已处理: {task.processed_items}/{task.total_items}")
        print(f"  - 失败: {task.failed_items}")
        
        # 验证已处理10个项目
        assert task.processed_items == 10, f"应已处理10个项目，实际处理了{task.processed_items}个"
        assert task.status in ["processing", "failed"], f"任务状态应为processing或failed，实际为{task.status}"
        
        # 查询预案项目，验证前10个已完成
        plan = db.query(ClassificationPlan).filter(
            ClassificationPlan.task_id == task.id
        ).first()
        
        assert plan is not None, "预案应已创建"
        
        completed_items = db.query(PlanItem).filter(
            PlanItem.plan_id == plan.id,
            PlanItem.processing_status == "completed"
        ).count()
        
        pending_items = db.query(PlanItem).filter(
            PlanItem.plan_id == plan.id,
            PlanItem.processing_status == "pending"
        ).count()
        
        print(f"✓ 预案项目状态:")
        print(f"  - 已完成: {completed_items}")
        print(f"  - 待处理: {pending_items}")
        
        assert completed_items == 10, f"应有10个已完成项目，实际有{completed_items}个"
        assert pending_items == 10, f"应有10个待处理项目，实际有{pending_items}个"
        
        # 步骤5: 继续处理
        print("\n步骤4: 继续处理任务...")
        
        # 重置mock，允许继续处理
        call_count[0] = 0
        processed_items_before_continue = []
        
        def mock_ai_response_continue(*args, **kwargs):
            call_count[0] += 1
            
            # 记录处理的项目
            if 'item_name' in str(args) or 'item_name' in str(kwargs):
                item_name = str(args) if args else str(kwargs)
                processed_items_before_continue.append(item_name)
            
            # 正常返回结果
            import random
            dimension = random.choice(dimensions)
            return {
                "dimension_id": dimension.id,
                "confidence": round(random.uniform(0.6, 0.95), 4)
            }
        
        mock_ai_call.side_effect = mock_ai_response_continue
        
        # 继续处理任务
        result = task_service.continue_task(task.id, hospital_id)
        print(f"✓ 继续处理任务")
        
        # 执行继续任务
        from app.tasks.classification_tasks import continue_classification_task
        continue_classification_task(task.id, hospital_id)
        
        # 步骤6: 验证不重复处理
        print("\n步骤5: 验证不重复处理...")
        
        db.refresh(task)
        print(f"✓ 任务最终状态: {task.status}")
        print(f"  - 已处理: {task.processed_items}/{task.total_items}")
        print(f"  - 失败: {task.failed_items}")
        
        # 验证所有项目已处理
        assert task.status == "completed", f"任务状态应为completed，实际为{task.status}"
        assert task.processed_items == task.total_items, \
            f"所有项目应已处理，实际处理{task.processed_items}/{task.total_items}"
        
        # 验证AI调用次数（应该只调用了剩余的10个项目）
        print(f"✓ 继续处理时的AI调用次数: {call_count[0]}")
        assert call_count[0] == 10, f"应只调用AI 10次（处理剩余项目），实际调用了{call_count[0]}次"
        
        # 验证所有预案项目都已完成
        all_completed = db.query(PlanItem).filter(
            PlanItem.plan_id == plan.id,
            PlanItem.processing_status == "completed"
        ).count()
        
        print(f"✓ 所有预案项目状态: {all_completed}/{task.total_items} 已完成")
        assert all_completed == task.total_items, \
            f"所有项目应已完成，实际完成{all_completed}/{task.total_items}"
        
        # 验证没有重复处理
        all_items = db.query(PlanItem).filter(
            PlanItem.plan_id == plan.id
        ).all()
        
        # 检查每个项目只有一个AI建议
        for item in all_items:
            assert item.ai_suggested_dimension_id is not None, \
                f"项目{item.charge_item_name}应有AI建议维度"
            assert item.ai_confidence is not None, \
                f"项目{item.charge_item_name}应有确信度"
        
        print("✓ 验证通过：没有重复处理")
        
        print("\n" + "="*80)
        print("✓ 断点续传场景测试通过！")
        print("="*80)
        
        return True
        
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        if test_data:
            cleanup_test_data(db, test_data)
        db.close()


if __name__ == "__main__":
    success = test_breakpoint_resume()
    sys.exit(0 if success else 1)
