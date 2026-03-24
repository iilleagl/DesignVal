---
name: pen-design-generator
description: Generate UI design drafts (.pen files) using Pencil MCP tools with DevUI component library and specification. Use when the user asks to create UI designs, mockups, screens, dashboards, or any visual design task that involves .pen files, DevUI components, or Pencil design tools.
---

# Pencil DevUI 设计稿生成

使用 Pencil MCP 工具 + DevUI 组件库 + 设计规范文档，生成符合 DevUI 规范的 .pen 设计稿。

---

## 组件文案填充（必读）

### 为什么必须对组件中的文案进行填充

组件库中的组件（顶栏、侧栏、面包屑、页签、表格、卡片等）自带的是**占位文案**（如「一级菜单」「二级菜单」「页签一」「编号」「标题」）。若插入 ref 后不替换这些文案，设计稿会：

- **语义不完整**：页面仍显示占位文字，无法表达真实业务含义；
- **无法交付**：开发或评审无法从设计稿理解实际界面内容；
- **易被漏审**：多文案组件（尤其侧栏、顶栏）一旦漏填，整块区域都会保留占位，影响最大。

因此：**凡使用 ref 引用的组件，只要内含可读文案（菜单、表头、按钮文字、标签、页签等），都必须按业务需求替换为实际文案。**

### 哪些组件需要填充文案

| 组件类型 | 需填充内容 | 说明 |
|----------|------------|------|
| **顶栏** `etDDY`/`Uexy2` | 产品名、菜单项、区域、用户等 | 多文本节点，必须一次性在 descendants 中填齐 |
| **侧栏/工具链导航** `E36oP`、`K0pVg` | 项目名、一级/二级菜单项 | 极易遗漏，插入时必须带齐 descendants |
| **面包屑** `AlQDE` 等 | 各层级路径文案 | 2～6 层按实际层级填 |
| **头信息** `hJlzm`/`TUWxd` | 标题、返回按钮、辅助信息、详情行 | 与页面业务强相关 |
| **页签** `5AtIy` 等 | 每个页签的标签文字 | 与当前页功能一致 |
| **按钮** `tSwIg`、`ChE0Z` 等 | 按钮上的文字 | 如「返回」「提交」「取消」 |
| **表格** `xz7LI` 等 | 表头列名、关键单元格 | 表头必须为业务列名，不能留「编号」「标题」等 |
| **卡片** `a74K6`、`QnsHG` 等 | 标题、描述、数据、操作文字 | 用于数据展示时需填具体指标与说明 |
| **搜索框** `sLVmB`/`pClmN` | 占位提示文案 | 如「请输入关键词」 |
| **标签** `jezfD` 等 | 标签文字 | 如「进行中」「已通过」 |

### 如何填充：插入时用 descendants 一次性填齐

- **推荐做法**：在 `I(parent, { type: "ref", ref: "组件ID", descendants: { "所有文本子节点ID": { content: "实际文案" }, ... } })` 中，**在插入时**就通过 `descendants` 传入该组件内**所有**需要展示的文本节点及其文案。
- **前置步骤**：先用 `batch_get(nodeIds=["devui:组件ID"], readDepth=3, resolveInstances=true)` 读出组件内部结构，找到所有 `type: "text"` 或带 `content` 的节点 ID（导出时为 `devui:xxx`），再在 Spec 或内容物料表中列出「节点 ID → 业务文案」的映射，插入时一次性写入 descendants。
- **禁止**：插入多文案组件时不带 descendants 或只填部分文案（如只改顶栏、不改侧栏），导致页面出现「一级菜单」「二级菜单」等占位。若首次漏填，只能删除该实例后重新插入并带齐 descendants；不要依赖事后 `U(实例ID/devui:子节点ID)` 补文案，以免污染组件定义。

详见下方「阶段 3：设计 — 组件优先」中的优先级 1 与多文案组件特别说明。

---

## 资源路径

| 资源 | 路径 |
|------|------|
| 组件库 | `designsystem/devUI/components/devUI2.pen`（相对项目根目录） |
| 规范文档 | `designsystem/devUI/llms-full.txt`（相对项目根目录） |

## 工作流程

