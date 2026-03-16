# DevUI Pencil 设计 — 详细参考

## 1. MCP 工具速查

### 1.1 读取与发现（Pencil MCP）

| 工具 | 用途 | 关键参数 |
|------|------|----------|
| `get_editor_state` | 当前编辑器状态、选中节点、组件列表 | `include_schema` |
| `batch_get` | 搜索/读取节点 | `patterns`, `nodeIds`, `readDepth`, `resolveInstances` |
| `snapshot_layout` | 查看布局结构 | `parentId`, `maxDepth` |
| `get_screenshot` | 截图验证 | `nodeId` |
| `get_variables` | 获取变量和主题 | `filePath` |
| `set_variables` | 设置变量 | `filePath`, `variables` |
| `get_guidelines` | 获取设计指南 | `topic` (design-system/web-app/code/table/tailwind/landing-page/slides/mobile-app) |
| `find_empty_space_on_canvas` | 找空白画布区域 | `width`, `height`, `direction` |

### 1.2 设计操作（batch_design）

| 操作 | 语法 | 说明 |
|------|------|------|
| 插入 | `foo=I(parent, {...})` | 创建新节点 |
| 复制 | `bar=C(nodeId, parent, {...})` | 复制节点（复制 reusable 节点 = 创建 ref 实例） |
| 更新 | `U(path, {...})` | 修改节点属性（不可改 children、id、type、ref） |
| 替换 | `baz=R(path, {...})` | 替换整个节点 |
| 移动 | `M(nodeId, parent, index)` | 移动节点 |
| 删除 | `D(nodeId)` | 删除节点 |
| 图片 | `G(nodeId, "stock"/"ai", prompt)` | 生成/获取图片填充 |

**每次调用最多 25 个操作**。每个 I/C/R 操作必须有绑定名。`document` 是预定义绑定，仅用于插入顶层 frame。

### 1.3 文件重载（pen-component-copy MCP）

| 工具 | 用途 | 参数 |
|------|------|------|
| `reloadfile` | 关闭并重新打开文件，从磁盘重读 | `file_path` (绝对路径) |
| `reload_pencil` | 重载编辑器窗口（重启 Pencil） | 无 |

---

## 2. Import 机制详解

### .pen 文件的 imports 字段

```json
{
  "version": "...",
  "imports": {
    "devui": "designsystem/devUI/components/devUI2.pen"
  },
  "variables": {...},
  "children": [...]
}
```

- `imports` 在文档顶层 JSON 对象中
- key 是别名（如 `devui`），value 是从当前 .pen 文件到被导入文件的**相对路径**
- 导入后，ref 格式为 `devui:组件ID`（如 `devui:RoYUx`）
- 更新实例内子节点时，path 为 `实例ID/devui:子节点ID`

### 添加 import 流程

1. 确定相对路径（从设计文件到 `devUI2.pen`）
2. 用 Shell/StrReplace 在 .pen 文件顶层 JSON 中添加 imports
3. 调用 `reloadfile` 重新加载
4. 用 `get_editor_state` 验证 Reusable Components 中出现 `devui:xxx`

---

## 3. devUI2.pen Design Token 变量

### 3.1 颜色

| 变量名 | 值 | 用途 |
|--------|-----|------|
| `$devui-brand` | #5e7ce0 | 品牌主色、主按钮、选中态 |
| `$devui-brand-foil` | #f2f5fc | 品牌辅助底色（hover/选中底色） |
| `$devui-brand-hover` | #7693f5 | 品牌色 hover |
| `$devui-brand-active` | #526ecc | 品牌色 active |
| `$devui-text` | #252b3a | 主要文字 |
| `$devui-text-weak` | #575d6c | 弱化文字 |
| `$devui-aide-text` | #8a8e99 | 辅助文字（占位符） |
| `$devui-light-text` | #ffffff | 深色背景文字 |
| `$devui-link` | #5e7ce0 | 链接文字 |
| `$devui-base-bg` | #ffffff | 基础白色背景 |
| `$devui-global-bg` | #f5f5f5 | 全局灰底背景 |
| `$devui-line` | #adb0b8 | 边框分割线 |
| `$devui-dividing-line` | #dfe1e6 | 内容分割线 |
| `$devui-success` | #50d4ab | 成功 |
| `$devui-danger` | #f66f6a | 错误 |
| `$devui-warning` | #fac532 | 警告 |
| `$devui-info` | #5e7ce0 | 信息/通知 |

### 3.2 圆角

| 变量名 | 值 | 用途 |
|--------|-----|------|
| `$radius-xs` | 2px | 复选框、侧边栏 |
| `$radius-sm` | 4px | 按钮、标签、输入框 |
| `$radius-md` | 6px | 搜索框 |
| `$radius-lg` | 8px | 卡片 |
| `$radius-pill` | 16px | 圆角标签 |
| `$radius-round` | 999px | 头像、圆形按钮 |

### 3.3 阴影

| 变量名 | 值 | 用途 |
|--------|-----|------|
| `$shadow-card` | 0 1px 5.25px rgba(0,0,0,0.08) | 卡片、顶部导航 |
| `$shadow-overlay` | 0 4px 10.5px rgba(0,0,0,0.16) | 下拉面板、弹出层 |
| `$shadow-sidebar` | 1px 0 7px rgba(25,25,25,0.06) | 侧边栏 |

### 3.4 排版

