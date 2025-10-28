"""
最小化测试应用
"""
from fastapi import FastAPI
from app.api.system_settings import router as system_settings_router

app = FastAPI()

# 注册系统设置路由
app.include_router(system_settings_router, prefix="/api/v1/system/settings", tags=["系统设置"])

@app.get("/")
def root():
    return {"message": "Test app"}

if __name__ == "__main__":
    import uvicorn
    print("启动测试服务器...")
    print("访问: http://localhost:8001/docs")
    print("测试: http://localhost:8001/api/v1/system/settings")
    uvicorn.run(app, host="0.0.0.0", port=8001)