### 阶段 0：环境检查 — Import 组件库（前置必做）

在任何设计操作之前，确保目标设计文件已导入 DevUI 组件库。

**0.1 检查 import 状态**

```
pencil.get_editor_state(include_schema=false)
```

查看文档 imports 中是否已存在指向 `devUI2.pen` 的条目。如已存在 → 跳到阶段 1。

**0.2 添加 import**

若缺少 import，需直接修改目标 .pen 文件（JSON 格式）。在文件顶层 JSON 对象中添加 `imports` 字段：

```json
"imports": {
  "devui": "<从目标文件到组件库的相对路径>"
}
```

相对路径示例：若设计文件在项目根目录 `my.pen`，组件库在 `designsystem/devUI/components/devUI2.pen`，则相对路径为 `designsystem/devUI/components/devUI2.pen`。

使用 Shell + `jq` 或 `StrReplace` 操作 .pen 文件添加 imports。

**0.3 重新加载文件**

修改磁盘文件后，**必须** 调用 `reloadfile` 让 Pencil 重新加载：

```
MCP: user-pen-component-copy → reloadfile(file_path="<目标文件绝对路径>")
```

**0.4 验证导入**

```
pencil.get_editor_state(include_schema=false)
```

确认 Reusable Components 列表中出现了 devUI2.pen 的组件（ref 格式为 `devui:组件ID`）。

---

### 阶段 1：准备 — 理解需求与组件选型

**1.1 读取规范文档**

读取项目内 `designsystem/devUI/llms-full.txt`。关注：颜色体系、排版体系、间距规则、阴影与圆角、组件规格。

**1.2 根据场景选择正确的组件**

不要盲目搜索组件，先根据需求场景查阅下方「DevUI 组件选型速查表」，确定每个 UI 元素应该使用哪个组件及其 ID。设计稿中一般使用 **default** 状态的组件。

**1.3 深度读取关键组件**

确定组件后，用 `batch_get` 读取内部结构（获取子节点 ID，后续 descendants 修改需要）：

```
pencil.batch_get(nodeIds=["devui:组件ID1", "devui:组件ID2"], readDepth=3, resolveInstances=true)
```

**1.4 补充搜索**

如果速查表中没有匹配的组件，再通过搜索确认：

```
pencil.batch_get(patterns=[{reusable: true, name: "关键词"}], searchDepth=2)
```

---

### 阶段 2：规划设计稿结构

完整规划页面布局，**必须**为每个区域标注具体的组件 ID（从速查表获取）：

```
设计稿结构示例（数据列表页）：
├── 顶部导航栏 → devui:Uexy2
├── 左侧边栏 → devui:E36oP（工具链导航/展开=on）
├── 内容区
│   ├── 面包屑 → devui:UOL0h（3层）
│   ├── 页面标题 → 无匹配组件，按规范自建
│   ├── 搜索框 → devui:pClmN（左图标/default）
│   ├── 页签 → devui:Z70QE（Pills/3项）
│   ├── 数据表格 → devui:8K8z3（singleLine/有阴影）
│   ├── 分页器 → devui:6gQ4a
│   └── 操作按钮 → devui:mYPZF（主要/md）+ devui:VKSqi（次要/md）
```

```
设计稿结构示例（表单页）：
├── 头信息 → devui:TUWxd
├── 表单区
│   ├── 表单组件-输入框 → devui:QzXy7（输入框/带按钮/showExtraInfo=false）
│   ├── 表单组件-下拉选择 → devui:lXYgx（下拉选择/带按钮/showExtraInfo=false）
│   ├── 复选框文本组合 → devui:zEXWw（未选/default）
│   └── 按钮组 → devui:mYPZF + devui:VKSqi
```

---

### 阶段 3：设计 — 组件优先

**核心原则**：充分使用组件库中的组件。在保证意图不冲突的前提下，优先调用组件实现设计意图。

#### 优先级 1：ref 引用 + descendants（最优）

条件：组件库有完全匹配的组件。导入后 ref 格式为 `devui:组件ID`（如 `devui:mYPZF`）。

