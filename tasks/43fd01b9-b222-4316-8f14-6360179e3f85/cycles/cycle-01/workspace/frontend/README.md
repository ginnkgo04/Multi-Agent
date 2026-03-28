# 粉色小猪介绍网站 🐷

一个可爱、粉嫩的粉色小猪介绍网站，采用现代Web技术栈构建。

## 功能特点 ✨

### 核心功能
- 🎨 粉色主题设计系统
- 📱 完全响应式布局
- 🎯 平滑滚动导航
- 💫 可爱动画效果
- 🎵 交互式音效控制
- ❤️ 点赞收藏功能

### 内容板块
1. **首页介绍** - 粉色小猪的欢迎页面
2. **关于我** - 小猪的个性介绍
3. **特点展示** - 6个独特特征
4. **趣味知识** - 互动式小知识卡片
5. **生活相册** - 小猪的日常瞬间
6. **资源下载** - 壁纸、涂鸦等资源

## 技术栈 🛠️

- **框架**: Next.js 14 (App Router)
- **语言**: TypeScript
- **样式**: Tailwind CSS
- **图标**: Lucide React
- **部署**: Vercel (推荐)

## 快速开始 🚀

### 环境要求
- Node.js 18+ 
- npm 或 yarn

### 安装步骤
```bash
# 克隆项目
git clone <repository-url>
cd pink-pig-website

# 安装依赖
npm install
# 或
yarn install

# 启动开发服务器
npm run dev
# 或
yarn dev
```

### 构建生产版本
```bash
npm run build
npm start
```

## 项目结构 📁

```
workspace/frontend/
├── app/                    # Next.js App Router
│   ├── layout.tsx         # 根布局组件
│   ├── page.tsx          # 主页组件
│   └── globals.css       # 全局样式
├── components/            # 可复用组件
│   └── FeatureExperience.tsx # 特色体验组件
├── lib/                   # 工具函数
│   └── api.ts            # API 工具
├── public/               # 静态资源
└── config/              # 配置文件
```

## 设计系统 🎨

### 颜色方案
- 主色: `#f472b6` (粉色)
- 辅色: `#fb7185` (玫瑰色)
- 背景: `#fdf2f8` 到 `#fff1f2` 渐变
- 文字: `#831843` (深粉色)

### 字体
- 主要: Inter (系统字体)
- 备用: 系统默认无衬线字体

### 动画效果
- 浮动动画: 元素上下浮动
- 心跳动画: 点赞效果
- 缩放动画: 交互反馈
- 渐变过渡: 平滑状态变化

## 开发指南 💻

### 添加新组件
1. 在 `components/` 目录创建 `.tsx` 文件
2. 使用 TypeScript 接口定义 props
3. 遵循现有的设计模式
4. 添加必要的样式和动画

### 修改样式
1. 使用 Tailwind CSS 工具类
2. 自定义样式添加到 `globals.css`
3. 新增颜色到 `tailwind.config.js`
4. 保持设计一致性

### API 集成
1. 使用 `lib/api.ts` 中的服务类
2. 处理加载和错误状态
3. 实现适当的缓存策略
4. 添加类型定义

## 性能优化 ⚡

### 已实现优化
- 图片懒加载
- 代码分割
- CSS 压缩
- 字体子集化
- 缓存策略

### 建议优化
- 图片使用 WebP 格式
- 实现服务端渲染
- 添加 PWA 支持
- 使用 CDN 加速

## 浏览器支持 🌐

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## 部署指南 🚢

### Vercel 部署 (推荐)
1. 连接 GitHub 仓库
2. 导入项目
3. 自动部署配置
4. 设置环境变量

### 自定义部署
1. 构建项目: `npm run build`
2. 输出目录: `.next`
3. 配置服务器
4. 设置反向代理

## 贡献指南 🤝

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 发起 Pull Request
5. 通过代码审查

## 许可证 📄

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 联系方式 📧

如有问题或建议，请通过以下方式联系：

- 邮箱: hello@pinkpig.world
- 网站: https://pinkpig.vercel.app
- GitHub: @pinkpig-team

---

**让世界充满粉色小猪的可爱！** 🐷💕