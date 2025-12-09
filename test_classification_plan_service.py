"""
测试分类预案服务
"""
import sys
import os

# 添加backend目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models.hospital import Hospital
from app.models.classification_task import ClassificationTask, TaskStatus
from app.models.classification_plan import ClassificationPlan, PlanStatus
from app.models.plan_item import PlanItem, ProcessingStatus
from app.models.model_version import ModelVersion
from app.models.model_node import ModelNode
from app.models.charge_item import ChargeItem
from app.models.dimension_item_mapping import DimensionItemMapping
from app.services.classification_plan_service import ClassificationPlanService
from app.schemas.classification_plan import (
    PlanItemQueryParams,
    PlanItemUpdate,
    UpdatePlanRequest,
    SubmitPlanRequest
)
from datetime import datetime
from decimal import Decimal

# 创建测试数据库
engine = create_engine("sqlite:///test_classification_plan.db")
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)


def test_classification_plan_service():
    """测试分类预案服务"""
    db = SessionLocal()
    
    try:
        print("=" * 80)
        print("测试分类预案服务")
        print("=" * 80)
        
        # 1. 创建测试数据
        print("\n1. 创建测试数据...")
        
        # 创建医疗机构
        hospital = Hospital(
            id=1,
            name="测试医院",
            code="TEST001",
            is_active=True
        )
        db.add(hospital)
        db.commit()
        print(f"   ✓ 创建医疗机构: {hospital.name}")
        
        # 创建模型版本
        model_version = ModelVersion(
            id=1,
            hospital_id=1,
            version_name="测试版本",
            is_active=True
        )
        db.add(model_version)
        db.commit()
        print(f"   ✓ 创建模型版本: {model_version.version_name}")
        
        # 创建维度节点
        root_node = ModelNode(
            id=1,
            hospital_id=1,
            version_id=1,
            name="根节点",
            code="ROOT",
            node_type="sequence",
            is_leaf=False,
            parent_id=None
        )
        db.add(root_node)
        
        leaf_node_1 = ModelNode(
            id=2,
            hospital_id=1,
            version_id=1,
            name="检查维度",
            code="DIM001",
            node_type="dimension",
            is_leaf=True,
            parent_id=1
        )
        db.add(leaf_node_1)
        
        leaf_node_2 = ModelNode(
            id=3,
            hospital_id=1,
            version_id=1,
            name="化验维度",
            code="DIM002",
            node_type="dimension",
            is_leaf=True,
            parent_id=1
        )
        db.add(leaf_node_2)
        db.commit()
        print(f"   ✓ 创建维度节点: 3个")
        
        # 创建收费项目
        charge_item_1 = ChargeItem(
            id=1,
            hospital_id=1,
            item_code="CI001",
            item_name="CT检查",
            item_category="检查费"
        )
        db.add(charge_item_1)
        
        charge_item_2 = ChargeItem(
            id=2,
            hospital_id=1,
            item_code="CI002",
            item_name="血常规",
            item_category="化验费"
        )
        db.add(charge_item_2)
        db.commit()
        print(f"   ✓ 创建收费项目: 2个")
        
        # 创建分类任务
        task = ClassificationTask(
            id=1,
            hospital_id=1,
            task_name="测试分类任务",
            model_version_id=1,
            charge_categories=["检查费", "化验费"],
            status=TaskStatus.completed,
            total_items=2,
            processed_items=2,
            failed_items=0,
            created_by=1
        )
        db.add(task)
        db.commit()
        print(f"   ✓ 创建分类任务: {task.task_name}")
        
        # 创建分类预案
        plan = ClassificationPlan(
            id=1,
            hospital_id=1,
            task_id=1,
            plan_name="测试预案",
            status=PlanStatus.draft
        )
        db.add(plan)
        db.commit()
        print(f"   ✓ 创建分类预案: {plan.plan_name}")
        
        # 创建预案项目
        plan_item_1 = PlanItem(
            id=1,
            hospital_id=1,
            plan_id=1,
            charge_item_id=1,
            charge_item_name="CT检查",
            ai_suggested_dimension_id=2,
            ai_confidence=Decimal("0.95"),
            processing_status=ProcessingStatus.completed
        )
        db.add(plan_item_1)
        
        plan_item_2 = PlanItem(
            id=2,
            hospital_id=1,
            plan_id=1,
            charge_item_id=2,
            charge_item_name="血常规",
            ai_suggested_dimension_id=3,
            ai_confidence=Decimal("0.45"),
            processing_status=ProcessingStatus.completed
        )
        db.add(plan_item_2)
        db.commit()
        print(f"   ✓ 创建预案项目: 2个")
        
        # 2. 测试获取预案列表
        print("\n2. 测试获取预案列表...")
        plans_response = ClassificationPlanService.get_plans(
            db=db,
            hospital_id=1,
            skip=0,
            limit=10
        )
        print(f"   ✓ 查询到 {plans_response.total} 个预案")
        assert plans_response.total == 1
        assert plans_response.items[0].plan_name == "测试预案"
        assert plans_response.items[0].total_items == 2
        
        # 3. 测试获取预案详情
        print("\n3. 测试获取预案详情...")
        plan_detail = ClassificationPlanService.get_plan_detail(
            db=db,
            hospital_id=1,
            plan_id=1
        )
        print(f"   ✓ 预案名称: {plan_detail.plan_name}")
        print(f"   ✓ 总项目数: {plan_detail.total_items}")
        print(f"   ✓ 低确信度项目数: {plan_detail.low_confidence_items}")
        assert plan_detail.total_items == 2
        assert plan_detail.low_confidence_items == 1  # 血常规的确信度是0.45
        
        # 4. 测试获取预案项目列表
        print("\n4. 测试获取预案项目列表...")
        query_params = PlanItemQueryParams(
            page=1,
            size=10
        )
        items_response = ClassificationPlanService.get_plan_items(
            db=db,
            hospital_id=1,
            plan_id=1,
            query_params=query_params
        )
        print(f"   ✓ 查询到 {items_response.total} 个项目")
        assert items_response.total == 2
        
        # 5. 测试按确信度排序
        print("\n5. 测试按确信度排序...")
        query_params_sorted = PlanItemQueryParams(
            sort_by="confidence_asc",
            page=1,
            size=10
        )
        items_sorted = ClassificationPlanService.get_plan_items(
            db=db,
            hospital_id=1,
            plan_id=1,
            query_params=query_params_sorted
        )
        print(f"   ✓ 第一个项目: {items_sorted.items[0].charge_item_name}, 确信度: {items_sorted.items[0].ai_confidence}")
        assert float(items_sorted.items[0].ai_confidence) < float(items_sorted.items[1].ai_confidence)
        
        # 6. 测试筛选低确信度项目
        print("\n6. 测试筛选低确信度项目...")
        query_params_filtered = PlanItemQueryParams(
            max_confidence=0.5,
            page=1,
            size=10
        )
        items_filtered = ClassificationPlanService.get_plan_items(
            db=db,
            hospital_id=1,
            plan_id=1,
            query_params=query_params_filtered
        )
        print(f"   ✓ 筛选到 {items_filtered.total} 个低确信度项目")
        assert items_filtered.total == 1
        assert items_filtered.items[0].charge_item_name == "血常规"
        
        # 7. 测试调整项目维度
        print("\n7. 测试调整项目维度...")
        update_data = PlanItemUpdate(dimension_id=2)  # 将血常规改为检查维度
        updated_item = ClassificationPlanService.update_plan_item(
            db=db,
            hospital_id=1,
            plan_id=1,
            item_id=2,
            update_data=update_data
        )
        print(f"   ✓ 项目 {updated_item.charge_item_name} 维度已调整")
        print(f"   ✓ AI建议: {updated_item.ai_suggested_dimension_name}")
        print(f"   ✓ 用户设置: {updated_item.user_set_dimension_name}")
        print(f"   ✓ 最终维度: {updated_item.final_dimension_name}")
        assert updated_item.is_adjusted == True
        assert updated_item.user_set_dimension_id == 2
        assert updated_item.final_dimension_id == 2
        
        # 8. 测试更新预案名称
        print("\n8. 测试更新预案名称...")
        update_plan_data = UpdatePlanRequest(plan_name="更新后的预案名称")
        updated_plan = ClassificationPlanService.update_plan(
            db=db,
            hospital_id=1,
            plan_id=1,
            update_data=update_plan_data
        )
        print(f"   ✓ 预案名称已更新: {updated_plan.plan_name}")
        assert updated_plan.plan_name == "更新后的预案名称"
        
        # 9. 测试生成提交预览
        print("\n9. 测试生成提交预览...")
        preview = ClassificationPlanService.generate_submit_preview(
            db=db,
            hospital_id=1,
            plan_id=1
        )
        print(f"   ✓ 总项目数: {preview.total_items}")
        print(f"   ✓ 新增项目数: {preview.new_count}")
        print(f"   ✓ 覆盖项目数: {preview.overwrite_count}")
        assert preview.total_items == 2
        assert preview.new_count == 2  # 都是新增，因为还没有映射
        
        # 10. 测试提交预案
        print("\n10. 测试提交预案...")
        submit_data = SubmitPlanRequest(confirm=True)
        submit_result = ClassificationPlanService.submit_plan(
            db=db,
            hospital_id=1,
            plan_id=1,
            submit_data=submit_data
        )
        print(f"   ✓ 提交结果: {submit_result.message}")
        print(f"   ✓ 新增: {submit_result.new_count} 项")
        print(f"   ✓ 覆盖: {submit_result.overwrite_count} 项")
        assert submit_result.success == True
        assert submit_result.new_count == 2
        
        # 验证映射已创建
        mappings = db.query(DimensionItemMapping).filter(
            DimensionItemMapping.hospital_id == 1
        ).all()
        print(f"   ✓ 创建了 {len(mappings)} 个维度映射")
        assert len(mappings) == 2
        
        # 验证预案状态已更新
        updated_plan = db.query(ClassificationPlan).filter(
            ClassificationPlan.id == 1
        ).first()
        print(f"   ✓ 预案状态: {updated_plan.status.value}")
        assert updated_plan.status == PlanStatus.submitted
        
        # 11. 测试再次生成预览（应该显示覆盖）
        print("\n11. 测试再次生成预览（应该显示覆盖）...")
        # 创建新预案
        new_plan = ClassificationPlan(
            id=2,
            hospital_id=1,
            task_id=1,
            plan_name="第二个预案",
            status=PlanStatus.draft
        )
        db.add(new_plan)
        
        # 创建新预案项目（相同的收费项目）
        new_plan_item = PlanItem(
            id=3,
            hospital_id=1,
            plan_id=2,
            charge_item_id=1,
            charge_item_name="CT检查",
            ai_suggested_dimension_id=3,  # 改为化验维度
            ai_confidence=Decimal("0.88"),
            processing_status=ProcessingStatus.completed
        )
        db.add(new_plan_item)
        db.commit()
        
        preview2 = ClassificationPlanService.generate_submit_preview(
            db=db,
            hospital_id=1,
            plan_id=2
        )
        print(f"   ✓ 新增项目数: {preview2.new_count}")
        print(f"   ✓ 覆盖项目数: {preview2.overwrite_count}")
        if preview2.overwrite_count > 0:
            print(f"   ✓ 覆盖项目: {preview2.overwrite_items[0].item_name}")
            print(f"   ✓ 原维度: {preview2.overwrite_items[0].old_dimension_name}")
            print(f"   ✓ 新维度: {preview2.overwrite_items[0].dimension_name}")
        assert preview2.overwrite_count == 1  # CT检查已经有映射了
        
        print("\n" + "=" * 80)
        print("✓ 所有测试通过！")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n✗ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()
        # 清理测试数据库
        os.remove("test_classification_plan.db")


if __name__ == "__main__":
    test_classification_plan_service()