**必须**用 `I(..., {type: "ref", ref: "组件ID", descendants: { "所有文本子节点ID": { content: "实际文案" }, ... }})` 在插入时通过 descendants 修改**全部**文本图层。禁止不带 descendants 的 ref 插入，禁止遗漏文本图层。

**特别强调 — 多文案组件（顶栏、侧栏、头信息、表格等）**：顶栏、**左侧栏/工具链导航**、头信息、数据表格等组件内含有多个菜单项/表头/单元格文案。插入这类 ref 时，**必须**在当次 `I(..., { ref, descendants })` 中一次性填齐该组件内所有需要展示的文本节点（先用 `batch_get(..., resolveInstances=true)` 读出所有 text 节点 ID），不得遗漏。否则后续用 `U(实例ID/devui:子节点ID)` 会污染组件定义、影响同文件其他实例；若首次未带齐 descendants，只能删除该实例后重新插入并带齐 descendants。

#### 优先级 2：复制后修改

条件：组件结构接近但部分不满足（需增删子节点）。

```javascript
navbar=C("devui:导航栏组件ID", screen, {
  width: "fill_container",
  descendants: { ... }
})
```

#### 优先级 3：按规范从零创建（最后手段）

条件：确认组件库中无匹配组件。**必须**使用 design token 变量（如 `$devui-text`、`$radius-sm`）。

**每个 `batch_design` 调用最多 25 个操作。**

**示例 — ref 复用并改文案（推荐用 descendants，见 reference 1.3）：**

```javascript
breadcrumb=I(header, {
  type: "ref",
  ref: "面包屑组件ID",
  width: "fill_container",
  descendants: {
    "第1级文本ID": { content: "首页" },
    "第2级文本ID": { content: "项目名称" },
    "第3级文本ID": { content: "代码托管" }
  }
})
```

**示例 — 复制后修改（导航栏菜单项）：**

```javascript
navbar=C("导航栏组件ID", screen, {width: "fill_container"})
U(navbar+"/标题文本ID", {content: "我的应用"})
D(navbar+"/多余菜单项ID")
newItem=R(navbar+"/旧菜单项ID", {type: "text", content: "新菜单项"})
```

**示例 — 从零创建（无匹配组件时）：**

```javascript
title=I(container, {type: "text", content: "页面标题", fontSize: 16, fontWeight: "700", fill: "#252B3A", fontFamily: "Noto Sans SC", lineHeight: 1.5})
```

---

### 阶段 4：验证

每完成一个主要区域后截图验证：`pencil.get_screenshot(nodeId="区域节点ID")`。检查布局、颜色、字号、文案是否已替换。发现问题立即修复。

---

## 组件使用要点

- 插入 ref 实例前，**必须**先用 `batch_get(readDepth=3, resolveInstances=true)` 读取组件内部结构，获取子节点 ID（导入组件为 `devui:子节点ID`）。
- 在 `descendants` 或后续 `U(实例ID/devui:子节点ID, {...})` 中逐一替换文本/图标。
- 选择从零创建前，必须确认已搜索组件库且无匹配组件。
- 组件名中带「/」描述变体属性（如「按钮/尺寸-Size=md, 状态-Status=default」），以 `.` 开头的是**基础子组件**，通常不直接使用，而是作为更高级组件的构成部分。
- 设计稿中一般使用 **default** 状态的组件，除非需要展示交互态。

---

## DevUI 组件选型速查表

根据 UI 需求场景，直接查找对应的组件 ID。所有 ID 在 ref 时加 `devui:` 前缀（如 `devui:mYPZF`）。

### 1. 按钮 Button

| 场景 | 组件 | 推荐 ID（default 状态） |
|------|------|------------------------|
| 主操作（提交、确认、新建） | 按钮-主要 `tSwIg` | `mYPZF`(md) `Rl5jm`(sm) `UtovU`(lg) |
| 辅助操作（取消、返回、编辑） | 按钮-次要 `ChE0Z` | `VKSqi`(md) `jxhLP`(sm) `rTL5w`(lg) |
| 带图标的操作按钮 | 按钮-图标文本按钮 `Krfl3` | `6LFBN`(md) `3i79O`(sm) |
| 带下拉菜单的按钮 | 按钮-可下拉次要组合按钮 `rrLTG` | `ziNQG`(icon/md) `r9lnG`(icon/sm) `rJDJL`(number/md) `gZrTy`(number/sm) |

