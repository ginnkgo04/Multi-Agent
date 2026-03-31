# Forum Platform Backend API

基于FastAPI的论坛平台后端API，提供完整的用户认证、分类管理、主题讨论、帖子回复和投票系统。

## 功能特性

- 🔐 **JWT认证**：安全的用户注册、登录和令牌管理
- 📁 **分类管理**：多级分类系统，支持版主管理
- 💬 **主题讨论**：完整的主题创建、编辑、删除功能
- 💬 **帖子回复**：支持嵌套回复的讨论系统
- 👍 **投票系统**：对主题和帖子进行赞/踩投票
- 👥 **用户管理**：用户资料、权限管理和版主系统
- 📊 **分页搜索**：支持分页、过滤和全文搜索
- 🔒 **权限控制**：基于角色的细粒度权限管理

## 技术栈

- **FastAPI** - 高性能Python Web框架
- **SQLAlchemy** - Python SQL工具包和ORM
- **PostgreSQL** - 关系型数据库
- **Alembic** - 数据库迁移工具
- **JWT** - JSON Web Tokens认证
- **Pydantic** - 数据验证和设置管理

## 快速开始

### 1. 环境设置

```bash
# 克隆项目
git clone <repository-url>
cd workspace/backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 数据库配置

```bash
# 创建PostgreSQL数据库
createdb forum_db

# 配置环境变量（或编辑.env文件）
cp .env.example .env
# 编辑.env文件设置数据库连接
```

### 3. 数据库迁移

```bash
# 初始化Alembic
alembic init alembic

# 创建初始迁移
alembic revision --autogenerate -m "Initial migration"

# 应用迁移
alembic upgrade head
```

### 4. 启动服务

```bash
# 开发模式（自动重载）
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 生产模式
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API文档

启动服务后访问：
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API端点

### 认证 (`/api/v1/auth`)
- `POST /register` - 用户注册
- `POST /login` - 用户登录
- `POST /refresh` - 刷新令牌
- `GET /me` - 获取当前用户信息
- `POST /logout` - 用户登出

### 用户 (`/api/v1/users`)
- `GET /` - 获取用户列表（管理员）
- `GET /{user_id}` - 获取用户信息
- `PUT /{user_id}` - 更新用户信息（管理员）
- `DELETE /{user_id}` - 删除用户（管理员）
- `GET /me` - 获取当前用户信息
- `PUT /me` - 更新当前用户信息

### 分类 (`/api/v1/categories`)
- `GET /` - 获取所有分类
- `GET /{category_id}` - 获取分类信息
- `GET /slug/{slug}` - 通过slug获取分类
- `POST /` - 创建分类（管理员）
- `PUT /{category_id}` - 更新分类（管理员）
- `DELETE /{category_id}` - 删除分类（管理员）
- `POST /{category_id}/moderators/{user_id}` - 添加版主（管理员）
- `DELETE /{category_id}/moderators/{user_id}` - 移除版主（管理员）

### 主题 (`/api/v1/threads`)
- `GET /` - 获取主题列表（支持过滤和搜索）
- `GET /{thread_id}` - 获取主题信息
- `GET /slug/{slug}` - 通过slug获取主题
- `POST /` - 创建主题
- `PUT /{thread_id}` - 更新主题
- `DELETE /{thread_id}` - 删除主题
- `POST /{thread_id}/pin` - 置顶主题（版主/管理员）
- `POST /{thread_id}/unpin` - 取消置顶（版主/管理员）
- `POST /{thread_id}/lock` - 锁定主题（版主/管理员）
- `POST /{thread_id}/unlock` - 解锁主题（版主/管理员）

### 帖子 (`/api/v1/posts`)
- `GET /thread/{thread_id}` - 获取主题下的帖子
- `GET /{post_id}` - 获取帖子信息
- `GET /user/{user_id}` - 获取用户的帖子
- `POST /` - 创建帖子
- `PUT /{post_id}` - 更新帖子
- `DELETE /{post_id}` - 删除帖子

### 投票 (`/api/v1/votes`)
- `POST /` - 创建投票
- `GET /thread/{thread_id}/user/{user_id}` - 获取用户对主题的投票
- `GET /post/{post_id}/user/{user_id}` - 获取用户对帖子的投票
- `GET /thread/{thread_id}/stats` - 获取主题投票统计
- `GET /post/{post_id}/stats` - 获取帖子投票统计
- `DELETE /thread/{thread_id}` - 删除主题投票
- `DELETE /post/{post_id}` - 删除帖子投票

## 数据模型

### User (用户)
- `id` - 主键
- `username` - 用户名（唯一）
- `email` - 邮箱（唯一）
- `hashed_password` - 密码哈希
- `display_name` - 显示名称
- `bio` - 个人简介
- `avatar_url` - 头像URL
- `is_active` - 是否活跃
- `is_admin` - 是否管理员
- `created_at` - 创建时间
- `updated_at` - 更新时间

### Category (分类)
- `id` - 主键
- `name` - 分类名称（唯一）
- `slug` - URL标识（唯一）
- `description` - 描述
- `color` - 颜色代码
- `icon` - 图标
- `is_active` - 是否活跃
- `order` - 排序顺序
- `created_at` - 创建时间

### Thread (主题)
- `id` - 主键
- `title` - 标题
- `slug` - URL标识
- `content` - 内容
- `is_pinned` - 是否置顶
- `is_locked` - 是否锁定
- `view_count` - 查看次数
- `reply_count` - 回复数量
- `last_post_at` - 最后回复时间
- `author_id` - 作者ID
- `category_id` - 分类ID
- `created_at` - 创建时间
- `updated_at` - 更新时间

### Post (帖子)
- `id` - 主键
- `content` - 内容
- `is_edited` - 是否编辑过
- `edit_reason` - 编辑原因
- `author_id` - 作者ID
- `thread_id` - 主题ID
- `parent_id` - 父帖子ID（用于嵌套回复）
- `created_at` - 创建时间
- `updated_at` - 更新时间

### Vote (投票)
- `id` - 主键
- `vote_type` - 投票类型（1:赞, -1:踩）
- `user_id` - 用户ID
- `thread_id` - 主题ID（可选）
- `post_id` - 帖子ID（可选）
- `created_at` - 创建时间

## 权限系统

### 用户角色
1. **普通用户**：可以创建主题、回复、投票
2. **版主**：可以管理指定分类的主题和帖子
3. **管理员**：可以管理所有内容，包括用户和分类

### 权限规则
- 用户可以编辑/删除自己的内容
- 版主可以管理自己分类的所有内容
- 管理员可以管理所有内容
- 锁定的主题不能添加新回复
- 只有版主/管理员可以置顶、锁定主题

## 开发指南

### 创建迁移
```bash
# 生成迁移脚本
alembic revision --autogenerate -m "描述信息"

# 应用迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1
```

### 运行测试
```bash
# 安装测试依赖
pip install pytest pytest-asyncio httpx

# 运行测试
pytest
```

### 代码风格
```bash
# 安装代码格式化工具
pip install black isort

# 格式化代码
black .
isort .
```

## 部署

### Docker部署
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 环境变量
```bash
# 数据库配置
DATABASE_URL=postgresql://user:password@host:port/dbname

# JWT配置
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS配置
BACKEND_CORS_ORIGINS=["http://localhost:3000"]
```

## 贡献指南

1. Fork项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

## 许可证

MIT License