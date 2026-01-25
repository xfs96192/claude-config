# 投资经理记事本应用 - 实现计划

## 项目概述

创建一个内网可用的投资产品管理记事本应用，支持多产品管理、交易日志记录、待办事项和富文本笔记，提供类似 OneNote 的分级组织结构。

## 用户需求总结

- **界面风格**: 经典编辑器风格（类 Evernote/OneNote），熟悉易用
- **产品规模**: 10-50 个产品，需要分组/标签管理系统
- **交易日志**:
  - 基础字段：交易时间、品种、方向、价格、数量
  - 分析内容：交易逻辑、市场分析、决策依据（富文本）
  - 附件支持：截图、文档上传
  - **核心需求**: 不同类型产品的固定模板，方便每天快速更新交易情况
- **核心功能**:
  - 富文本编辑（格式、表格、列表）
  - 分级笔记本/分区/页面结构
  - 快速搜索和标签
  - 手绘/图表插入

## 设计方向

### 美学定位：**Financial Editor Elegance**

融合经典编辑器的专业性与金融应用的精确性，创造一个优雅、高效的工作环境。

**核心理念**：
- 信息架构清晰，层级分明
- 专业而温暖的配色（避免冷冰冰）
- 快速操作，键盘友好
- 数据优先，视觉辅助

**设计元素**：
- **Typography**:
  - 标题/界面: "Spectral" (优雅衬线字体，传达专业与权威)
  - 正文: "Source Sans Pro" (清晰易读，数字识别性好)
  - 代码/数字: "JetBrains Mono" (等宽，适合交易数据)

- **Color Palette**:
  - 主背景: #f8f9fa (温暖的浅灰白)
  - 次级背景: #ffffff (纯白内容区)
  - 主色调: #2d5a7b (深蓝，专业稳重)
  - 强调色: #c97d60 (暖橙棕，标记重点)
  - 成功: #4a7c59 (森林绿)
  - 警告: #d4a373 (金棕)
  - 文字: #1a1a1a (深灰黑)
  - 次级文字: #6b7280 (中灰)

- **Layout**:
  - 三栏经典布局：笔记本导航 | 页面列表 | 编辑区 + 侧边栏
  - 可折叠面板，最大化编辑空间
  - 固定顶部工具栏，快速访问功能

- **Visual Details**:
  - 微妙的纸张纹理背景
  - 柔和的阴影和圆角（4-8px）
  - 平滑的过渡动画（200-300ms）
  - 悬停状态的细腻反馈

## 技术架构

### 技术栈选择

**纯前端实现，无需后端服务器**

- **框架**: Vanilla JavaScript + HTML5 + CSS3
  - 原因：内网环境，简单部署，无需构建工具
  - 单文件 HTML 打包所有资源，双击即可使用

- **富文本编辑器**: Quill.js
  - 原因：轻量、功能完整、可扩展性好
  - 支持 Delta 格式，便于存储和版本控制

- **存储方案**: IndexedDB + LocalStorage
  - IndexedDB：存储笔记内容、附件（Base64）
  - LocalStorage：存储用户配置、界面状态

- **图表/手绘**:
  - Chart.js：简单图表绘制
  - Canvas API：手绘功能

- **文件处理**:
  - FileReader API：读取上传文件
  - Base64 编码：存储图片/小文件

- **搜索**:
  - 客户端全文搜索（字符串匹配）
  - 可选：Fuse.js（模糊搜索）

### 数据结构设计