**尺寸规则**: lg→页面主操作区，md→表单/卡片内，sm→表格行内或紧凑空间。

### 2. 页签 Tabs

| 场景 | 组件 | 推荐 ID |
|------|------|--------|
| 胶囊式切换（紧凑筛选） | 页签Pills `5AtIy` | `l9A3O`(2项) `Z70QE`(3项) `KEOhA`(4项) `6YelH`(5项) `8L4up`(6项) |

### 3. 面包屑 BreadCrumbs

| 场景 | 组件 | 推荐 ID |
|------|------|--------|
| 标准面包屑（按层级数选） | 面包屑组 `AlQDE` | `ydEdG`(2层) `UOL0h`(3层) `yl4Dd`(4层) `EF14Z`(5层) `oNW38`(6层) |
| 省略形式面包屑 | 面包屑组 | `H50rT`(ellipsis) |

### 4. 标签 Tag

| 场景 | 组件 | 推荐 ID |
|------|------|--------|
| 状态标签（成功/运行中） | 标签 `jezfD` | `FQ7uH`(md/green) `97oGy`(md/orange) `SCjyy`(lg/green) `sgr9e`(lg/orange) |
| 辅助信息标签 | 辅助标签 `qyFas` | `rS2Ar`(md/green) `6s2lw`(md/grey) `M7pBw`(lg/green) `GeQ2G`(lg/grey) |
| 通用标签（分类/标记） | 常规标签 `S4vFN` | `xtggI`(md) `BhCuI`(lg) |
| 线性轮廓标签 | 线性标签 `9iCpY` | `5Uwaj`(md/green) `rPKah`(md/orange) `DCWif`(md/red) `vbC5I`(lg/green) `2cBdA`(lg/orange) `9wtql`(lg/red) |

**颜色语义**: green=成功/正常，orange=警告/进行中，red=错误/危险，grey=默认/禁用。

### 5. 搜索框 Search

| 场景 | 推荐 ID |
|------|--------|
| 默认搜索框（左图标） | `pClmN`(default-noContent) |
| 右侧搜索图标 | `sMfy0`(default-noContent) |
| 带已有内容的搜索框 | `Yvn9i`(left/contentpresent) `WwjQs`(right/contentpresent) |
| hover 状态 | `8wlP5`(left) `eMmaO`(right) |
| 激活-等待输入 | `8440P`(left) `fFllq`(right) |
| 激活-已输入 | `3oslM`(left) `bE46t`(right) |
| 禁用 | `kUBVi`(left) `ljKNe`(right) |

### 6. 分类搜索 CategorySearch

| 场景 | 推荐 ID |
|------|--------|
| 默认状态（标签关） | `TnjT0`(default/tag=关) |
| 默认状态（标签开） | `Egl1a`(default/tag=开) |
| hover 状态 | `YZlVY`(hover/tag=关) `FH7dj`(hover/tag=开) |

### 7. 复选框 Checkbox

| 场景 | 推荐 ID |
|------|--------|
| 带文本 - 未选中 | `zEXWw`(default) `Z7suW`(hover) `0MYsw`(disabled) |
| 带文本 - 已选中 | `Ee6NI`(default) `TlgP7`(hover) `ZkDgw`(disabled) |
| 带文本 - 半选 | `ORk6K`(default) `jyQdg`(hover) `5JUes`(disabled) |

### 8. 分页器 Pagination

| 场景 | 推荐 ID |
|------|--------|
| 标准分页（无跳转） | `6gQ4a` |
| 带跳转输入的分页 | `IRAdk` |

### 9. 输入框 TextInput

| 场景 | 组件 | 推荐 ID |
|------|------|--------|
| 标准文本输入 | 文本输入框 `zUrj8` | `rn9tI`(noContent) `tdhOO`(hasContent) `uF43C`(hover) `OLGBd`(focus) `yF2iu`(input) `QgeQz`(danger) `Um9VZ`(success) `ZnH43`(disabled) |
| 数字输入 | 数字输入框 `FPTv3` | `ko1Kw`(default) `hxtGb`(hover) `w16xK`(left-hover) `CDf29`(right-hover) `l7vk3`(disabled) |
| 多行文本输入 | 表单项-多行文本输入框 `VFC67` | `qjjWq` |
| 表单标题 | 表单标题 `mySBY` | `7iMMv`(基础) `78DAm`(必填) `67xGb`(提示图标) `kzZ0d`(必填+提示) |

