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
| **顶栏** Rpv7B | 产品名、菜单项、区域、用户等 | 多文本节点，必须一次性在 descendants 中填齐 |
| **侧栏/工具链导航** JGEqF、kyl45 | 项目名、一级/二级菜单项 | 极易遗漏，插入时必须带齐 descendants |
| **面包屑** iLVzA 等 | 各层级路径文案 | 2～6 层按实际层级填 |
| **头信息** Xxf4j | 标题、返回按钮、辅助信息、详情行 | 与页面业务强相关 |
| **页签** hbi7t、cee0f 等 | 每个页签的标签文字 | 与当前页功能一致 |
| **按钮** RoYUx、qTc8e 等 | 按钮上的文字 | 如「返回」「提交」「取消」 |
| **表格** 35iCd 等 | 表头列名、关键单元格 | 表头必须为业务列名，不能留「编号」「标题」等 |
| **卡片** 7ipso、LcKkl 等 | 标题、描述、数据、操作文字 | 用于数据展示时需填具体指标与说明 |
| **搜索框** X93Mt | 占位提示文案 | 如「请输入关键词」 |
| **标签** PXlZz 等 | 标签文字 | 如「进行中」「已通过」 |

### 如何填充：插入时用 descendants 一次性填齐

- **推荐做法**：在 `I(parent, { type: "ref", ref: "devui:组件ID", descendants: { "devui:文本节点ID": { content: "实际文案" }, ... } })` 中，**在插入时**就通过 `descendants` 传入该组件内**所有**需要展示的文本节点及其文案。
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
├── 顶部导航栏 → devui:Rpv7B
├── 左侧边栏 → devui:JGEqF（工具链导航/展开）
├── 内容区
│   ├── 面包屑 → devui:iLVzA（3层）
│   ├── 页面标题 → 无匹配组件，按规范自建
│   ├── 搜索框 → devui:X93Mt（左图标/default）
│   ├── 页签 → devui:hbi7t（Tabs/3项）
│   ├── 数据表格 → devui:35iCd（单线/有阴影）
│   ├── 分页器 → devui:i5IDo
│   └── 操作按钮 → devui:RoYUx（主要/md）+ devui:qTc8e（次要/md）
```

```
设计稿结构示例（表单页）：
├── 头信息 → devui:Xxf4j
├── 表单区
│   ├── 表单项-文本输入框 → devui:Laiht（noContent/基础）
│   ├── 表单项-下拉选择框 → devui:qw7Ux（noContent）
│   ├── 复选框文本组合 → devui:f0TO6（未选/default）
│   └── 按钮组 → devui:RoYUx + devui:qTc8e
```

---

### 阶段 3：设计 — 组件优先

**核心原则**：充分使用组件库中的组件。在保证意图不冲突的前提下，优先调用组件实现设计意图。

#### 优先级 1：ref 引用 + descendants（最优）

条件：组件库有完全匹配的组件。导入后 ref 格式为 `devui:组件ID`（如 `devui:RoYUx`）。

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

---

### 阶段 4：验证

每完成一个主要区域后截图验证：`pencil.get_screenshot(nodeId="区域节点ID")`。检查布局、颜色、字号、文案是否已替换。发现问题立即修复。

---

## 组件使用要点

- 插入 ref 实例前，**必须**先用 `batch_get(readDepth=3, resolveInstances=true)` 读取组件内部结构，获取子节点 ID（导入组件为 `devui:子节点ID`）。
- 在 `descendants` 或后续 `U(实例ID/devui:子节点ID, {...})` 中逐一替换文本/图标。
- 选择从零创建前，必须确认已搜索组件库且无匹配组件。
- 以 `.` 开头的组件（如 `.基础面包屑组件`）是**基础子组件**，通常不直接使用，而是作为更高级组件的构成部分。
- 设计稿中一般使用 **default** 状态的组件，除非需要展示交互态。

---

## DevUI 组件选型速查表

根据 UI 需求场景，直接查找对应的组件 ID。所有 ID 在 ref 时加 `devui:` 前缀（如 `devui:RoYUx`）。

### 1. 按钮 Button

| 场景 | 组件 | 推荐 ID（default 状态） |
|------|------|------------------------|
| 主操作（提交、确认、新建） | 按钮-主要 | `RoYUx`(md) `VoApM`(sm) `K9tFF`(lg) |
| 辅助操作（取消、返回、编辑） | 按钮-次要 | `qTc8e`(md) `9auaH`(sm) `UQ59s`(lg) |
| 带图标的操作按钮 | 按钮-图标文本按钮 | `hOrvp`(md) `pQrIo`(sm) |
| 带下拉菜单的按钮 | 按钮-可下拉次要组合按钮 | `XE86l`(md/icon) `hrHhN`(md/number) |

**尺寸规则**: lg→页面主操作区，md→表单/卡片内，sm→表格行内或紧凑空间。

### 2. 页签 Tabs

| 场景 | 组件 | 推荐 ID |
|------|------|--------|
| 胶囊式切换（紧凑筛选） | 页签Pills | `Mtrw0`(4项) `cee0f`(3项) `Fyjni`(2项) |
| 标准下划线页签 | 页签Tabs | `nCtvQ`(4项) `hbi7t`(3项) `6gvC2`(2项) |
| 环绕式页签（卡片式） | 页签Wrapped | `ABY1y`(2项) `dl8H7`(3项) `ulUOy`(4项) |
| 带图标的页签 | 页签Icon | `Qrd7b`(3项) `mOgNp`(2项) |
| 纯图标页签（视图切换） | 页签-图标页签 | `RcvJ4`(2项) `n92Tu`(3项) |

### 3. 面包屑 BreadCrumbs

| 场景 | 组件 | 推荐 ID |
|------|------|--------|
| 标准面包屑（按层级数选） | 面包屑组 | `WYqKP`(2层) `iLVzA`(3层) `jGzKJ`(4层) `AnLIL`(5层) `rC1xU`(6层) |
| 省略形式面包屑 | 面包屑组/ellipsis | `mkJuD` |

### 4. 标签 Tag

| 场景 | 组件 | 推荐 ID |
|------|------|--------|
| 状态标签（成功/运行中） | 标签 | `PXlZz`(md/green) `qWlVQ`(md/orange) |
| 辅助信息标签 | 辅助标签 | `wcoqv`(md/green) `JQE2Y`(md/grey) |
| 通用标签（分类/标记） | 常规标签 | `6LAHt`(md) `WZFF6`(lg) |
| 线性轮廓标签 | 线性标签 | `rqTmW`(md/green) `UyGV1`(md/orange) `VnbP7`(md/red) |

**颜色语义**: green=成功/正常，orange=警告/进行中，red=错误/危险，grey=默认/禁用。

### 5. 搜索框 Search

| 场景 | 推荐 ID |
|------|--------|
| 默认搜索框（左图标） | `X93Mt`(default-noContent) |
| 右侧搜索图标 | `xzhr5`(default-noContent) |
| 分类搜索（带标签） | `Pts3s`(default/关) `9M9md`(default/开) |

### 6. 复选框 Checkbox

| 场景 | 推荐 ID |
|------|--------|
| 纯复选框（表格行选择） | `bzYOF`(未选) `S2hIB`(已选) `c45Iy`(半选) |
| 带文本的复选框 | `f0TO6`(未选) `4q9SP`(已选) `JEIKW`(半选) |

### 7. 分页器 Pagination

| 场景 | 推荐 ID |
|------|--------|
| 标准分页（无跳转） | `i5IDo` |
| 带跳转输入的分页 | `9iCrn` |

### 8. 输入框 TextInput

| 场景 | 组件 | 推荐 ID |
|------|------|--------|
| 标准文本输入 | 文本输入框 | `jmCZP`(noContent) `wSpES`(hasContent) |
| 数字输入 | 数字输入框 | `1ggPm`(default) |
| 带标题的表单输入项 | 表单项-文本输入框 | `Laiht`(noContent/基础) `IKx4V`(noContent/必填) |
| 表单标题 | 表单标题 | `byJ1L`(基础) `Rl404`(必填) `VPtKX`(必填+提示) |

表单项-文本输入框的选择需确定 4 个属性：`状态-status`、`必选图标-required`、`提示图标-helpTips`、`是否展示辅助文本-showExtraInfo`。

### 9. 选择框 Select

| 场景 | 组件 | 推荐 ID |
|------|------|--------|
| 单选下拉框（关） | 下拉选择框 | `wDKSI`(未选) `PdpLn`(已选) |
| 单选下拉框（开） | 下拉选择框 | `of7nh` |
| 多选下拉框 | 下拉选择框-多选 | `QHiNZ`(Default) `6R9AA`(active) |
| 表单中的下拉选择 | 表单项-下拉选择框 | `qw7Ux`(noContent) `NckfV`(hasContent) |

### 10. 表格 DataTable

| 场景 | 推荐 ID |
|------|--------|
| 单线表格（有阴影） | `35iCd` |
| 单线表格（无阴影） | `aIr8R` |
| 带分隔线表格（有阴影） | `e9Fdp` |
| 带分隔线表格（无阴影） | `ZxEIK` |

**嵌套结构**:
```
表格
├── 表头行 → 默认类/表头单项 × N（position: startPosition/middleItem/endPosition）
└── 表体行 × M → 默认类/表体单项 × N
    contentType: text/link/treeStructure/statusWithName/iconWithLabelAndTitle/
                 textWithLabel/tags/labelWithText/priorityLevel/perationColumn/checkBox
