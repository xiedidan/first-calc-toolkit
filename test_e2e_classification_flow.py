"""
端到端分类流程测试

测试完整的AI分类流程：
1. 配置AI接口
2. 创建分类任务
3. 等待任务完成
4. 查看预案
5. 调整部分项目
6. 保存预案
7. 提交预案
8. 验证维度目录中的数据
"""

import sys
import os
import time
from unittest.mock import patch, MagicMock

# 添加backend目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.database import SessionLocal
from app.models import (
    Hospital, User, ModelVersion, ModelNode, ChargeItem,
    AIConfig, ClassificationTask, ClassificationPlan, PlanItem, DimensionItem
)
from app.services.ai_config_service import AIConfigService
from app.services.classification_task_service import ClassificationTaskService
from app.services.classification_plan_service import ClassificationPlanService
from app.utils.encryption import encrypt_api_key, decrypt_api_key


def setup_test_data(db):
    """设置测试数据"""
    print("设置测试数据...")
    
    # 创建医疗机构
    hospital = Hospital(
        name="测试医院E2E",
        code="TEST_E2E_001",
        is_active=True
    )
    db.add(hospital)
    db.flush()
    
    # 创建用户
    user = User(
        username="test_e2e_user",
        email="test_e2e@example.com",
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
        name="测试版本E2E",
        is_active=True
    )
    db.add(version)
    db.flush()
    
    # 创建维度节点（末级维度）
    dimensions = []
    for i in range(5):
        node = ModelNode(
            version_id=version.id,
            name=f"检查维度{i+1}",
            code=f"CHECK_{i+1}",
            node_type="dimension",
            is_leaf=True,
            sort_order=i + 1
        )
        db.add(node)
        db.flush()
        dimensions.append(node)
    
    # 创建医技收费项目
    charge_items = []
    charge_categories = ["检查费", "放射费", "化验费"]
    for i in range(10):
        item = ChargeItem(
            hospital_id=hospital.id,
            item_code=f"ITEM_E2E_{i+1:03d}",
            item_name=f"医技项目{i+1}",
            charge_category=charge_categories[i % 3],
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
        # 删除维度项目
        db.query(DimensionItem).filter(
            DimensionItem.hospital_id == test_data["hospital"].id
        ).delete()
        
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
def test_e2e_classification_flow(mock_sleep, mock_ai_call):
    """
    端到端分类流程测试
    
    验证需求: 1.1-12.5
    """
    print("\n" + "="*80)
    print("开始端到端分类流程测试")
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
        print(f"  - 医疗机构ID: {hospital_id}")
        print(f"  - 用户ID: {user_id}")
        print(f"  - 模型版本ID: {version_id}")
        print(f"  - 维度数量: {len(dimensions)}")
        print(f"  - 收费项目数量: {len(charge_items)}")
        
        # 步骤2: 配置AI接口
        print("\n步骤1: 配置AI接口...")
        ai_service = AIConfigService(db)
        
        config_data = {
            "api_endpoint": "https://api.deepseek.com/v1",
            "api_key": "test-api-key-12345",
            "prompt_template": "请为以下医技项目选择合适的维度：\n项目名称：{item_name}\n可选维度：{dimensions}",
            "call_delay": 0.1,
            "daily_limit": 1000,
            "batch_size": 100
        }
        
        config = ai_service.create_or_update_config(hospital_id, config_data)
        print(f"✓ AI配置创建成功，ID: {config.id}")
        
        # 验证密钥加密
        decrypted_key = decrypt_api_key(config.api_key_encrypted)
        assert decrypted_key == "test-api-key-12345", "密钥解密失败"
        print("✓ API密钥加密验证通过")
        
        # 步骤3: 创建分类任务
        print("\n步骤2: 创建分类任务...")
        task_service = ClassificationTaskService(db)
        
        # 模拟AI接口返回
        def mock_ai_response(*args, **kwargs):
            # 随机返回一个维度
            import random
            dimension = random.choice(dimensions)
            return {
                "dimension_id": dimension.id,
                "confidence": round(random.uniform(0.6, 0.95), 4)
            }
        
        mock_ai_call.side_effect = mock_ai_response
        
        task_data = {
            "task_name": "E2E测试任务",
            "model_version_id": version_id,
            "charge_categories": ["检查费", "放射费", "化验费"]
        }
        
        task = task_service.create_task(hospital_id, user_id, task_data)
        print(f"✓ 分类任务创建成功，ID: {task.id}")
        print(f"  - 任务名称: {task.task_name}")
        print(f"  - 总项目数: {task.total_items}")
        print(f"  - 状态: {task.status}")
        
        # 步骤4: 等待任务完成（模拟异步处理）
        print("\n步骤3: 等待任务完成...")
        
        # 手动执行分类任务（因为我们在测试环境中）
        from app.tasks.classification_tasks import classify_items_task
        
        # 执行任务
        classify_items_task(task.id, hospital_id)
        
        # 刷新任务状态
        db.refresh(task)
        print(f"✓ 任务处理完成")
        print(f"  - 状态: {task.status}")
        print(f"  - 已处理: {task.processed_items}/{task.total_items}")
        print(f"  - 失败: {task.failed_items}")
        
        assert task.status == "completed", f"任务状态应为completed，实际为{task.status}"
        assert task.processed_items == task.total_items, "所有项目应已处理"
        
        # 步骤5: 查看预案
        print("\n步骤4: 查看预案...")
        plan_service = ClassificationPlanService(db)
        
        # 获取预案
        plan = db.query(ClassificationPlan).filter(
            ClassificationPlan.task_id == task.id
        ).first()
        
        assert plan is not None, "预案应已生成"
        print(f"✓ 预案已生成，ID: {plan.id}")
        
        # 获取预案项目
        items = plan_service.get_plan_items(plan.id, hospital_id)
        print(f"✓ 预案包含 {len(items)} 个项目")
        
        # 显示前3个项目
        for i, item in enumerate(items[:3]):
            print(f"  项目{i+1}: {item['charge_item_name']}")
            print(f"    - AI建议维度: {item['ai_suggested_dimension_name']}")
            print(f"    - 确信度: {item['ai_confidence']}")
        
        # 步骤6: 调整部分项目
        print("\n步骤5: 调整部分项目...")
        
        # 调整前3个项目的维度
        adjusted_count = 0
        for item in items[:3]:
            # 选择一个不同的维度
            new_dimension = dimensions[0] if item['ai_suggested_dimension_id'] != dimensions[0].id else dimensions[1]
            
            update_data = {
                "user_set_dimension_id": new_dimension.id
            }
            
            updated_item = plan_service.update_plan_item(
                plan.id,
                item['id'],
                hospital_id,
                update_data
            )
            
            assert updated_item['is_adjusted'] == True, "项目应标记为已调整"
            adjusted_count += 1
        
        print(f"✓ 已调整 {adjusted_count} 个项目")
        
        # 步骤7: 保存预案
        print("\n步骤6: 保存预案...")
        
        plan_update = {
            "plan_name": "E2E测试预案",
            "status": "draft"
        }
        
        updated_plan = plan_service.update_plan(plan.id, hospital_id, plan_update)
        print(f"✓ 预案已保存")
        print(f"  - 预案名称: {updated_plan['plan_name']}")
        print(f"  - 状态: {updated_plan['status']}")
        
        # 步骤8: 提交预览
        print("\n步骤7: 生成提交预览...")
        
        preview = plan_service.generate_submit_preview(plan.id, hospital_id)
        print(f"✓ 提交预览生成成功")
        print(f"  - 新增项目: {preview['new_count']}")
        print(f"  - 覆盖项目: {preview['overwrite_count']}")
        
        assert preview['new_count'] + preview['overwrite_count'] == len(items), "预览统计应匹配项目总数"
        
        # 步骤9: 提交预案
        print("\n步骤8: 提交预案...")
        
        result = plan_service.submit_plan(plan.id, hospital_id)
        print(f"✓ 预案提交成功")
        print(f"  - 新增: {result['new_count']}")
        print(f"  - 更新: {result['update_count']}")
        
        # 刷新预案状态
        db.refresh(plan)
        assert plan.status == "submitted", "预案状态应为submitted"
        assert plan.submitted_at is not None, "应记录提交时间"
        
        # 步骤10: 验证维度目录中的数据
        print("\n步骤9: 验证维度目录中的数据...")
        
        # 查询维度项目
        dimension_items = db.query(DimensionItem).filter(
            DimensionItem.hospital_id == hospital_id,
            DimensionItem.charge_item_id.in_([item.id for item in charge_items])
        ).all()
        
        print(f"✓ 维度目录中有 {len(dimension_items)} 个项目")
        assert len(dimension_items) == len(charge_items), "所有收费项目应已添加到维度目录"
        
        # 验证调整的项目
        adjusted_items = [item for item in items[:3]]
        for adj_item in adjusted_items:
            dim_item = db.query(DimensionItem).filter(
                DimensionItem.hospital_id == hospital_id,
                DimensionItem.charge_item_id == adj_item['charge_item_id']
            ).first()
            
            assert dim_item is not None, f"项目{adj_item['charge_item_name']}应在维度目录中"
            
            # 验证使用的是用户设置的维度
            expected_dimension_id = adj_item['user_set_dimension_id']
            assert dim_item.node_id == expected_dimension_id, \
                f"项目{adj_item['charge_item_name']}应使用用户设置的维度"
        
        print("✓ 调整的项目验证通过")
        
        # 验证未调整的项目使用AI建议
        unadjusted_items = items[3:]
        for item in unadjusted_items:
            dim_item = db.query(DimensionItem).filter(
                DimensionItem.hospital_id == hospital_id,
                DimensionItem.charge_item_id == item['charge_item_id']
            ).first()
            
            assert dim_item is not None, f"项目{item['charge_item_name']}应在维度目录中"
            
            # 验证使用的是AI建议的维度
            expected_dimension_id = item['ai_suggested_dimension_id']
            assert dim_item.node_id == expected_dimension_id, \
                f"项目{item['charge_item_name']}应使用AI建议的维度"
        
        print("✓ 未调整的项目验证通过")
        
        print("\n" + "="*80)
        print("✓ 端到端分类流程测试通过！")
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
    success = test_e2e_classification_flow()
    sys.exit(0 if success else 1)
