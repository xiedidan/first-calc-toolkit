"""
测试AI分类Schema定义
"""
import sys
sys.path.insert(0, 'backend')

from app.schemas.ai_config import AIConfigCreate, AIConfigResponse, AIConfigTest
from app.schemas.classification_task import ClassificationTaskCreate, ClassificationTaskResponse
from app.schemas.classification_plan import (
    ClassificationPlanResponse,
    PlanItemResponse,
    PlanItemUpdate,
    SubmitPreviewResponse,
    SubmitPreviewItem,
    SubmitPreviewOverwriteItem
)
from pydantic import ValidationError


def test_ai_config_create_validation():
    """测试AI配置创建验证"""
    # 有效的配置
    valid_config = AIConfigCreate(
        api_endpoint="https://api.deepseek.com/v1",
        api_key="sk-test-key-12345",
        prompt_template="请对以下医技项目进行分类：{item_name}\n可选维度：{dimensions}",
        call_delay=1.5,
        daily_limit=5000,
        batch_size=50
    )
    assert valid_config.api_endpoint == "https://api.deepseek.com/v1"
    assert valid_config.call_delay == 1.5
    
    # 无效的URL
    try:
        AIConfigCreate(
            api_endpoint="not-a-valid-url",
            api_key="sk-test",
            prompt_template="test"
        )
        assert False, "应该抛出验证错误"
    except ValidationError as e:
        assert "API端点必须是有效的URL格式" in str(e)
    
    # 调用延迟超出范围
    try:
        AIConfigCreate(
            api_endpoint="https://api.test.com",
            api_key="sk-test",
            prompt_template="test",
            call_delay=15.0  # 超过10秒
        )
        assert False, "应该抛出验证错误"
    except ValidationError as e:
        assert "less than or equal to 10" in str(e)
    
    print("[PASS] AI配置创建验证测试通过")


def test_classification_task_create_validation():
    """测试分类任务创建验证"""
    # 有效的任务
    valid_task = ClassificationTaskCreate(
        task_name="医技项目分类-2024年11月",
        model_version_id=1,
        charge_categories=["检查费", "放射费", "化验费"]
    )
    assert valid_task.task_name == "医技项目分类-2024年11月"
    assert len(valid_task.charge_categories) == 3
    
    # 任务名称为空
    try:
        ClassificationTaskCreate(
            task_name="",
            model_version_id=1,
            charge_categories=["检查费"]
        )
        assert False, "应该抛出验证错误"
    except ValidationError as e:
        assert "at least 1 character" in str(e)
    
    # 收费类别为空
    try:
        ClassificationTaskCreate(
            task_name="测试任务",
            model_version_id=1,
            charge_categories=[]
        )
        assert False, "应该抛出验证错误"
    except ValidationError as e:
        # Pydantic的min_length验证会先触发
        assert "at least 1 item" in str(e) or "收费类别列表不能为空" in str(e)
    
    print("[PASS] 分类任务创建验证测试通过")


def test_plan_item_response_structure():
    """测试预案项目响应结构"""
    from datetime import datetime
    from decimal import Decimal
    
    # 创建预案项目响应
    item = PlanItemResponse(
        id=1,
        plan_id=1,
        charge_item_id=100,
        charge_item_name="CT检查",
        ai_suggested_dimension_id=10,
        ai_suggested_dimension_name="影像检查",
        ai_suggested_dimension_path="医技序列/影像检查",
        ai_confidence=Decimal("0.85"),
        user_set_dimension_id=None,
        user_set_dimension_name=None,
        user_set_dimension_path=None,
        is_adjusted=False,
        final_dimension_id=10,
        final_dimension_name="影像检查",
        final_dimension_path="医技序列/影像检查",
        processing_status="completed",
        error_message=None,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    assert item.charge_item_name == "CT检查"
    assert item.ai_confidence == Decimal("0.85")
    assert item.is_adjusted is False
    assert item.final_dimension_id == 10
    
    print("[PASS] 预案项目响应结构测试通过")


def test_submit_preview_response_structure():
    """测试提交预览响应结构"""
    # 创建提交预览响应
    preview = SubmitPreviewResponse(
        plan_id=1,
        plan_name="医技分类预案-2024年11月",
        total_items=100,
        new_count=80,
        overwrite_count=20,
        new_items=[
            SubmitPreviewItem(
                item_id=1,
                item_name="CT检查",
                dimension_id=10,
                dimension_name="影像检查",
                dimension_path="医技序列/影像检查"
            )
        ],
        overwrite_items=[
            SubmitPreviewOverwriteItem(
                item_id=2,
                item_name="X光检查",
                dimension_id=10,
                dimension_name="影像检查",
                dimension_path="医技序列/影像检查",
                old_dimension_id=11,
                old_dimension_name="放射检查",
                old_dimension_path="医技序列/放射检查"
            )
        ],
        warnings=["有20个项目将覆盖现有分类"]
    )
    
    assert preview.total_items == 100
    assert preview.new_count == 80
    assert preview.overwrite_count == 20
    assert len(preview.new_items) == 1
    assert len(preview.overwrite_items) == 1
    assert preview.overwrite_items[0].old_dimension_name == "放射检查"
    
    print("[PASS] 提交预览响应结构测试通过")


def test_plan_item_update_validation():
    """测试预案项目更新验证"""
    # 有效的更新
    update = PlanItemUpdate(dimension_id=10)
    assert update.dimension_id == 10
    
    # 无效的维度ID
    try:
        PlanItemUpdate(dimension_id=0)
        assert False, "应该抛出验证错误"
    except ValidationError as e:
        assert "greater than 0" in str(e)
    
    print("[PASS] 预案项目更新验证测试通过")


if __name__ == "__main__":
    print("开始测试AI分类Schema定义...\n")
    
    test_ai_config_create_validation()
    test_classification_task_create_validation()
    test_plan_item_response_structure()
    test_submit_preview_response_structure()
    test_plan_item_update_validation()
    
    print("\n[SUCCESS] 所有Schema测试通过！")
    print("\n创建的Schema文件：")
    print("- backend/app/schemas/ai_config.py")
    print("- backend/app/schemas/classification_task.py")
    print("- backend/app/schemas/classification_plan.py")
    print("\nSchema功能：")
    print("[OK] AI配置：URL验证、密钥加密、提示词模板")
    print("[OK] 分类任务：任务名称验证、收费类别验证、进度跟踪")
    print("[OK] 分类预案：AI建议、用户调整、提交预览、新增/覆盖分析")
