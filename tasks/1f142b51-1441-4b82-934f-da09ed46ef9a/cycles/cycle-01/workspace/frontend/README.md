# 小熊猫介绍网站

一个响应式、现代化的单页网站，专门介绍小熊猫（红熊猫）的生态、习性和保护现状。

## 功能特点

### 🎨 设计亮点
- **响应式设计**: 完美适配移动端和桌面端
- **现代化UI**: 使用Tailwind CSS构建的现代化界面
- **交互体验**: 图片画廊、趣味知识卡片等交互元素
- **可访问性**: 符合WCAG标准的无障碍设计

### 📱 核心功能
1. **小熊猫介绍**: 详细的小熊猫基本信息
2. **特征展示**: 栖息地、饮食、分布、保护状态
3. **图片画廊**: 高质量小熊猫图片展示
4. **趣味知识**: 有趣的小熊猫事实和知识
5. **保护信息**: 保护现状和措施
6. **响应式布局**: 自适应各种屏幕尺寸

## 技术栈

- **Next.js 14**: React框架，支持App Router
- **TypeScript**: 类型安全的JavaScript
- **Tailwind CSS**: 实用优先的CSS框架
- **Lucide React**: 精美的图标库
- **ESLint**: 代码质量检查
- **PostCSS**: CSS处理工具

## 快速开始

### 环境要求
- Node.js 18.17 或更高版本
- npm 或 yarn 包管理器

### 安装步骤

1. **克隆项目**
```bash
git clone <repository-url>
cd workspace/frontend
```

2. **安装依赖**
```bash
npm install
# 或
yarn install
```

3. **开发环境运行**
```bash
npm run dev
# 或
yarn dev
```

4. **构建生产版本**
```bash
npm run build
npm start
# 或
yarn build
yarn start
```

## 项目结构

```
workspace/frontend/
├── app/                    # Next.js App Router
│   ├── layout.tsx         # 根布局组件
│   ├── page.tsx          # 主页面组件
│   └── globals.css       # 全局样式
├── components/            # React组件
│   └── FeatureExperience.tsx  # 交互功能组件
├── lib/                   # 工具函数和配置
│   └── api.ts            # API工具和数据
├── public/               # 静态资源
├── tailwind.config.ts    # Tailwind配置
├── next.config.js       # Next.js配置
├── tsconfig.json        # TypeScript配置
└── package.json         # 项目配置
```

## 开发指南

### 添加新组件
1. 在 `components/` 目录下创建新的 `.tsx` 文件
2. 导出React组件
3. 在需要的地方导入使用

### 样式开发
- 使用Tailwind CSS类名
- 自定义样式添加到 `globals.css`
- 主题配置在 `tailwind.config.ts`

### 数据管理
- 静态数据定义在 `lib/api.ts`
- 类型定义使用TypeScript接口
- 模拟API调用支持异步数据

## 部署

### Vercel部署（推荐）
1. 将代码推送到GitHub仓库
2. 在Vercel中导入项目
3. 自动部署完成

### 手动部署
```bash
# 构建项目
npm run build

# 输出到out目录
npm run export

# 部署到静态服务器
# 将out目录内容上传到服务器
```

## 性能优化

### 图片优化
- 使用Next.js Image组件
- 自动WebP格式转换
- 响应式图片加载

### 代码分割
- Next.js自动代码分割
- 动态导入支持
- 按需加载组件

### 缓存策略
- 静态资源长期缓存
- 浏览器缓存优化
- CDN加速支持

## 可访问性

### 键盘导航
- 所有交互元素支持键盘访问
- 焦点管理正确实现
- 跳过导航链接

### 屏幕阅读器
- 语义化HTML结构
- ARIA属性支持
- 适当的alt文本

### 颜色对比度
- 满足WCAG AA标准
- 高对比度模式支持
- 颜色盲友好设计

## 浏览器支持

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 许可证

本项目采用MIT许可证。详见 [LICENSE](LICENSE) 文件。

## 联系方式

如有问题或建议，请通过以下方式联系：

- 项目仓库: [GitHub Repository]
- 问题反馈: [Issues Page]
- 电子邮件: contact@redpanda.org

## 致谢

- 图片提供: Unsplash
- 图标提供: Lucide React
- 数据参考: IUCN Red List, WWF, Red Panda Network

---

**保护小熊猫，保护生物多样性！** 🐾