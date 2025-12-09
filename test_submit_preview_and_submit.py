"""
测试提交预览和批量提交功能
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models.hospital import Hospital
from app.models.model_version import ModelVersion
from app.models.model_node import ModelNode
from app.models.charge_item import ChargeItem
from app.models.classification_task import ClassificationTask, TaskStatus
from app.models.classification_plan import ClassificationPlan, PlanStatus
from app.models.plan_item import PlanItem, ProcessingStatus
from app.models.dimension_item_mapping import DimensionItemMapping
from app.services.classification_plan_service import ClassificationPlanService
from app.schemas.classification_plan import SubmitPlanRequest


# 测试数据库配置
TEST_DATABASE_URL = "sqlite:///./test_submit_preview.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """创建测试数据库会话"""
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # 清理数据库
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_data(db):
    """创建测试数据"""
    # 创建医疗机构
    hospital = Hospital(
        id=1,
        name="测试医院",
        code="TEST001",
        is_active=True
    )
    db.add(hospital)
    
    # 创建模型版本
    version = ModelVersion(
        id=1,
        hospital_id=1,
        version="v1.0",
        name="测试版本",
        is_active=True
    )
    db.add(version)
    
    # 创建维度节点（序列 -> 一级维度 -> 二级维度）
    sequence = ModelNode(
        id=1,
        hospital_id=1,
        version_id=1,
        code="SEQ001",
        name="序列A",
        node_type="sequence",
        is_leaf=False,
        parent_id=None
    )
    db.add(sequence)
    
    dimension1 = ModelNode(
        id=2,
        hospital_id=1,
        version_id=1,
        code="DIM001",
        name="一级维度",
        node_type="dimension",
        is_leaf=False,
        parent_id=1
    )
    db.add(dimension1)
    
    dimension2_1 = ModelNode(
        id=3,
        hospital_id=1,
        version_id=1,
        code="DIM002",
        name="二级维度A",
        node_type="dimension",
        is_leaf=True,
        parent_id=2
    )
    db.add(dimension2_1)
    
    dimension2_2 = ModelNode(
        id=4,
        hospital_id=1,
        version_id=1,
        code="DIM003",
        name="二级维度B",
        node_type="dimension",
        is_leaf=True,
        parent_id=2
    )
    db.add(dimension2_2)
    
    # 创建收费项目
    charge_item1 = ChargeItem(
        id=1,
        hospital_id=1,
        item_code="ITEM001",
        item_name="CT检查",
        charge_category="检查费"
    )
    db.add(charge_item1)
    
    charge_item2 = ChargeItem(
        id=2,
        hospital_id=1,
        item_code="ITEM002",
        item_name="MRI检查",
        charge_category="检查费"
    )
    db.add(charge_item2)
    
    charge_item3 = ChargeItem(
        id=3,
        hospital_id=1,
        item_code="ITEM003",
        item_name="X光检查",
        charge_category="放射费"
    )
    db.add(charge_item3)
    
    # 创建已存在的映射（用于测试覆盖场景）
    existing_mapping = DimensionItemMapping(
        id=1,
        hospital_id=1,
        dimension_code="DIM002",  # 原来映射到二级维度A
        item_code="ITEM001",
        charge_item_id=1
    )
    db.add(existing_mapping)
    
    # 创建分类任务
    task = ClassificationTask(
        id=1,
        hospital_id=1,
        task_name="测试分类任务",
        model_version_id=1,
        charge_categories=["检查费", "放射费"],
        status=TaskStatus.completed,
        total_items=3,
        processed_items=3,
        created_by=1
    )
    db.add(task)
    
    # 创建分类预案
    plan = ClassificationPlan(
        id=1,
        hospital_id=1,
        task_id=1,
        plan_name="测试预案",
        status=PlanStatus.draft
    )
    db.add(plan)
    
    # 创建预案项目
    # 项目1：已存在映射，将被覆盖（从DIM002改为DIM003）
    item1 = PlanItem(
        id=1,
        hospital_id=1,
        plan_id=1,
        charge_item_id=1,
        charge_item_name="CT检查",
        ai_suggested_dimension_id=3,  # AI建议：二级维度A
        ai_confidence=0.85,
        user_set_dimension_id=4,  # 用户调整为：二级维度B
        is_adjusted=True,
        processing_status=ProcessingStatus.completed
    )
    db.add(item1)
    
    # 项目2：新增项目
    item2 = PlanItem(
        id=2,
        hospital_id=1,
        plan_id=1,
        charge_item_id=2,
        charge_item_name="MRI检查",
        ai_suggested_dimension_id=3,  # AI建议：二级维度A
        ai_confidence=0.92,
        user_set_dimension_id=None,  # 用户未调整，使用AI建议
        is_adjusted=False,
        processing_status=ProcessingStatus.completed
    )
    db.add(item2)
    
    # 项目3：新增项目
    item3 = PlanItem(
        id=3,
        hospital_id=1,
        plan_id=1,
        charge_item_id=3,
        charge_item_name="X光检查",
        ai_suggested_dimension_id=4,  # AI建议：二级维度B
        ai_confidence=0.78,
        user_set_dimension_id=None,  # 用户未调整，使用AI建议
        is_adjusted=False,
        processing_status=ProcessingStatus.completed
    )
    db.add(item3)
    
    db.commit()
    
    return {
        "hospital_id": 1,
        "plan_id": 1,
        "task_id": 1,
        "version_id": 1
    }


def test_generate_submit_preview(db, test_data):
    """测试生成提交预览功能"""
    print("\n=== 测试生成提交预览 ===")
    
    # 调用服务方法
    preview = ClassificationPlanService.generate_submit_preview(
        db=db,
        hospital_id=test_data["hospital_id"],
        plan_id=test_data["plan_id"]
    )
    
    print(f"\n预览结果:")
    print(f"  预案名称: {preview.plan_name}")
    print(f"  总项目数: {preview.total_items}")
    print(f"  新增数量: {preview.new_count}")
    print(f"  覆盖数量: {preview.overwrite_count}")
    
    # 验证统计数字
    assert preview.total_items == 3, "总项目数应为3"
    assert preview.new_count == 2, "新增项目应为2个（MRI和X光）"
    assert preview.overwrite_count == 1, "覆盖项目应为1个（CT）"
    
    # 验证新增项目
    print(f"\n新增项目:")
    for item in preview.new_items:
        print(f"  - {item.item_name} -> {item.dimension_name} ({item.dimension_path})")
    
    assert len(preview.new_items) == 2
    new_item_names = [item.item_name for item in preview.new_items]
    assert "MRI检查" in new_item_names
    assert "X光检查" in new_item_names
    
    # 验证覆盖项目
    print(f"\n覆盖项目:")
    for item in preview.overwrite_items:
        print(f"  - {item.item_name}")
        print(f"    原维度: {item.old_dimension_name} ({item.old_dimension_path})")
        print(f"    新维度: {item.dimension_name} ({item.dimension_path})")
    
    assert len(preview.overwrite_items) == 1
    overwrite_item = preview.overwrite_items[0]
    assert overwrite_item.item_name == "CT检查"
    assert overwrite_item.old_dimension_name == "二级维度A"
    assert overwrite_item.dimension_name == "二级维度B"
    
    print("\n✓ 提交预览测试通过")


def test_submit_plan(db, test_data):
    """测试批量提交功能"""
    print("\n=== 测试批量提交 ===")
    
    # 提交前检查预案状态
    plan_before = db.query(ClassificationPlan).filter_by(id=test_data["plan_id"]).first()
    assert plan_before.status == PlanStatus.draft, "提交前预案状态应为draft"
    
    # 提交前检查映射数量
    mappings_before = db.query(DimensionItemMapping).filter_by(
        hospital_id=test_data["hospital_id"]
    ).count()
    print(f"\n提交前映射数量: {mappings_before}")
    
    # 调用服务方法提交预案
    submit_request = SubmitPlanRequest()
    result = ClassificationPlanService.submit_plan(
        db=db,
        hospital_id=test_data["hospital_id"],
        plan_id=test_data["plan_id"],
        submit_data=submit_request
    )
    
    print(f"\n提交结果:")
    print(f"  成功: {result.success}")
    print(f"  消息: {result.message}")
    print(f"  新增数量: {result.new_count}")
    print(f"  覆盖数量: {result.overwrite_count}")
    print(f"  提交时间: {result.submitted_at}")
    
    # 验证提交结果
    assert result.success is True, "提交应该成功"
    assert result.new_count == 2, "应新增2个映射"
    assert result.overwrite_count == 1, "应覆盖1个映射"
    assert result.submitted_at is not None, "应记录提交时间"
    
    # 验证预案状态已更新
    plan_after = db.query(ClassificationPlan).filter_by(id=test_data["plan_id"]).first()
    assert plan_after.status == PlanStatus.submitted, "提交后预案状态应为submitted"
    assert plan_after.submitted_at is not None, "应记录提交时间"
    
    # 验证映射数量
    mappings_after = db.query(DimensionItemMapping).filter_by(
        hospital_id=test_data["hospital_id"]
    ).count()
    print(f"提交后映射数量: {mappings_after}")
    assert mappings_after == 3, "提交后应有3个映射（1个原有+2个新增）"
    
    # 验证具体映射
    print(f"\n映射详情:")
    mappings = db.query(DimensionItemMapping).filter_by(
        hospital_id=test_data["hospital_id"]
    ).all()
    
    for mapping in mappings:
        charge_item = db.query(ChargeItem).filter_by(id=mapping.charge_item_id).first()
        dimension = db.query(ModelNode).filter_by(code=mapping.dimension_code).first()
        print(f"  - {charge_item.item_name} -> {dimension.name} (code: {mapping.dimension_code})")
    
    # 验证CT检查的映射已更新（从DIM002改为DIM003）
    ct_mapping = db.query(DimensionItemMapping).filter_by(
        hospital_id=test_data["hospital_id"],
        charge_item_id=1
    ).first()
    assert ct_mapping is not None, "CT检查的映射应存在"
    assert ct_mapping.dimension_code == "DIM003", "CT检查应映射到二级维度B（DIM003）"
    
    # 验证MRI检查的映射已创建
    mri_mapping = db.query(DimensionItemMapping).filter_by(
        hospital_id=test_data["hospital_id"],
        charge_item_id=2
    ).first()
    assert mri_mapping is not None, "MRI检查的映射应存在"
    assert mri_mapping.dimension_code == "DIM002", "MRI检查应映射到二级维度A（DIM002）"
    
    # 验证X光检查的映射已创建
    xray_mapping = db.query(DimensionItemMapping).filter_by(
        hospital_id=test_data["hospital_id"],
        charge_item_id=3
    ).first()
    assert xray_mapping is not None, "X光检查的映射应存在"
    assert xray_mapping.dimension_code == "DIM003", "X光检查应映射到二级维度B（DIM003）"
    
    print("\n✓ 批量提交测试通过")


def test_submit_plan_duplicate_prevention(db, test_data):
    """测试防止重复提交"""
    print("\n=== 测试防止重复提交 ===")
    
    # 第一次提交
    submit_request = SubmitPlanRequest()
    result1 = ClassificationPlanService.submit_plan(
        db=db,
        hospital_id=test_data["hospital_id"],
        plan_id=test_data["plan_id"],
        submit_data=submit_request
    )
    assert result1.success is True, "第一次提交应该成功"
    print("第一次提交成功")
    
    # 尝试第二次提交
    try:
        result2 = ClassificationPlanService.submit_plan(
            db=db,
            hospital_id=test_data["hospital_id"],
            plan_id=test_data["plan_id"],
            submit_data=submit_request
        )
        assert False, "第二次提交应该抛出异常"
    except ValueError as e:
        print(f"第二次提交被阻止: {str(e)}")
        assert "已提交" in str(e) or "重复提交" in str(e), "错误消息应提示已提交"
    
    print("\n✓ 防止重复提交测试通过")


def test_submit_plan_rollback_on_error(db, test_data):
    """测试提交失败时的事务回滚"""
    print("\n=== 测试事务回滚 ===")
    
    # 删除一个维度节点，使提交过程中出现错误
    db.query(ModelNode).filter_by(id=4).delete()
    db.commit()
    
    # 提交前的映射数量
    mappings_before = db.query(DimensionItemMapping).filter_by(
        hospital_id=test_data["hospital_id"]
    ).count()
    print(f"提交前映射数量: {mappings_before}")
    
    # 尝试提交（应该失败）
    submit_request = SubmitPlanRequest()
    result = ClassificationPlanService.submit_plan(
        db=db,
        hospital_id=test_data["hospital_id"],
        plan_id=test_data["plan_id"],
        submit_data=submit_request
    )
    
    print(f"\n提交结果:")
    print(f"  成功: {result.success}")
    print(f"  消息: {result.message}")
    
    # 验证提交失败
    assert result.success is False, "提交应该失败"
    
    # 验证预案状态未改变
    plan = db.query(ClassificationPlan).filter_by(id=test_data["plan_id"]).first()
    assert plan.status == PlanStatus.draft, "失败后预案状态应保持为draft"
    assert plan.submitted_at is None, "失败后不应记录提交时间"
    
    # 验证映射数量未改变（事务回滚）
    mappings_after = db.query(DimensionItemMapping).filter_by(
        hospital_id=test_data["hospital_id"]
    ).count()
    print(f"提交后映射数量: {mappings_after}")
    assert mappings_after == mappings_before, "失败后映射数量应保持不变（事务回滚）"
    
    print("\n✓ 事务回滚测试通过")


if __name__ == "__main__":
    print("开始测试提交预览和批量提交功能...")
    print("=" * 60)
    
    # 创建数据库会话
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    
    try:
        # 创建测试数据
        test_data_fixture = pytest.fixture(test_data)
        data = test_data(db)
        
        # 运行测试
        test_generate_submit_preview(db, data)
        
        # 重新创建数据库（清理上一个测试的数据）
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        db = TestingSessionLocal()
        data = test_data(db)
        
        test_submit_plan(db, data)
        
        # 重新创建数据库
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        db = TestingSessionLocal()
        data = test_data(db)
        
        test_submit_plan_duplicate_prevention(db, data)
        
        # 重新创建数据库
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        db = TestingSessionLocal()
        data = test_data(db)
        
        test_submit_plan_rollback_on_error(db, data)
        
        print("\n" + "=" * 60)
        print("✓ 所有测试通过！")
        
    except Exception as e:
        print(f"\n✗ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()
        # 清理测试数据库
        Base.metadata.drop_all(bind=engine)
        if os.path.exists("test_submit_preview.db"):
            os.remove("test_submit_preview.db")
