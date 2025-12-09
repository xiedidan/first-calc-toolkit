"""
FastAPI主应用入口
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
import traceback
import logging

from app.config import settings

# 配置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="医院科室业务价值评估工具API",
    docs_url="/docs",
    redoc_url="/redoc",
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该配置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 配置医疗机构上下文中间件
from app.middleware import HospitalContextMiddleware
app.add_middleware(HospitalContextMiddleware)


# 全局异常处理器 - 捕获 Pydantic 验证错误
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """处理请求验证错误，返回详细的错误信息"""
    logger.error(f"Validation error on {request.method} {request.url}")
    logger.error(f"Error details: {exc.errors()}")
    logger.error(f"Request body: {exc.body}")
    
    # 格式化错误信息，确保可以JSON序列化
    errors = []
    for error in exc.errors():
        error_dict = {
            "loc": list(error.get("loc", [])),
            "msg": str(error.get("msg", "")),
            "type": error.get("type", ""),
        }
        # 如果有ctx，也包含进来
        if "ctx" in error:
            error_dict["ctx"] = {k: str(v) for k, v in error["ctx"].items()}
        errors.append(error_dict)
    
    # 返回详细的错误信息
    return JSONResponse(
        status_code=422,
        content={
            "detail": "请求验证失败",
            "errors": errors,
        }
    )


@app.exception_handler(ValidationError)
async def pydantic_validation_exception_handler(request: Request, exc: ValidationError):
    """处理 Pydantic 验证错误"""
    logger.error(f"Pydantic validation error on {request.method} {request.url}")
    logger.error(f"Error details: {exc.errors()}")
    
    return JSONResponse(
        status_code=400,
        content={
            "detail": "数据验证失败",
            "errors": exc.errors()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """处理所有未捕获的异常"""
    logger.error(f"Unhandled exception on {request.method} {request.url}")
    logger.error(f"Exception type: {type(exc).__name__}")
    logger.error(f"Exception message: {str(exc)}")
    logger.error(f"Traceback:\n{traceback.format_exc()}")
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": f"服务器内部错误: {str(exc)}",
            "type": type(exc).__name__,
            "traceback": traceback.format_exc()
        }
    )


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "医院科室业务价值评估工具API",
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """健康检查端点"""
    return JSONResponse(
        content={
            "status": "healthy",
            "version": settings.APP_VERSION,
        }
    )


# 导入路由
from app.api import auth, users, roles, departments, dimension_items, charge_items, model_versions, model_nodes, calculation_workflows, calculation_steps, data_sources, system_settings, calculation_tasks, hospitals, data_templates, data_issues, orientation_rules, orientation_benchmarks, orientation_ladders, ai_config, ai_prompt_config, classification_tasks, classification_plans, cost_benchmarks, reference_values, analysis_reports

# 注册路由
app.include_router(auth.router, prefix="/api/v1/auth", tags=["认证"])
app.include_router(users.router, prefix="/api/v1/users", tags=["用户管理"])
app.include_router(roles.router, prefix="/api/v1/roles", tags=["角色管理"])
app.include_router(hospitals.router, prefix="/api/v1/hospitals", tags=["医疗机构管理"])
app.include_router(charge_items.router, prefix="/api/v1/charge-items", tags=["收费项目管理"])
app.include_router(departments.router, prefix="/api/v1/departments", tags=["科室管理"])
app.include_router(dimension_items.router, prefix="/api/v1/dimension-items", tags=["维度目录管理"])
app.include_router(model_versions.router, prefix="/api/v1/model-versions", tags=["模型版本管理"])
app.include_router(model_nodes.router, prefix="/api/v1/model-nodes", tags=["模型节点管理"])
app.include_router(calculation_workflows.router, prefix="/api/v1/calculation-workflows", tags=["计算流程管理"])
app.include_router(calculation_steps.router, prefix="/api/v1/calculation-steps", tags=["计算步骤管理"])
app.include_router(data_sources.router, prefix="/api/v1/data-sources", tags=["数据源管理"])
app.include_router(data_templates.router, prefix="/api/v1/data-templates", tags=["数据模板管理"])
app.include_router(data_issues.router, prefix="/api/v1/data-issues", tags=["数据问题记录"])
app.include_router(system_settings.router, prefix="/api/v1/system/settings", tags=["系统设置"])
app.include_router(calculation_tasks.router, prefix="/api/v1/calculation", tags=["计算任务"])
app.include_router(orientation_rules.router, prefix="/api/v1/orientation-rules", tags=["导向规则管理"])
app.include_router(orientation_benchmarks.router, prefix="/api/v1/orientation-benchmarks", tags=["导向基准管理"])
app.include_router(orientation_ladders.router, prefix="/api/v1/orientation-ladders", tags=["导向阶梯管理"])
app.include_router(cost_benchmarks.router, prefix="/api/v1/cost-benchmarks", tags=["成本基准管理"])
app.include_router(ai_config.router, prefix="/api/v1/ai-config", tags=["AI接口配置"])
app.include_router(ai_prompt_config.router, prefix="/api/v1/ai-prompt-config", tags=["AI提示词配置"])
app.include_router(classification_tasks.router, prefix="/api/v1/classification-tasks", tags=["分类任务管理"])
app.include_router(classification_plans.router, prefix="/api/v1/classification-plans", tags=["分类预案管理"])
app.include_router(reference_values.router, prefix="/api/v1/reference-values", tags=["参考价值管理"])
app.include_router(analysis_reports.router, prefix="/api/v1/analysis-reports", tags=["运营分析报告"])