```

**子组件**: `.操作列` `IcutX`/`ED8JJ`/`RDeTa`，`.priority-flag` `QFgfR`(低)/`1RjoZ`(中)/`4031i`(高)，`.表体组件/状态图标` `ZxnlF`(success)/`4h5bF`(info)/`01K6T`(warning)

### 11. 筛选 Filter

| 场景 | 推荐 ID |
|------|--------|
| 简易筛选（单条件） | `8hidv`(default) |
| 复杂筛选（多条件） | `dXtcd`(default) |
| 筛选选择面板 | `Hk6wG`(3项) `89xhB`(4项) `oIVzC`(5项) `fGhHM`(6项) |

### 12. 表单 Form

| 场景 | 推荐 ID |
|------|--------|
| 下拉选择表单项（带按钮） | `PQwRQ` |
| 下拉选择表单项（无按钮） | `jbFdp` |
| 输入框表单项（带按钮） | `hzV0w` |
| 输入框表单项（无按钮） | `xdkiR` |

### 13. 卡片 Cards

| 场景 | 组件 | 推荐 ID |
|------|------|--------|
| 项目卡片（带项目图标） | 项目卡片 | `LcKkl`(默认) |
| 基本卡片（通用展示） | 基本卡片 | `7ipso`(默认) |
| 基本卡片容器（可插入slot） | 卡片/基本卡片 | `YCOKr` `WLYWO` |
| 带图卡片 | 带图卡片 | `rKwK1`(默认) |

**子组件**: `.有图标标题` `AcYr4`/`hX9h2`/`jG3Sg`，`.无图标标题` `I1uwM`/`86i3l`，`.信息展示` `bzUgt`(图标on)/`znCAX`(图标off)

### 14. 头信息 Header

| 场景 | 推荐 ID |
|------|--------|
| 默认头信息 | `Xxf4j` |
| 带搜索的头信息 | `p1nGW`(2项) `psp7m`(3项) `b6iRO`(4项) |

### 15. 导航

#### 顶部导航栏

| 场景 | 推荐 ID |
|------|--------|
| 默认顶部导航栏 | `Rpv7B` |
| 占位顶部导航栏 | `qPAD7` |

#### 工具链专用侧边栏

| 场景 | 推荐 ID |
|------|--------|
| 展开状态 | `JGEqF` |
| 收起状态 | `BBmtw` |

一级菜单（展开态）按二级菜单数量选择: `QOgvs`(0个) `RkIsL`(2个) `prLam`(3个) `s8rZy`(4个) `430Og`(5个) `NmMfG`(6个)

#### 手风琴侧边导航

| 场景 | 推荐 ID |
|------|--------|
| 完整侧边栏 | `kyl45` |

### 16. 业务组件

| 场景 | 推荐 ID |
|------|--------|
| 左侧选择菜单卡片 | `6aBNN` |
| Banner卡片 | `wxO2j` |
| Banner（大横幅） | `lSc0M` |
| 公告卡片 | `3kAYs` |
| 活动卡片 | `ioZGG` |

### 17. 图标资源

| 类型 | frame ID | 说明 |
|------|----------|------|
| 操作图标 (16px) | `QY5Bx` | add/help/chevron-down/more/search/close/setting/filter |
| 字母图标 (48px) | `SYWnk` | A-Z 用于项目卡片标识 |
| 字母图标 (32px) | `HEF9Q` | A-Z 较小尺寸 |
| 2D 服务图标 (16px) | `c3mAv` | 服务树/变更列表/部署/测试/发布 |
| 质感图标 (24px) | `iIj5S` | 持续交付/仪表盘/软件设计/代码管理 |
| 顶部导航图标 (24px) | `wqMp8` | 服务/看板/项目/工作台/首页 |

---

## 典型页面布局模板

### 数据列表页

```
顶部导航栏 (devui:Rpv7B)
├── 侧边栏 (devui:JGEqF 或 devui:kyl45)
└── 主内容区
    ├── 头信息 (devui:Xxf4j) 或 面包屑 (devui:iLVzA)
    ├── 筛选/搜索区 (devui:8hidv + devui:X93Mt + 按钮)
    ├── 页签切换 (devui:hbi7t 或 devui:cee0f)
    ├── 数据表格 (devui:35iCd)
    └── 分页器 (devui:i5IDo)
```

### 表单页

```
头信息 (devui:Xxf4j)
└── 表单区域
    ├── 表单项-文本输入框 (devui:Laiht) × N
    ├── 表单项-下拉选择框 (devui:qw7Ux) × N
    ├── 复选框文本组合 (devui:f0TO6)
    └── 按钮组 (devui:RoYUx + devui:qTc8e)
```

### 卡片网格页

```
顶部导航栏 (devui:Rpv7B)
├── 侧边栏 (devui:JGEqF)
└── 主内容区
    ├── 头信息 (devui:Xxf4j)
    ├── 筛选/搜索区
    └── 卡片网格 (devui:LcKkl 或 devui:7ipso) × N
```

---

## 详细参考

- Design Token 变量表、组件 ID 速查见 [reference.md](reference.md)
- 规范文档见项目内 `designsystem/devUI/llms-full.txt`
