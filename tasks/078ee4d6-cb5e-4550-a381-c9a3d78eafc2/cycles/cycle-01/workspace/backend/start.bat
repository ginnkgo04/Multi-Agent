@echo off
REM 论坛平台后端启动脚本（Windows）

echo === Forum Platform Backend ===

REM 检查Python环境
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: Python 未安装
    pause
    exit /b 1
)

REM 检查虚拟环境
if not exist "venv" (
    echo 创建虚拟环境...
    python -m venv venv
)

REM 激活虚拟环境
echo 激活虚拟环境...
call venv\Scripts\activate.bat

REM 安装依赖
echo 安装依赖...
pip install --upgrade pip
pip install -r requirements.txt

REM 检查环境变量
if not exist ".env" (
    echo 创建环境变量文件...
    copy .env.example .env
    echo 请编辑 .env 文件配置数据库连接
)

REM 检查数据库迁移
if not exist "alembic\versions" (
    echo 初始化数据库迁移...
    alembic init alembic
    alembic revision --autogenerate -m "Initial migration"
    alembic upgrade head
) else (
    echo 应用数据库迁移...
    alembic upgrade head
)

REM 启动服务
echo 启动服务...
echo API文档: http://localhost:8000/docs
echo 按 Ctrl+C 停止服务

uvicorn main:app --reload --host 0.0.0.0 --port 8000

pause