```javascript
// Notebook (笔记本) - 最顶层
{
  id: 'notebook-uuid',
  name: '权益组合',
  type: 'product-group', // product-group | general
  icon: '📊',
  color: '#2d5a7b',
  createdAt: timestamp,
  updatedAt: timestamp,
  sortOrder: 0
}

// Section (分区) - 中间层
{
  id: 'section-uuid',
  notebookId: 'notebook-uuid',
  name: '2024年Q1',
  icon: '📅',
  createdAt: timestamp,
  updatedAt: timestamp,
  sortOrder: 0
}

// Page (页面) - 内容层
{
  id: 'page-uuid',
  sectionId: 'section-uuid',
  title: '沪深300ETF - 2024-01-20',
  type: 'trade-log | note | todo | template',
  tags: ['权益', '指数', '交易'],
  content: QuillDelta, // 富文本内容
  metadata: {
    productName: '沪深300ETF',
    productCode: '510300',
    templateId: 'template-uuid' // 如果基于模板创建
  },
  createdAt: timestamp,
  updatedAt: timestamp,
  isPinned: false,
  sortOrder: 0
}

// Template (模板) - 用于快速创建交易日志
{
  id: 'template-uuid',
  name: '股票交易日志模板',
  productType: 'stock | bond | fund | future | option',
  content: QuillDelta, // 预设结构
  fields: [
    { name: 'tradingDate', label: '交易日期', type: 'date', required: true },
    { name: 'productCode', label: '品种代码', type: 'text', required: true },
    { name: 'direction', label: '方向', type: 'select', options: ['买入', '卖出'], required: true },
    { name: 'price', label: '价格', type: 'number', required: true },
    { name: 'quantity', label: '数量', type: 'number', required: true },
    { name: 'analysis', label: '市场分析', type: 'richtext', required: false },
    { name: 'logic', label: '交易逻辑', type: 'richtext', required: false }
  ],
  createdAt: timestamp,
  updatedAt: timestamp
}

// Attachment (附件)
{
  id: 'attachment-uuid',
  pageId: 'page-uuid',
  name: '持仓截图.png',
  type: 'image/png',
  size: 102400,
  data: 'base64-encoded-data', // 小文件直接存储
  createdAt: timestamp
}

// Todo (待办事项)
{
  id: 'todo-uuid',
  pageId: 'page-uuid', // 可关联到特定页面，或独立存在
  content: '跟进XXX产品赎回',
  completed: false,
  priority: 'high | medium | low',
  dueDate: timestamp,
  tags: ['权益组'],
  createdAt: timestamp,
  updatedAt: timestamp
}
```

### IndexedDB Schema

```javascript
// Database: 'InvestmentNotebook'
// Version: 1

ObjectStore: 'notebooks'
  - keyPath: 'id'
  - indexes: ['createdAt', 'updatedAt', 'sortOrder']

ObjectStore: 'sections'
  - keyPath: 'id'
  - indexes: ['notebookId', 'createdAt', 'sortOrder']

ObjectStore: 'pages'
  - keyPath: 'id'
  - indexes: ['sectionId', 'type', 'createdAt', 'updatedAt', 'tags']

ObjectStore: 'templates'
  - keyPath: 'id'
  - indexes: ['productType', 'createdAt']

ObjectStore: 'attachments'
  - keyPath: 'id'
  - indexes: ['pageId', 'createdAt']

ObjectStore: 'todos'
  - keyPath: 'id'
  - indexes: ['pageId', 'completed', 'dueDate', 'priority']
```

## 功能模块设计

### 1. 核心布局 (Layout)

**三栏布局 + 可折叠侧边栏**

```
┌─────────────────────────────────────────────────────────────────┐
│  顶部工具栏 (Top Toolbar)                                         │
│  [搜索] [新建] [模板] [待办] [设置] [导出]                         │
├──────────┬────────────┬────────────────────────────┬─────────────┤
│          │            │                            │             │
│ 笔记本   │  页面列表  │      编辑器区域             │   侧边栏    │
│ 导航区   │  (Pages)   │      (Editor)              │   (Panel)   │
│          │            │                            │             │
│ 📚权益组 │ 📄 沪深...│  ┌──────────────────────┐  │ 📋 页面信息 │
│  └Q1交易 │ 📄 科创...│  │ # 交易日志 2024-01-20│  │ ⏰ 创建时间 │
│  └Q2交易 │ 📄 红利...│  │                      │  │ 🏷️ 标签     │
│          │            │  │ **品种**: 沪深300ETF │  │             │
│ 📚债券组 │ [+新建页面]│  │ **方向**: 买入        │  │ 📎 附件 (3) │
│  └利率债 │            │  │ **价格**: 3.580      │  │             │
│  └信用债 │ 🔍 搜索..  │  │                      │  │ ✅ 待办事项 │
│          │            │  │ ## 市场分析          │  │  □ 更新报告 │
│ [+笔记本]│  筛选:     │  │ 今日市场...          │  │  ☑ 提交申购 │
│          │  [全部▼]   │  │                      │  │             │
│ [折叠]   │            │  └──────────────────────┘  │ [折叠]      │
└──────────┴────────────┴────────────────────────────┴─────────────┘
│  状态栏: 最后保存于 14:32 | 选中: 1 项 | 共 128 页               │
└─────────────────────────────────────────────────────────────────┘
```