表单项-文本输入框由表单标题 + 文本输入框 + 可选辅助文本组成。选择时确定：`状态-status`、`必选图标-required`、`提示图标-helpTips`、`是否展示辅助文本-showExtraInfo`。

### 10. 选择框 Select

| 场景 | 组件 | 推荐 ID |
|------|------|--------|
| 单选下拉框（未选/关） | 下拉选择框 `zlQjV` | `zTtRm`(default/未选/关) |
| 单选下拉框（已选/关） | 下拉选择框 | `g8ll6`(default/已选/关) |
| 单选下拉框（展开） | 下拉选择框 | `LjSx5`(未选/开) `zvNlm`(已选/开) |
| 其他状态 | 下拉选择框 | `oEm0T`(hover/未选) `V8Ggo`(hover/已选) `JTmP2`(select/未选) `OX3vH`(select/已选) `GK2ZR`(active/已选) `JRnyz`(disabled) |

### 11. 表格 DataTable

| 场景 | 推荐 ID |
|------|--------|
| 单线表格（有阴影） | `8K8z3` |
| 单线表格（无阴影） | `BUBhb` |
| 带分隔线表格（有阴影） | `8Oq0P` |
| 带分隔线表格（无阴影） | `2PPub` |

**嵌套结构**:
```
表格
├── 表头行 → 表头单项 × N（position: startPosition/middleItem/endPosition）
└── 表体行 × M → 表体单项 × N
    contentType: text/link/treeStructure/statusWithName/iconWithLabelAndTitle/
                 textWithLabel/tags/labelWithText/priorityLevel/perationColumn/checkBox
```

### 12. 筛选 Filter

| 场景 | 推荐 ID |
|------|--------|
| 简易筛选（单条件） | `Jz8Tn`(default) `kasjZ`(hover) `IBiU4`(active) |
| 复杂筛选（多条件） | `3Nppx`(default) `xwumW`(hover) `ImL7Y`(active) |

### 13. 表单 Form

| 场景 | 推荐 ID |
|------|--------|
| 下拉选择表单项（带按钮，无辅助文本） | `lXYgx` |
| 下拉选择表单项（带按钮，有辅助文本） | `ziusM` |
| 下拉选择表单项（无按钮，无辅助文本） | `Crm3Z` |
| 下拉选择表单项（无按钮，有辅助文本） | `H2LJA` |
| 输入框表单项（带按钮，无辅助文本） | `QzXy7` |
| 输入框表单项（带按钮，有辅助文本） | `AEMdH` |
| 输入框表单项（无按钮，无辅助文本） | `Zk0Ev` |
| 输入框表单项（无按钮，有辅助文本） | `XI7d1` |

### 14. 卡片 Cards

| 场景 | 组件 | 推荐 ID |
|------|------|--------|
| 项目卡片（带项目图标） | 项目卡片 `a74K6` | `9qbEz`(默认) `PyyzD`(悬浮) `0sBFU`(悬浮-标题变蓝) |
| 基本卡片（通用展示） | 基本卡片 `QnsHG` | `MBNRG`(默认) `8vipZ`(悬浮) `veIiD`(悬浮-标题变蓝) |
| 带图卡片 | 带图卡片 `RKPRI` | `HKJpB`(默认) `Z9pnT`(悬浮) `UXGvV`(悬浮-标题变蓝) |
| 现网卡片样式 | 现网卡片样式 `cpmQU` | `JIqzC`(default) `eJVv6`(hover) |

### 15. 头信息 Header

| 场景 | 推荐 ID |
|------|--------|
| 默认头信息 | `TUWxd`(default) |
| 带搜索的头信息（2项） | `ZU5hh` |
| 带搜索的头信息（3项） | `ju9uI` |
| 带搜索的头信息（4项） | `v7KDW` |