| 变量名 | 值 | 用途 |
|--------|-----|------|
| `$devui-font-primary` | Noto Sans SC | 主字体 |
| `$devui-font-size-sm` | 12px | sm 组件字号 |
| `$devui-font-size-md` | 12px | md 组件字号 |
| `$devui-font-size-lg` | 14px | lg 组件字号 |
| `$devui-font-size-card-title` | 14px | 卡片标题 |
| `$devui-font-size-page-title` | 16px | 页面标题 |
| `$devui-font-size-modal-title` | 18px | 弹窗标题 |
| `$devui-line-height-base` | 1.5 | 基础行高 |

### 3.5 间距

| 变量名 | 值 | 用途 |
|--------|-----|------|
| `$spacing-button-icon-gap` | 4px | 按钮图标间距 |
| `$spacing-tag-inner-gap` | 4px | 标签内间距 |
| `$spacing-form-group-gap` | 8px | 表单组间距 |
| `$spacing-card-content-gap` | 16px | 卡片内容间距 |
| `$spacing-card-section-gap` | 20px | 卡片区域间距 |
| `$spacing-page-section-gap` | 10px | 页面区域间距 |
| `$spacing-pagination-gap` | 9px | 分页器间距 |
| `$spacing-sidebar-menu-gap` | 7px | 侧边菜单间距 |

---

## 4. devUI2.pen 组件速查（ref 使用 devui:ID）

### 按钮类

| 组件 | ref | 变体 |
|------|-----|------|
| 按钮-主要/md/default | `devui:RoYUx` | Size=md, Status=default |
| 按钮-主要/sm/default | `devui:VoApM` | Size=sm |
| 按钮-主要/lg/default | `devui:K9tFF` | Size=lg |
| 按钮-次要/md/default | `devui:qTc8e` | Size=md |
| 按钮-次要/lg/default | `devui:UQ59s` | Size=lg |
| 按钮-次要/sm/default | `devui:9auaH` | Size=sm |
| 按钮-图标文本/md/default | `devui:hOrvp` | Size=md |

### 导航类

| 组件 | ref | 变体 |
|------|-----|------|
| 页签 Tabs/number=4 | `devui:nCtvQ` | 4个选项 |
| 页签 Tabs/number=3 | `devui:hbi7t` | 3个选项 |
| 页签 Tabs/number=2 | `devui:6gvC2` | 2个选项 |
| 面包屑组/number=3 | `devui:iLVzA` | 3级面包屑 |
| 面包屑组/number=4 | `devui:jGzKJ` | 4级面包屑 |
| 面包屑 BreadCrumbs/面包屑 | `devui:0HCYy` | 面包屑 |

### 输入类

| 组件 | ref | 变体 |
|------|-----|------|
| 文本输入框/noContent | `devui:jmCZP` | status=noContent |
| 文本输入框/hasContent | `devui:wSpES` | status=hasContent |
| 搜索框-线框白底/left/default | `devui:X93Mt` | iconPosition=left, default |

### 标签类

| 组件 | ref | 变体 |
|------|-----|------|
| 标签/md/green | `devui:PXlZz` | Size=md, Color=green |
| 标签/md/orange | `devui:qWlVQ` | Size=md, Color=orange |
| 辅助标签/md/green | `devui:wcoqv` | Size=md, Color=green |
| 辅助标签/md/grey | `devui:JQE2Y` | Size=md, Color=grey |
| 常规标签/md | `devui:6LAHt` | Size=md |

### 复选框类

| 组件 | ref | 变体 |
|------|-----|------|
| 复选框/noChecked/default | `devui:bzYOF` | 未选中/默认 |
| 复选框/checked/default | `devui:S2hIB` | 选中/默认 |
| 复选框文本组合/noChecked/default | `devui:f0TO6` | 未选中/默认 |
| 复选框文本组合/checked/default | `devui:4q9SP` | 选中/默认 |

### 分页类

| 组件 | ref | 变体 |
|------|-----|------|
| 分页 Pagination/跳转=false | `devui:i5IDo` | 无跳转 |
| 分页 Pagination/跳转=true | `devui:9iCrn` | 有跳转 |

---

## 5. 常用组件规格（来自 llms-full.txt）

### 主按钮 (Primary Button)

- `cornerRadius`: [4,4,4,4], `fill`: #5e7ce0, `gap`: 4
- Size 变体 padding: sm=[4,16,4,16], md=[5,16,5,16], lg=[8,16,8,16]
- 文字: fontSize=14, fontFamily="Noto Sans SC", fill=#ffffff

### 次按钮 (Secondary Button)

- `fill`: #ffffff, `stroke`: #adb0b8 (1px inside)
- hover: stroke=#5e7ce0, textColor=#5e7ce0
- disabled: stroke=#dfe1e6, textColor=#babbc0

### 文本输入框 (TextInput)

- `cornerRadius`: [4,4,4,4], `fill`: #ffffff, `stroke`: #adb0b8 (1px), `height`: 32
- 文字: fontSize=14, padding=[5,12]
- focus: stroke=#5e7ce0, danger: stroke=#f66f6a, disabled: fill=#f5f5f5, stroke=#dfe1e6

### 复选框 (Checkbox)

- 尺寸: 16×16, `cornerRadius`: [2,2,2,2]
- unchecked: stroke=#adb0b8, fill=#ffffff; checked: fill=#5e7ce0