**关键特性**:
- 左侧笔记本导航可折叠（展开/收起图标）
- 页面列表支持搜索、筛选（按标签、类型、日期）
- 右侧面板可切换：页面信息 | 待办事项 | 附件列表
- 所有面板状态保存到 LocalStorage

### 2. 笔记本/分区/页面管理

**笔记本导航区 (左侧栏)**

功能：
- 树形结构显示：笔记本 → 分区 → 页面（前3级）
- 右键菜单：新建、重命名、删除、移动、设置颜色/图标
- 拖拽排序和移动
- 展开/收起状态持久化

交互：
- 单击：选中并显示该层级下的页面列表
- 双击：重命名
- 拖拽：调整顺序或移动到其他笔记本

**页面列表区 (中间栏)**

功能：
- 显示当前选中分区/笔记本下的所有页面
- 列表项显示：标题、最后编辑时间、标签、图标（固定/模板）
- 顶部搜索框：实时过滤
- 筛选器：按类型（交易日志/笔记/待办）、标签、日期范围
- 排序：按创建时间、修改时间、标题字母

交互：
- 单击页面：加载到编辑器
- 右键菜单：复制、移动、删除、固定、导出
- 星标/固定功能：重要页面置顶

### 3. 富文本编辑器 (Quill.js)

**工具栏配置**:

```javascript
const toolbarOptions = [
  // 文本格式
  [{ 'header': [1, 2, 3, 4, 5, 6, false] }],
  ['bold', 'italic', 'underline', 'strike'],
  [{ 'color': [] }, { 'background': [] }],

  // 列表和对齐
  [{ 'list': 'ordered'}, { 'list': 'bullet' }, { 'list': 'check' }],
  [{ 'indent': '-1'}, { 'indent': '+1' }],
  [{ 'align': [] }],

  // 插入元素
  ['link', 'image', 'video'],
  ['blockquote', 'code-block'],

  // 表格（自定义模块）
  ['table'],

  // 自定义：交易数据快速插入
  ['trade-template'],

  // 清除格式
  ['clean']
];
```

**自定义功能**:
1. **交易数据模板插入**:
   - 快速插入预设表格（品种、方向、价格、数量）
   - 按钮点击弹出表单，填写后自动生成格式化内容

2. **表格增强**:
   - 合并单元格
   - 列宽调整
   - 表格样式（边框、背景色）

3. **附件插入**:
   - 图片：直接粘贴或上传，转 Base64 存储
   - 文件：显示为文件卡片，点击下载
   - 截图：支持 Ctrl+V 粘贴

4. **自动保存**:
   - 防抖 500ms，内容变化后自动保存
   - 状态栏显示"保存中..." → "已保存"

### 4. 模板系统

**模板管理器**

功能：
- 创建/编辑/删除模板
- 模板分类：按产品类型（股票、债券、基金、期货、期权等）
- 模板预览
- 基于模板快速创建页面

**模板结构**:
- 预定义字段（结构化数据）
- 富文本区域（自由编辑）
- 字段类型：文本、数字、日期、下拉选择、富文本

**使用流程**:
1. 点击"从模板新建"按钮
2. 选择模板类型
3. 弹出表单，填写结构化字段
4. 自动生成页面，包含：
   - 标题：自动根据字段生成（如"沪深300ETF - 2024-01-20"）
   - 内容：模板预设结构 + 填写的数据
   - 标签：自动添加产品类型标签

**示例模板：股票交易日志**

```markdown
# 交易日志 - {productName} - {tradingDate}

## 基本信息
- **品种代码**: {productCode}
- **交易方向**: {direction}
- **成交价格**: {price}
- **成交数量**: {quantity}
- **成交金额**: {price * quantity} (自动计算)

## 市场分析
{richtext: analysis}

## 交易逻辑
{richtext: logic}

## 风险提示
{richtext: risks}

## 附件
{attachments}
```

### 5. 待办事项 (Todo)

**待办列表视图**:
- 右侧面板可切换到"待办事项"标签
- 显示所有待办 + 关联的页面
- 按状态分组：进行中 / 已完成
- 按优先级排序：高 → 中 → 低

**功能**:
- 快速添加：输入框 + 回车
- 设置优先级、截止日期
- 关联到页面（可选）
- 批量操作：标记完成、删除
- 过期提醒（红色高亮）

**页面内嵌待办**:
- 在编辑器内使用 Checklist 格式
- 自动同步到全局待办列表

