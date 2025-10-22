# 医院科室业务价值评估工具

> 一个灵活、可配置的在线平台，用于定义和计算医院各科室的业务价值（绩效）

## 📋 项目文档

- [需求文档](./需求文档.md)
- [系统设计文档](./系统设计文档.md)
- [API设计文档](./API设计文档.md)
- [部署文档](./部署文档.md)

## 🚀 快速开始

### 环境要求

- Windows 10/11
- WSL2 + Ubuntu
- Docker Desktop（已启用WSL2集成）
- Anaconda（Python环境管理）
- Node.js 18+

### 开发环境部署

#### 0. 环境检查（推荐）

```powershell
# 检查所有必要工具是否已安装
.\scripts\check-environment.ps1
```

**注意**: 如果提示"Conda not installed"，请查看 [CONDA_SETUP.md](./CONDA_SETUP.md) 配置Conda环境。

#### 1. 设置Conda环境

```powershell
# 创建并配置Python环境
.\scripts\setup-conda-env.ps1
```

#### 2. 安装前端依赖

```powershell
cd frontend
npm install
```

#### 3. 启动开发服务

```powershell
# 方式1: 一键启动所有服务（推荐）
.\scripts\dev-start-all.ps1

# 方式2: 分别启动各个服务
# 启动数据库和Redis
docker-compose -f docker-compose.dev.yml up -d

# 启动后端（新终端）
.\scripts\dev-start-backend.ps1

# 启动Celery（新终端）
.\scripts\dev-start-celery.ps1

# 启动前端（新终端）
.\scripts\dev-start-frontend.ps1
```

#### 4. 访问应用

- 前端：http://localhost:3000
- 后端API文档：http://localhost:8000/docs
- 后端ReDoc：http://localhost:8000/redoc

#### 5. 停止服务

```powershell
.\scripts\dev-stop-all.ps1
```

### 生产环境部署

```powershell
# 一键启动所有服务
docker-compose -f docker-compose.prod.yml up -d --build

# 查看服务状态
docker-compose -f docker-compose.prod.yml ps

# 查看日志
docker-compose -f docker-compose.prod.yml logs -f

# 停止服务
docker-compose -f docker-compose.prod.yml down
```

## 📁 项目结构

```
first-calc-toolkit/
├── backend/                    # 后端代码
│   ├── app/                   # 应用代码
│   │   ├── api/              # API路由
│   │   ├── models/           # 数据模型
│   │   ├── schemas/          # Pydantic模型
│   │   ├── services/         # 业务逻辑
│   │   ├── utils/            # 工具函数
│   │   ├── main.py           # FastAPI主入口
│   │   ├── config.py         # 配置文件
│   │   ├── database.py       # 数据库连接
│   │   └── celery_app.py     # Celery配置
│   ├── alembic/              # 数据库迁移
│   ├── tests/                # 测试代码
│   ├── requirements.txt      # Python依赖
│   ├── .env.dev             # 开发环境配置
│   ├── .env.prod            # 生产环境配置
│   └── Dockerfile           # Docker镜像
├── frontend/                  # 前端代码
│   ├── src/                  # 源代码
│   │   ├── views/           # 页面组件
│   │   ├── router/          # 路由配置
│   │   ├── App.vue          # 根组件
│   │   └── main.ts          # 入口文件
│   ├── public/               # 静态资源
│   ├── package.json          # Node依赖
│   ├── vite.config.ts        # Vite配置
│   ├── nginx.conf            # Nginx配置
│   └── Dockerfile            # Docker镜像
├── scripts/                   # 启动脚本
│   ├── setup-conda-env.ps1       # 设置Conda环境
│   ├── dev-start-all.ps1         # 启动所有服务
│   ├── dev-start-backend.ps1     # 启动后端
│   ├── dev-start-celery.ps1      # 启动Celery
│   ├── dev-start-frontend.ps1    # 启动前端
│   └── dev-stop-all.ps1          # 停止所有服务
├── docker-compose.dev.yml     # 开发环境Docker配置
├── docker-compose.prod.yml    # 生产环境Docker配置
└── README.md
```

## 🛠️ 技术栈

### 后端
- Python 3.12
- FastAPI
- SQLAlchemy
- PostgreSQL
- Redis
- Celery

### 前端
- Vue.js 3
- TypeScript
- Element Plus
- Vite
- Pinia

### 部署
- Docker
- Docker Compose
- Nginx

## 📝 开发指南

### 后端开发

```powershell
# 激活Conda环境
conda activate hospital-backend

# 进入后端目录
cd backend

# 运行开发服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 前端开发

```powershell
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 运行开发服务器
npm run dev

# 构建生产版本
npm run build
```

### 数据库迁移

```powershell
# 激活Conda环境
conda activate hospital-backend

# 进入后端目录
cd backend

# 创建迁移
alembic revision --autogenerate -m "描述"

# 执行迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1
```

## 🐛 故障排查

### Docker Desktop无法启动

```powershell
# 更新WSL2
wsl --update
wsl --set-default-version 2

# 重启Docker Desktop
```

### 端口被占用

```powershell
# 查看端口占用
netstat -ano | findstr :5432

# 结束进程
taskkill /PID <PID> /F
```

### Celery在Windows上无法启动

使用 `--pool=solo` 参数：
```powershell
celery -A app.celery_app worker --loglevel=info --pool=solo
```

## 📄 许可证

本项目仅供内部使用。

## 👥 贡献者

- 开发团队

## 📞 联系方式

如有问题，请联系项目负责人。
