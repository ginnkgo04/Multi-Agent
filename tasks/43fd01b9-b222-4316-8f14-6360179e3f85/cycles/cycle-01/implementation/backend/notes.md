# 粉粉猪网站后端实施说明

## 项目概述
为"粉色小猪介绍网页"项目构建的后端服务，使用FastAPI框架提供API接口和静态文件服务。

## 技术栈
- **框架**: FastAPI 0.104.1
- **服务器**: Uvicorn
- **数据验证**: Pydantic 2.5.0
- **静态文件**: FastAPI StaticFiles

## 项目结构
```
workspace/backend/
├── requirements.txt              # 项目依赖
├── app/
│   ├── main.py                  # 应用入口点
│   ├── schemas.py               # 数据模型定义
│   ├── services.py              # 业务逻辑服务
│   └── routes.py                # API路由定义
└── implementation/backend/notes.md  # 本说明文档
```

## 核心功能

### 1. 内容管理API
- `GET /api/content` - 获取完整的粉粉猪内容数据
- `PUT /api/content` - 更新网站内容
- `GET /api/characteristics` - 获取粉粉猪的特点
- `GET /api/fun-facts` - 获取有趣的猪知识
- `GET /api/random-fact` - 获取随机趣味知识

### 2. 静态文件服务
- `GET /static/{filename}` - 提供图片、CSS、JS等静态文件
- 自动创建static目录结构
- 支持常见文件类型：jpg, png, gif, svg, css, js, html

### 3. 健康检查
- `GET /api/health` - 服务健康状态检查

### 4. 主页服务
- `GET /` - 提供HTML格式的主页，展示网站信息和API文档

## 数据模型

### PigContent (主要内容模型)
- `name`: 粉粉猪的名字
- `tagline`: 标语/口号
- `description`: 详细描述
- `main_image_url`: 主图片URL
- `characteristics`: 特点列表
- `fun_facts`: 趣味知识列表
- `colors`: 颜色配置
- `social_links`: 社交媒体链接

### PigCharacteristic (特点模型)
- `title`: 特点标题
- `description`: 详细描述
- `icon`: 图标名称/URL

### FunFact (趣味知识模型)
- `fact`: 知识内容
- `category`: 分类
- `is_surprising`: 是否令人惊讶

## 默认内容
系统包含预设的粉粉猪内容：
- 名称: "粉粉猪"
- 标语: "世界上最可爱的小猪！"
- 4个特点: 超级可爱、活泼好动、爱吃美食、友好善良
- 5个趣味知识: 关于猪的智力、习性、能力等
- 粉色系颜色配置

## 运行方式

### 安装依赖
```bash
cd workspace/backend
pip install -r requirements.txt
```

### 启动服务
```bash
cd workspace/backend
python -m app.main
```

或直接运行：
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 访问地址
- 主页: http://localhost:8000
- API文档: http://localhost:8000/api/docs
- 内容API: http://localhost:8000/api/content

## 与前端集成

### 数据获取
前端可以通过以下方式获取数据：

1. **直接API调用**:
```javascript
fetch('/api/content')
  .then(response => response.json())
  .then(data => console.log(data));
```

2. **获取特定数据**:
```javascript
// 获取特点
fetch('/api/characteristics')

// 获取趣味知识
fetch('/api/fun-facts')

// 获取随机知识
fetch('/api/random-fact')
```

### 静态资源
- 图片放在 `static/images/` 目录
- CSS文件放在 `static/css/` 目录
- JS文件放在 `static/js/` 目录

访问方式：`/static/images/pink-pig-main.jpg`

## 扩展性

### 添加新内容类型
1. 在 `schemas.py` 中定义新的Pydantic模型
2. 在 `services.py` 的ContentService中添加相应方法
3. 在 `routes.py` 中添加新的API端点

### 添加数据库支持
当前使用JSON文件存储，可轻松替换为：
- SQLite (轻量级)
- PostgreSQL (生产环境)
- MongoDB (文档存储)

### 添加用户认证
如需内容管理后台，可添加：
- JWT认证
- 用户角色管理
- 内容审核流程

## 注意事项

1. **CORS配置**: 当前允许所有来源，生产环境应限制为前端域名
2. **文件上传**: 当前版本未实现文件上传，可通过扩展 `/api/upload` 端点添加
3. **内容缓存**: 考虑添加Redis缓存提高性能
4. **安全性**: 生产环境应添加速率限制、输入验证等安全措施

## 与前端设计协调
后端已准备好支持前端设计需求：
- 提供完整的颜色配置数据
- 支持响应式图片URL
- 提供结构化内容便于前端组件化
- 支持交互式功能（如随机事实展示）

## 下一步工作
1. 等待前端设计完成，协调API调用方式
2. 根据实际图片资源调整图片URL
3. 添加内容管理后台（如果需要）
4. 部署配置和性能优化