### 6. 搜索功能

**全局搜索**:
- 顶部工具栏搜索框
- 快捷键：Ctrl+F / Cmd+F
- 搜索范围：标题、内容、标签
- 实时高亮匹配结果

**搜索结果显示**:
- 侧边栏展开搜索结果面板
- 显示匹配的页面列表
- 预览匹配上下文（前后 50 字符）
- 点击跳转到页面并高亮关键词

**高级筛选**:
- 按笔记本/分区过滤
- 按日期范围
- 按标签
- 按页面类型

### 7. 导出功能

**支持格式**:
- **JSON**: 完整数据导出（包含附件 Base64）
- **Markdown**: 纯文本格式，图片转为链接
- **HTML**: 带样式的网页格式
- **PDF**: 打印友好格式（可选）

**导出范围**:
- 单个页面
- 整个分区
- 整个笔记本
- 全部数据

**实现方式**:
- JSON：直接从 IndexedDB 读取
- Markdown：Quill Delta → Markdown 转换
- HTML：Quill 自带 getHTML() + 样式包装
- PDF：使用浏览器打印功能（window.print）

### 8. 图表和手绘

**图表插入**:
- 使用 Chart.js 创建简单图表
- 支持类型：折线图、柱状图、饼图
- 数据输入：表格形式
- 图表配置：颜色、标签、标题

**手绘功能**:
- Canvas 画板
- 工具：画笔、橡皮、形状（矩形、圆形、箭头）
- 颜色选择
- 导出为图片嵌入笔记

**实现优先级**:
- MVP 阶段：图片上传 + 简单表格
- 增强阶段：Chart.js 图表
- 可选功能：手绘画板

## 文件结构

```
investment-notebook/
├── index.html                 # 主文件（单文件应用）
├── README.md                  # 使用说明
└── assets/                    # 可选：独立资源文件（如果不打包）
    ├── css/
    │   └── styles.css
    ├── js/
    │   ├── app.js             # 主应用逻辑
    │   ├── db.js              # IndexedDB 操作
    │   ├── editor.js          # 编辑器封装
    │   ├── template.js        # 模板系统
    │   ├── search.js          # 搜索功能
    │   └── export.js          # 导出功能
    └── libs/
        ├── quill.min.js
        ├── quill.snow.css
        └── chart.min.js
```

**单文件打包方案** (推荐内网使用):
- 将所有 CSS、JS、字体、图标内联到 index.html
- 使用 Data URI 嵌入外部资源
- 最终生成一个自包含的 HTML 文件
- 双击打开即可使用，无需服务器

## 实现步骤

### Phase 1: 核心框架 (1-2天)

1. **HTML 结构搭建**
   - 三栏布局 HTML 骨架
   - 顶部工具栏
   - 模态框组件（新建、设置等）

2. **CSS 样式系统**
   - CSS 变量定义（颜色、字体、间距）
   - 响应式布局（Grid + Flexbox）
   - 经典编辑器美学实现
   - 微妙动画和过渡效果

3. **IndexedDB 初始化**
   - 数据库连接和版本管理
   - ObjectStore 创建
   - CRUD 操作封装

4. **基础导航功能**
   - 笔记本/分区树形结构渲染
   - 页面列表渲染
   - 点击切换逻辑

### Phase 2: 编辑器集成 (1天)

1. **Quill.js 集成**
   - 初始化编辑器
   - 工具栏配置
   - 自定义主题匹配整体设计

2. **页面 CRUD**
   - 新建页面
   - 编辑和保存
   - 删除和移动

3. **自动保存**
   - 防抖机制
   - 状态反馈

### Phase 3: 模板系统 (1天)

1. **模板管理器 UI**
   - 模板列表
   - 创建/编辑模板

2. **字段定义系统**
   - 动态表单生成
   - 字段类型渲染

3. **基于模板创建页面**
   - 表单填写
   - 内容生成逻辑

### Phase 4: 附件和富功能 (1天)

1. **附件上传**
   - 图片上传和预览
   - 文件 Base64 编码存储
   - 附件列表管理

2. **粘贴图片支持**
   - 监听 paste 事件
   - 自动插入编辑器

3. **表格增强**
   - Quill 表格模块配置
   - 基础表格操作

### Phase 5: 待办和搜索 (1天)

1. **待办事项**
   - 待办列表 UI
   - CRUD 操作
   - 关联页面逻辑

