"""
FastAPI主应用入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings

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
from app.api import auth, users, departments, dimension_items, charge_items, model_versions, model_nodes, calculation_workflows, calculation_steps, data_sources, system_settings, calculation_tasks

# 注册路由
app.include_router(auth.router, prefix="/api/v1/auth", tags=["认证"])
app.include_router(users.router, prefix="/api/v1/users", tags=["用户管理"])
app.include_router(charge_items.router, prefix="/api/v1/charge-items", tags=["收费项目管理"])
app.include_router(departments.router, prefix="/api/v1/departments", tags=["科室管理"])
app.include_router(dimension_items.router, prefix="/api/v1/dimension-items", tags=["维度目录管理"])
app.include_router(model_versions.router, prefix="/api/v1/model-versions", tags=["模型版本管理"])
app.include_router(model_nodes.router, prefix="/api/v1/model-nodes", tags=["模型节点管理"])
app.include_router(calculation_workflows.router, prefix="/api/v1/calculation-workflows", tags=["计算流程管理"])
app.include_router(calculation_steps.router, prefix="/api/v1/calculation-steps", tags=["计算步骤管理"])
app.include_router(data_sources.router, prefix="/api/v1/data-sources", tags=["数据源管理"])
app.include_router(system_settings.router, prefix="/api/v1/system/settings", tags=["系统设置"])
app.include_router(calculation_tasks.router, prefix="/api/v1/calculation", tags=["计算任务"])
