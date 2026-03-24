# Pencil .pen 设计常见错误（精炼）

> 用于指引模型在 DevUI + Pencil 设计稿中少犯同类错误。

---

## 组件文案填充（总则）

**组件库中的组件是占位内容**：顶栏、侧栏、面包屑、页签、表格、卡片等自带「一级菜单」「页签一」「编号」「标题」等占位文案。用 ref 引用后**必须**按业务需求替换为实际文案，否则设计稿语义不完整、无法交付。  
**正确做法**：在插入时用 `descendants` 一次性填齐该组件内所有需展示的文本节点（先用 `batch_get(..., resolveInstances=true)` 获取文本节点 ID）。**多文案组件**（顶栏、侧栏、头信息、表格）最容易漏填，必须当次插入就带齐 descendants，不得只填部分或依赖事后 `U()` 补文案。

---

## 1. 组件优先，勿手搭

- **错**：用 `frame` + `text` 手搭顶栏、侧栏、表格整块。
- **对**：优先用组件库 ref（如 `devui:Uexy2` 顶栏、`devui:E36oP` 侧栏、`devui:8K8z3` 表格），用 `descendants` 或 `U(实例ID/devui:子节点ID, {content: "..."})` 改文案。
- **原因**：用户明确要求「用组件」时，手搭会导致风格不统一、难维护。

---

## 2. batch_design 里 parent 必须用字符串 ID

- **错**：`I(d8wyB, {...})` 或 `I(screen, {...})` 且 screen 来自上一批（binding 已失效）。
- **对**：parent 用**节点 ID 字符串**，如 `I("d8wyB", {...})`、`I("CCNh0", {...})`。
- **现象**：`binding variable xxx not found`。

---

## 3. text 节点不能设 padding

- **错**：`I(leftNav, {type:"text", content:"任务列表", padding:[20,24,8,24]})`。
- **对**：text 不写 `padding`；需要留白时用外层 `frame` 包一层并给 frame 设 `padding`。
- **现象**：`Invalid properties: padding unexpected property`。

---

## 4. 用 ref 后必须填占位文案（组件文案填充）

- **介绍**：组件库中的顶栏、侧栏、面包屑、页签、表格、卡片等自带的是占位文案（如「一级菜单」「二级菜单」「编号」「标题」）。这些文案**必须**按页面业务替换为实际内容，否则设计稿无法表达真实界面语义，且侧栏/顶栏等多文案组件一旦漏填会整块保留占位。
- **错**：插入顶栏/侧栏/表格后不改文案，保留「一级菜单」「二级菜单」「编号」「标题」等默认占位；或只改顶栏、不改侧栏。
- **对**：在**插入时**用 `I(..., { ref, descendants: { "devui:文本节点ID": { content: "业务文案" }, ... } })` 一次性填齐该组件内所有菜单项、表头、关键单元格等文案。多文案组件（顶栏、侧栏、头信息、表格）必须当次就带齐 descendants。
- **原因**：组件库是占位内容，不填则页面语义不完整；事后用 `U(实例ID/devui:文本节点ID)` 会污染组件定义，故应以 descendants 在插入时填齐。

---

## 5. 更新实例用「实例ID/devui:子节点ID」

- **对**：`U("RM44s/devui:3tONU", {content:"控制台"})`。
- **注意**：`U()` 会改到组件定义（devui:xxx），同文件内所有该 ref 实例会一起变；若需不同文案需用不同组件或 Copy 后改 descendants。

---

## 6. 改 .pen 磁盘文件后要 reload

- **场景**：在 .pen 顶层 JSON 里加了 `imports`（如引入 devUI2.pen）。
- **对**：改完后调用 `user-pen-component-copy` 的 `reloadfile(file_path="绝对路径")`，再 `get_editor_state` 验证 Reusable Components 是否出现 `devui:xxx`。

---

## 7. 组件尺寸「还原」的代价

- **现象**：把 width/height 改成 `fit_content` 后，表格/卡片等 ref 可能报 circular layout 或 fit_content 无 flex 的警告。
- **建议**：能接受就保留；要完全还原可查组件库该组件的默认宽高，设回具体数值。

---

## 8. batch_design 单次 ≤25 个操作

- **对**：按区块拆分多轮调用（如先框架，再顶栏，再表格行），每轮 ≤25 个操作。
- **原因**：超量易失败或回滚。

---

## 9. Copy 的 descendants 在 C() 里写，不要事后 U() 子节点

- **错**：`C("devui:xxx", parent, {})` 后再 `U(新实例ID/devui:子ID, {...})`，子节点 ID 已变会失败。
- **对**：在 `C("devui:xxx", parent, {descendants: {"子节点ID或路径": {content: "..."}}})` 里一次写齐，或 Copy 后用**新实例下解析出的路径**再 U()。

---

## 10. 表头/列语义要跟业务一致

- **错**：用 8K8z3 后不改表头，仍显示「编号」「标题」「结束时间」「状态」等。
- **对**：查表头 text 节点 ID，用 `U(表格实例ID/devui:xxx, {content: "代码仓"})` 等改成业务列名；不需要的列可 `width:0` 隐藏。