2. **搜索功能**
   - 全文搜索实现
   - 结果高亮
   - 筛选器

### Phase 6: 导出和优化 (1天)

1. **导出功能**
   - JSON 导出
   - Markdown 转换
   - HTML 导出

2. **性能优化**
   - 虚拟滚动（如果页面数量大）
   - 图片懒加载
   - IndexedDB 查询优化

3. **用户体验优化**
   - 快捷键支持
   - 加载动画
   - 错误处理和提示

### Phase 7: 打包和部署 (0.5天)

1. **单文件打包**
   - 内联所有资源
   - 压缩 CSS/JS
   - 测试离线可用性

2. **文档编写**
   - README 使用说明
   - 快捷键列表
   - 常见问题

## 关键文件清单

需要创建的主要文件：

1. **index.html** - 主应用入口和 HTML 结构
2. **styles.css** - 完整样式系统
3. **app.js** - 应用主逻辑和状态管理
4. **db.js** - IndexedDB 数据库操作封装
5. **editor.js** - Quill 编辑器封装和扩展
6. **template.js** - 模板系统逻辑
7. **search.js** - 搜索和筛选功能
8. **export.js** - 数据导出功能
9. **utils.js** - 工具函数（UUID生成、日期格式化等）

## 验证计划

### 功能测试

1. **基础操作**
   - [ ] 创建笔记本/分区/页面
   - [ ] 重命名和删除
   - [ ] 拖拽排序

2. **编辑器**
   - [ ] 富文本格式（粗体、斜体、颜色等）
   - [ ] 列表和表格
   - [ ] 图片粘贴和上传
   - [ ] 自动保存

3. **模板功能**
   - [ ] 创建交易日志模板
   - [ ] 基于模板新建页面
   - [ ] 字段自动填充和计算

4. **附件**
   - [ ] 上传图片和文件
   - [ ] 附件列表显示
   - [ ] 附件下载

5. **待办事项**
   - [ ] 添加待办
   - [ ] 标记完成
   - [ ] 关联页面

6. **搜索**
   - [ ] 全文搜索
   - [ ] 标签筛选
   - [ ] 结果高亮

7. **导出**
   - [ ] JSON 导出和导入
   - [ ] Markdown 导出
   - [ ] 单页面导出

### 数据持久化测试

1. **数据存储**
   - [ ] 刷新页面数据不丢失
   - [ ] IndexedDB 正确保存
   - [ ] 大量数据（100+ 页面）性能

2. **离线可用性**
   - [ ] 断网状态下正常使用
   - [ ] 单文件 HTML 独立运行

### 浏览器兼容性测试

- [ ] Chrome/Edge (主要)
- [ ] Firefox
- [ ] Safari (如果用 macOS)

### 性能测试

- [ ] 页面加载时间 < 2s
- [ ] 搜索响应 < 500ms
- [ ] 编辑器输入无延迟
- [ ] 大图片上传和显示流畅

## 后续增强方向 (MVP 后可选)

1. **数据同步**
   - 导出/导入 JSON 实现跨设备同步
   - 文件存储到网络共享盘

2. **高级图表**
   - 集成 Chart.js 完整功能
   - 盈亏曲线绘制

3. **手绘功能**
   - Canvas 画板
   - 批注和标记

4. **版本历史**
   - 保存页面修改历史
   - 版本对比和恢复

5. **协作功能** (如果有局域网服务器)
   - 多人编辑
   - 评论系统

6. **移动端适配**
   - 响应式设计
   - 触摸操作优化

## 预估工作量

**MVP 版本**: 约 5-7 天
- 核心功能完整
- 可用性高
- 美观专业

**完整版本**: 约 10-12 天
- 所有功能实现
- 性能优化
- 完善文档

## 总结

本计划设计了一个功能完整、美观专业的投资经理记事本应用，核心特性包括：

✅ 经典编辑器风格，熟悉易用
✅ 分级组织结构（笔记本/分区/页面）
✅ 富文本编辑器（Quill.js）
✅ 交易日志模板系统（核心需求）
✅ 附件上传和管理
✅ 待办事项集成
✅ 全文搜索和筛选
✅ 数据导出（JSON/Markdown/HTML）
✅ 完全离线可用（IndexedDB）
✅ 单文件部署，内网友好

设计美学融合了经典编辑器的专业性与金融应用的精确性，使用温暖的配色和优雅的字体，创造高效舒适的工作环境。