### 16. 导航

#### 顶部导航栏

| 场景 | 推荐 ID |
|------|--------|
| 默认顶部导航栏 | `Uexy2`(种类=default) |
| 占位顶部导航栏 | `2bjDj`(种类=占位) |

#### 工具链专用侧边栏

| 场景 | 推荐 ID |
|------|--------|
| 展开状态 | `E36oP`(展开=on) |
| 收起状态 | `SQOb3`(展开=off) |

#### 手风琴侧边导航

| 场景 | 推荐 ID |
|------|--------|
| 完整侧边栏 | `K0pVg` |

### 17. 链接 Link

| 场景 | 推荐 ID |
|------|--------|
| 默认链接 | `mhEH0`(默认) `3RfnO`(悬浮) |
| 表格文字黑色链接 | `LEdP1`(默认/无前缀图标) `JJnfg`(默认/有前缀图标) |
| 表格加粗列文字链接 | `o7CIP`(默认) `T543A`(悬浮) |

### 18. 业务组件

| 场景 | 推荐 ID |
|------|--------|
| 左侧选择菜单卡片 | `VP3uY` |
| Banner（大横幅） | `Zj0tz` |
| 公告卡片 | `FvbbS` |
| 活动卡片 | `gk3XY` |
| 帮助文档卡片 | `x0QDF` |
| 字母图标 | `N8QxK`（帧内按字母选择） |

### 19. 模态弹窗 Modal

| 场景 | 推荐 ID |
|------|--------|
| 非模态弹窗 | `xbwXy` |
| 模态弹窗（全屏遮罩） | `WJxDN` |

### 20. 步骤条 TaskStep

| 场景 | 推荐 ID |
|------|--------|
| 横向-左右布局 | `Zavv1` |
| 横向-居中对齐 | `qPPvF`（帧内选变体） |
| 纵向步骤条 | `FYkld`（帧内选变体） |

### 21. 其他组件

| 场景 | 组件 | 推荐 ID |
|------|------|--------|
| 进度条（条形） | 进度条 Progress | `bMfa8` |
| 进度条（圆形） | 进度条-circle | `QqPAN` |
| 徽标 | 徽标 Badge | `neMUc`(默认) `HfYS3`(小尺寸) |
| 图片上传 | 图片上传 ImageUpload | `cA3sd` |
| 级联菜单 | 级联菜单 Cascader | `fXw1o` |
| 缺省页插画 | 缺省页插画 | `UksPg`(缺省图) `aZADr`(小尺寸卡片插图) |
| 滚动条 | 滚动条 Scrollbar | `tzbQI`(竖向/默认) `vBb1r`(横向/默认) `jHuhG`(竖向/小) `Gy5v0`(横向/小) |

---

## 典型页面布局模板

### 数据列表页

```
顶部导航栏 (devui:Uexy2)
├── 侧边栏 (devui:E36oP 或 devui:K0pVg)
└── 主内容区
    ├── 头信息 (devui:TUWxd) 或 面包屑 (devui:UOL0h)
    ├── 筛选/搜索区 (devui:Jz8Tn + devui:pClmN + 按钮)
    ├── 页签切换 (devui:Z70QE 或 devui:KEOhA)
    ├── 数据表格 (devui:8K8z3)
    └── 分页器 (devui:6gQ4a)
```

### 表单页

```
头信息 (devui:TUWxd)
└── 表单区域
    ├── 表单组件-输入框 (devui:QzXy7) × N
    ├── 表单组件-下拉选择 (devui:lXYgx) × N
    ├── 复选框文本组合 (devui:zEXWw)
    └── 按钮组 (devui:mYPZF + devui:VKSqi)
```

### 卡片网格页

```
顶部导航栏 (devui:Uexy2)
├── 侧边栏 (devui:E36oP)
└── 主内容区
    ├── 头信息 (devui:TUWxd)
    ├── 筛选/搜索区
    └── 卡片网格 (devui:9qbEz 或 devui:MBNRG) × N
```

---

## 详细参考

- Design Token 变量表、组件 ID 速查见 [reference.md](reference.md)
- 规范文档见项目内 `designsystem/devUI/llms-full.txt`
