#!/bin/bash

# 论坛平台后端启动脚本

# 设置颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Forum Platform Backend ===${NC}"

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}错误: Python3 未安装${NC}"
    exit 1
fi

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}创建虚拟环境...${NC}"
    python3 -m venv venv
fi

# 激活虚拟环境
echo -e "${YELLOW}激活虚拟环境...${NC}"
source venv/bin/activate

# 安装依赖
echo -e "${YELLOW}安装依赖...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

# 检查环境变量
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}创建环境变量文件...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}请编辑 .env 文件配置数据库连接${NC}"
fi

# 检查数据库迁移
if [ ! -d "alembic/versions" ]; then
    echo -e "${YELLOW}初始化数据库迁移...${NC}"
    alembic init alembic
    alembic revision --autogenerate -m "Initial migration"
    alembic upgrade head
else
    echo -e "${YELLOW}应用数据库迁移...${NC}"
    alembic upgrade head
fi

# 启动服务
echo -e "${GREEN}启动服务...${NC}"
echo -e "${YELLOW}API文档: http://localhost:8000/docs${NC}"
echo -e "${YELLOW}按 Ctrl+C 停止服务${NC}"

uvicorn main:app --reload --host 0.0.0.0 --port 8000