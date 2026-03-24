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
- 导入后，ref 格式为 `devui:组件ID`（如 `devui:mYPZF`）
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
| 按钮-主要/md/default | `devui:mYPZF` | Size=md, Status=default |
| 按钮-主要/sm/default | `devui:Rl5jm` | Size=sm |
| 按钮-主要/lg/default | `devui:UtovU` | Size=lg |
| 按钮-次要/md/default | `devui:VKSqi` | Size=md |
| 按钮-次要/lg/default | `devui:rTL5w` | Size=lg |
| 按钮-次要/sm/default | `devui:jxhLP` | Size=sm |
| 按钮-图标文本/md/default | `devui:6LFBN` | Size=md |
| 按钮-图标文本/sm/default | `devui:3i79O` | Size=sm |

### 导航类

| 组件 | ref | 变体 |
|------|-----|------|
| 页签 Pills/number=2 | `devui:l9A3O` | 2个选项 |
| 页签 Pills/number=3 | `devui:Z70QE` | 3个选项 |
| 页签 Pills/number=4 | `devui:KEOhA` | 4个选项 |
| 页签 Pills/number=5 | `devui:6YelH` | 5个选项 |
| 页签 Pills/number=6 | `devui:8L4up` | 6个选项 |
| 面包屑组/number=2 | `devui:ydEdG` | 2级面包屑 |
| 面包屑组/number=3 | `devui:UOL0h` | 3级面包屑 |
| 面包屑组/number=4 | `devui:yl4Dd` | 4级面包屑 |
| 面包屑组/number=5 | `devui:EF14Z` | 5级面包屑 |
| 面包屑组/number=6 | `devui:oNW38` | 6级面包屑 |
| 面包屑组/ellipsis | `devui:H50rT` | 省略形式 |

### 输入类

| 组件 | ref | 变体 |
|------|-----|------|
| 文本输入框/noContent | `devui:rn9tI` | status=noContent |
| 文本输入框/hasContent | `devui:tdhOO` | status=hasContent |
| 文本输入框/hover | `devui:uF43C` | status=hover |
| 文本输入框/focus | `devui:OLGBd` | status=focus |
| 搜索框/left/default | `devui:pClmN` | iconPosition=left, default-noContent |
| 搜索框/right/default | `devui:sMfy0` | iconPosition=right, default-noContent |
| 数字输入框/default | `devui:ko1Kw` | status=default |
| 数字输入框/hover | `devui:hxtGb` | status=hover |

### 选择类

| 组件 | ref | 变体 |
|------|-----|------|
| 下拉选择框/default/未选/关 | `devui:zTtRm` | 默认/未选择/关闭 |
| 下拉选择框/default/已选/关 | `devui:g8ll6` | 默认/已选择/关闭 |
| 下拉选择框/未选/开 | `devui:LjSx5` | 带面板展开 |
| 下拉选择框/已选/开 | `devui:zvNlm` | 带面板展开/已选 |

### 标签类

| 组件 | ref | 变体 |
|------|-----|------|
| 标签/md/green | `devui:FQ7uH` | Size=md, Color=green |
| 标签/md/orange | `devui:97oGy` | Size=md, Color=orange |
| 辅助标签/md/green | `devui:rS2Ar` | Size=md, Color=green |
| 辅助标签/md/grey | `devui:6s2lw` | Size=md, Color=grey |
| 常规标签/md | `devui:xtggI` | Size=md |
| 常规标签/lg | `devui:BhCuI` | Size=lg |
| 线性标签/md/green | `devui:5Uwaj` | Size=md, Color=green |
| 线性标签/md/orange | `devui:rPKah` | Size=md, Color=orange |
| 线性标签/md/red | `devui:DCWif` | Size=md, Color=red |

### 复选框类

| 组件 | ref | 变体 |
|------|-----|------|
| 复选框文本/noChecked/default | `devui:zEXWw` | 未选中/默认 |
| 复选框文本/checked/default | `devui:Ee6NI` | 选中/默认 |
| 复选框文本/halfChecked/default | `devui:ORk6K` | 半选/默认 |

### 分页类

| 组件 | ref | 变体 |
|------|-----|------|
| 分页 Pagination/跳转=false | `devui:6gQ4a` | 无跳转 |
| 分页 Pagination/跳转=true | `devui:IRAdk` | 有跳转 |

### 表格类

| 组件 | ref | 变体 |
|------|-----|------|
| 表格/singleLine/shadow | `devui:8K8z3` | 单线/有阴影 |
| 表格/singleLine/noShadow | `devui:BUBhb` | 单线/无阴影 |
| 表格/withDividers/shadow | `devui:8Oq0P` | 分隔线/有阴影 |
| 表格/withDividers/noShadow | `devui:2PPub` | 分隔线/无阴影 |

### 卡片类

| 组件 | ref | 变体 |
|------|-----|------|
| 项目卡片/默认 | `devui:9qbEz` | 状态=默认 |
| 项目卡片/悬浮 | `devui:PyyzD` | 状态=悬浮 |
| 基本卡片/默认 | `devui:MBNRG` | 状态=默认 |
| 基本卡片/悬浮 | `devui:8vipZ` | 状态=悬浮 |
| 带图卡片/默认 | `devui:HKJpB` | 状态=默认 |
| 现网卡片/默认 | `devui:JIqzC` | 状态=默认 |

### 页面框架类

| 组件 | ref | 变体 |
|------|-----|------|
| 顶部导航/default | `devui:Uexy2` | 种类=default |
| 顶部导航/占位 | `devui:2bjDj` | 种类=占位 |
| 工具链侧栏/展开 | `devui:E36oP` | 展开=on |
| 工具链侧栏/收起 | `devui:SQOb3` | 展开=off |
| 手风琴侧边栏 | `devui:K0pVg` | 完整侧边栏 |
| 头信息/default | `devui:TUWxd` | 默认 |
| 头信息/search/2项 | `devui:ZU5hh` | 带搜索 |
| 头信息/search/3项 | `devui:ju9uI` | 带搜索 |
| 头信息/search/4项 | `devui:v7KDW` | 带搜索 |

### 弹窗与步骤

| 组件 | ref | 变体 |
|------|-----|------|
| 模态弹窗/非模态 | `devui:xbwXy` | 非模态 |
| 模态弹窗/模态 | `devui:WJxDN` | 模态（全屏遮罩） |
| 步骤条/横向-左右布局 | `devui:Zavv1` | 横向 |

---

## 5. 常用组件规格（来自 llms-full.txt）

### 主按钮 (Primary Button)

- `cornerRadius`: [4,4,4,4], `fill`: #5e7ce0, `gap`: 4
- Size 变体 padding: sm=[3,16], md=[5,16], lg=[9,20]
- 文字: fontSize=14, fontFamily="Noto Sans SC", fill=#ffffff

### 次按钮 (Secondary Button)

- `fill`: #ffffff, `stroke`: #adb0b8 (1px inside)
- hover: stroke=#575d6c; active: stroke=#5e7ce0
- disabled: fill=#f5f5f5, stroke=#dfe1e6

### 文本输入框 (TextInput)

- `cornerRadius`: [4,4,4,4], `fill`: #ffffff, `stroke`: #adb0b8 (1px), `height`: 32
- 文字: fontSize=14, padding=[5,8]
- focus: stroke=#5e7ce0, danger: stroke=#f66f6a, disabled: fill=#f3f3f3, stroke=#dfe1e6

### 复选框 (Checkbox)

- 尺寸: 16×16, `cornerRadius`: [2,2,2,2]
- unchecked: stroke=#adb0b8, fill=#ffffff; checked: fill=#5e7ce0
