---
name: wbl-ppt-guoyi
description: 企业PPT制作专家。基于品牌粉设计系统，经素材验证→需求探询→大纲打磨→格式选择后，生成专业统一的 HTML演示文稿、PPTX，或二者同时交付。当用户说"做PPT"、"生成PPT"、"企业PPT"、"做汇报PPT"、"HTML PPT"、"做演示文稿"时触发。
version: 1.4.0
---

# 企业PPT制作专家 (wbl-ppt-guoyi)

> 品牌粉（`#CF2154`）演示文稿技能。设计取向：**极简、大留白、冷灰 + 一点粉、平面色块、左对齐**。

**核心管线**:
`素材验证 → 需求探询 → 大纲打磨 → 大纲落盘 → ⛔格式选择 → HTML生成 和/或 SVG→PPTX → 可编辑性验收`

**视觉基准**: `./references/gold-sample/guoyi-html-deck-v2.html`（**仅版式参考**，它不含 logo，不能当交付样张）
**设计系统**: `./references/design-system.md`（HTML/SVG/PPTX 共用，必读）
**HTML 执行**: `./references/html-executor.md`

---

## 一、模板注册表

| 模板ID | 显示名称 | 路径 | 主色 | 说明 |
|--------|----------|------|------|------|
| guoyi-fen | 品牌粉（默认） | `./templates/guoyi-fen/` | #CF2154 | SVG/PPTX 版式库 + logo.png |
| html-shell | HTML壳 | `./references/gold-sample/guoyi-html-deck-v2.html` | #CF2154 | HTML 演示文稿底座（金样即壳） |

未指定模板时默认 `guoyi-fen`；HTML 通道基于金样 CSS/结构。时间轴必须用 `.tl-wrap > .timeline`。

---

## 二、规则分级（先读这一节）

设计系统里的规则分三级，**按级别区别对待**——不要逐条硬套：

| 级别 | 含义 | 处理方式 |
|------|------|----------|
| **硬约束** | 违反会直接出错（乱码、LOGO 空白、文件打不开）或破坏品牌 | 必须遵守，无例外 |
| **设计原则** | 决定"好不好看"的判断依据 | 结合页面情况判断，允许合理偏离 |
| **参考区间** | 经验数值，不是标准答案 | 可偏离；偏离时在交付说明里讲一句理由 |

原则与参考区间冲突时，**以原则为准**。规则越少越准，别把页面管死。

### 硬约束清单（只有 10 条）

1. 禁用 Emoji（含 ✅❌⭐）
2. 画布固定 1280×720
3. PPTX 通道 SVG 禁用 `mask` / `<style>` / `class` / `foreignObject` / `symbol+use` / `textPath` / 动画脚本
4. LOGO 固定写 `<image href="../images/logo.png" x="1041" y="44" width="220" height="31"/>`，路径与坐标不得改
5. 字体族固定：微软雅黑 / Arial（数字）/ Consolas（URL、代码）
6. `#CF2154` 是唯一彩色，不得引入第二种彩色
7. 正文可读下限 13px；已知投屏场合 15px
8. SVG 中 `& < > "` 用 XML 实体
9. **交付物必须全原生可编辑**——文字一律是文本框、图形一律是形状/图表/表格；禁止把版式、表格、图表渲染成图片贴进页面（**唯一例外**：`logo.png` 与用户提供的照片/截图素材）
10. **禁止图片化导出**——不得用 `--only legacy`、`--svg-snapshot` 产出的 `_svg.pptx` 当交付物；导出后必须跑 `pptx_editability_check.py` 并拿到"通过"

### 核心设计原则（判断时用）

- **粉色是强调色，不是结构色**——拿掉页面所有粉色，结构还清楚吗？不清楚就说明用错位置
- **每页一个视觉锚点**——扫一眼，第一落点在哪
- **层级靠字号和明度对比**，不靠描边、底色、加粗堆强度
- **容器用填色分层，不用描边分层**——默认无边框、无阴影、无圆角
- **留白是设计手段**，页尾允许留白 15–25%
- **相邻页不要长得一样**——连续同骨架会显机械

详见 `design-system.md` 第 6 节。

---

## 三、内容执行纪律（流程，不放松）

1. **严格串行** — 大纲未确认前不生成成稿
2. **⛔ 阻塞点必须停止** — 素材验证、需求、结构、逐章、大纲定稿、**格式选择** 均需用户明确响应
3. **内容稳定优先** — 大纲阶段充分打磨；成稿阶段少改结构、多改版式
4. **一套设计系统** — 无论 HTML 还是 PPTX，都遵循 `design-system.md`
5. **异议必停** — 有疑问或更好方案时立即与用户确认
6. **口头优先** — 大纲对话阶段口头确认，确认后再落盘
7. **可编辑才算交付** — PPTX 未过 `pptx_editability_check.py`（结论"通过，全原生可编辑"）不算完成，不得交给用户

> 纪律只管"什么时候停"，不管"页面长什么样"。视觉判断交给设计原则。

---

## 四、交互流程

### 第一步：素材接收与验证

🚧 用户提供素材（文本/Word/PDF/URL/Markdown/PPTX/图片/对话均可）

| 用户提供 | 操作 |
|----------|------|
| PDF / DOCX / PPTX / URL / HTML | `python ./scripts/source_to_md.py <路径或URL>` |
| Markdown / 纯文本 / 对话 | 直接读取 |
| 图片 | Read 工具识别 |

#### ⛔ 解析验证（BLOCKING）

1. 列出全部资料与解析状态（成功/失败）
2. 任一份失败 → **立即停止**，说明原因与建议，等待补充
3. 全部通过 → 简述要点，进入第二步
4. 含统计数字时做交叉校验，异常主动指出

---

### 第二步：需求深度探询（BLOCKING）

一次性输出需求四问（标注推荐项），用户一次回答：

1. **核心目标**：工作汇报 / 方案宣讲 / 培训 / 获批 / 竞聘 / 学术 / 产品推介 / 路演 / 其他
2. **受众与演讲者**：角色、受众、谁来讲
3. **场景与时长**：场合、期望页数、时长、**是否现场投屏**（决定正文下限 13px 还是 15px）
4. **核心主旨**：一句话中心思想

有矛盾、更好方案或素材不足时 **立即停下确认**。

---

### 第三步：大纲概览（结构确认，口头）

输出：核心主旨、章节数、预估页数、每章一句话。
提示可用页型（见 `design-system.md` 第 8 节）。
用户确认结构后进入第四步。

---

### 第四步：逐章打磨（细节确认，口头）

按章分批（每轮 1–2 章）。每页写明：

- 类型（封面/目录/章节/内容/结尾）
- 核心内容（按信息组拆分，不按行数硬切）
- 展示建议（页型 + 组件）
- 是否配图

超过 12 页必须分章确认。全部确认后进入第五步。

---

### 第五步：完整大纲定稿（BLOCKING）

口头汇总完整逐页大纲 → 用户确认 → 进入第六步。

---

### 第六步：大纲落盘

输出目录：
- 用户指定路径；或
- 默认 `./output/<YYYY-MM-DD HH>/`

文件：`第一步：<PPT标题>-大纲内容.md`
（含目标受众、目的、场景、模板、逐页版式与要点）

**✅ 大纲文件已生成并请用户确认无误。**

---

### 第七步：⛔ 输出格式选择（BLOCKING）

大纲落盘确认后，**必须停下让用户选择成稿格式**，不得默认：

```
大纲已确认。请选择最终输出格式：

A. 仅 HTML     — 单文件演示文稿（侧栏目录+翻页+缩放），适合沟通预览
B. 仅 PPTX     — 品牌粉 SVG→PPTX，含 logo.png，适合正式汇报投屏
C. HTML + PPTX — 同时交付（推荐需要既沟通又汇报时）

请回复 A / B / C。
```

| 选择 | 下一步 |
|------|--------|
| A | 第八步-A HTML 通道 |
| B | 第八步-B SVG→PPTX 通道 |
| C | 先 A 再 B（或并行准备资源后依次交付） |

---

### 第八步-A：HTML 演示文稿生成

🚧 入口：格式选择为 A 或 C

**必读**：
1. `./references/design-system.md`
2. `./references/html-executor.md`
3. `./references/gold-sample/guoyi-html-deck-v2.html`

**执行要点**：

1. 以金样的 CSS 与翻页脚本为底座，**禁止另起配色体系**
2. 按大纲生成全部 `.slide`，更新侧栏 `tocData`
3. 页眉只放"左对齐标题"；**不要**加顶部粉线、方块品牌标、全宽分隔线
4. 容器用 `#F7F8FA` 色块，**不要**用白底 + 粉描边
5. HTML 品牌：几何标 + 文字品牌名；**不嵌入 logo.png**
6. 写入后请用户抽查封面 / 内容页 / 表格页 / 章节页 / 结尾
7. 输出：`第二步：<PPT标题>-演示文稿.html`

**HTML 自检**：见 `html-executor.md` 第 6 节。

---

### 第八步-B：SVG 逐页生成与 PPTX 导出

🚧 入口：格式选择为 B 或 C

#### B1. 项目初始化

```bash
python ./scripts/project_manager.py init <project_name> --format ppt169
```

复制骨架页模板与 LOGO（**模板目录与项目结构一一对应，原样复制即可**）：

```bash
# 1) 复制 LOGO（必须，否则每页 LOGO 空白）
cp templates/guoyi-fen/images/logo.png <project>/images/logo.png
# 2) 复制 4 个骨架页模板到 svg_output/（封面/目录/章节/结尾，内容页按需另写）
cp templates/guoyi-fen/svg_output/*.svg <project>/svg_output/
```

对应结构：

```
<project>/
  ├── images/logo.png       # 品牌 LOGO（仅此一处）
  ├── svg_output/*.svg      # 骨架页 + 内容页；LOGO 引用 ../images/logo.png
  └── svg_final/            # finalize_svg.py 产出，图片已转 base64
```

必读：`design-system.md`、`svg-tech.md`

#### B2. 逐页生成 SVG

- 每页生成前读取对应模板 SVG
- **SVG 手写**，禁止脚本批量生成页面内容
- 遵循品牌粉规范 + 设计系统组件语言
- LOGO：`<image href="../images/logo.png" x="1041" y="44" width="220" height="31"/>`，路径与坐标不得改
- 同样遵守硬约束（字体、唯一彩色、13px 下限、无 emoji）
- 每页自检通过后再写入；有预览条件则逐页确认

#### B3. 质量检查

```bash
python ./scripts/svg_quality_checker.py <project_path>
```

error 必须修复；warning 自行判断是否合理，不必强行消除。

#### B4. 导出 PPTX

```bash
python ./scripts/total_md_split.py <project_path>
python ./scripts/finalize_svg.py <project_path>
python ./scripts/svg_to_pptx.py <project_path> -s final
```

默认走 **native** 通道（SVG → 原生形状 + 原生文本框）。**禁止** `--only legacy`（整页渲染成图片）、**禁止**交付 `--svg-snapshot` 的 `_svg.pptx`。
表格/图表需要是真对象（可改数据）时加 `--native-objects`，此时输出名带 `_native_charts`。

组织输出：
- `第二步：<PPT标题>-SVG图片/`
- `第三步：<PPT标题>-最终成稿.pptx`

#### B5. 可编辑性验收（BLOCKING）

```bash
python ./scripts/pptx_editability_check.py "第三步：<PPT标题>-最终成稿.pptx"
```

必须拿到 `结论：通过，全原生可编辑`（退出码 0）。判定口径：

| 结果 | 含义 | 处理 |
|------|------|------|
| ERROR 单图占页面 ≥60% | 整页/整块被渲染成图片 | 回 B2 改成形状+文本重绘，不得交付 |
| ERROR 页面无文字且图片 ≥30% | 文字已被图片吞掉 | 同上 |
| ERROR 全文字数 <20 | 整册图片化（多半走了 legacy） | 重新用 native 导出 |
| WARN 图片占比偏高 | 可能是 logo + 满幅照片 | 判断照片是否仅作装饰；正文/数据不得在图里 |

再目检三项：每页 LOGO 未空白、文字可选中编辑、形状可拖动改色。任一不满足即回到 B2。

---

### 第八步-C：在已有 PPTX 上改稿

🚧 入口：已有做好的 deck，只需改数字 / 加页 / 删页 / 调版式

**不要从零重画**。先反向取源，页面的像素级一致由转换器保证：

```bash
python scripts/pptx_to_svg.py <现有.pptx> -o <输出目录> --inheritance-mode flat
```

再把 `svg/slide_NN.svg` 按目标页码命名放进 `svg_output/`，把图片 href 从 `../assets/imageN.png` 改为 `../images/xxx.png`，随后走第八步-B 的后处理与导出。

**动笔前的两个必查项**（详见 `references/svg-tech.md` §9）：

1. **先读演讲备注**——反向提取不含 notesSlide。备注里常写着"某个数字为什么和早期资料不一样"，那是刻意统一而非笔误。编号与页码不是 1:1，需通过 `ppt/slides/_rels/slideN.xml.rels` 确认。
2. **先看实际渲染再判断版式新旧**——同一份 deck 可能同时存在"新结构旧样式"与"旧结构新样式"两个分支，不要凭文件时间戳猜。

---

## 五、输出目录结构

```
<输出目录>/
  ├── 第一步：<标题>-大纲内容.md
  ├── 第二步：<标题>-演示文稿.html          # 选 A 或 C
  ├── 第二步：<标题>-SVG图片/               # 选 B 或 C
  └── 第三步：<标题>-最终成稿.pptx         # 选 B 或 C
```

---

## 六、版式速查

| 场景 | HTML 组件 | SVG 模板 |
|------|-----------|----------|
| 封面 | `cover-*` | `01_cover`（骨架模板） |
| 目录 | `toc-cards` | `02_toc`（骨架模板） |
| 章节+要点 | `chapter` | `03a_chapter`（骨架模板） |
| 结尾 | `ending` | `05_ending`（骨架模板） |
| **内容页**（无固化模板，按下列组件现场写） | | |
| 单栏要点 | `lead` + `bullets` | 左对齐标题 + 浅灰色块 |
| 双栏对比 | `two` + 对比色块 | 两个 548px 色块（x=80 / 652） |
| 三栏/四宫格 | `three` / `four` | 三栏 357px 或 2×2 色块 |
| 流程条 | `flow-lane` | 等宽色块横排 |
| 编号列表 | `steps`（大号粉色数字） | 40px 粉色数字独立成列 |
| 图标卡 | `icon-card`（`three` 变体） | 浅灰色块 + 真实品牌图标 |
| 表格 | `table`（零边框） | 零边框，表头 `#EEF0F3` |
| KPI 大数字 | `kpi-row` | 4 列浅灰卡，大号粉色数字 |
| 水平时间轴 | `tl-wrap` + `timeline` | `.tl-wrap > .timeline` |

完整页型与令牌见 `design-system.md`。

---

## 七、避坑指南

| # | 陷阱 | 处理 |
|---|------|------|
| 1 | 页面发"死板" | 多半是页头装饰重复 + 字号层级挤在一起。先拆装饰、再拉字阶 |
| 2 | 粉色到处铺 | 粉色只做强调。拿掉粉色测一测结构还清不清楚 |
| 3 | 白底 + 粉描边卡片 | 改成 `#F7F8FA` 色块分层，不要描边 |
| 4 | 表头粉底白字 | 改浅灰底 `#EEF0F3` + 深色字，表格去边框 |
| 5 | 字太小 | 正文不得低于 13px；投屏场合 15px。宁拆信息组不缩字 |
| 6 | 出现 emoji | 生成后全文检索删除 |
| 7 | PPTX LOGO 空白 | 复制 logo.png + 导出后再目检 |
| 8 | 每页骨架一样 | 相邻页换一种排法（P6） |
| 9 | HTML 另起一套样式 | 复用金样 CSS 与组件类名 |
| 10 | 跳过格式选择 | 大纲后必须问 A/B/C |
| 11 | 满宽粉色块 | 内容页禁止满宽 `#CF2154` 色块、禁止全出血顶线 |
| 12 | 整段正文变粗 | `<text>` 外层带 `font-weight="bold"` 会被内部未声明字重的 `<tspan>` 继承，导出后正文全粗。**字重只写在 `<tspan>` 上**（见 `svg-tech.md` §3） |
| 13 | 同类块间距各页不一 | 块内「标题→首行内容＝字号×2.2」「多行正文行距＝字号×1.65」「列表条目间距＝字号×2.0」，直接照用不逐页试数（见 `design-system.md` §7） |
| 14 | 小标题颜色各页不同 | 同层级小标题统一 `ink` 加粗；粉色只给序号、关键词与结语强调句。不要一页黑一页粉 |
| 15 | 色块下半部空一半 | 内容在块内**垂直居中**、下留白 ≤40px；内容不够先缩块高，不要靠加大字号硬撑 |
| 16 | 改已有 PPTX 时从零重画 | 先 `pptx_to_svg.py --inheritance-mode flat` 反向取源再改（见 `svg-tech.md` §9） |
| 17 | 改了不该改的数字 | 反向取源**拿不到演讲备注**，备注里常写着"为什么和早期资料不一样"。动任何数字或结论前先读 `notesSlide`（见 `svg-tech.md` §9） |
| 18 | 导出报写入失败 | 目标 .pptx 被预览器占用（`PermissionError` / `Device or resource busy`）；先关闭，或另存新文件名，不要覆盖写 |
| 19 | 交付后用户改不了字 | 版式/表格/图表被渲染成图片贴进页面。文字只能写 `<text>`，表格图表用形状或 `--native-objects` 真对象，导出后跑 `pptx_editability_check.py` 验收 |
| 20 | 拿到的是整页图片 | 走了 `--only legacy` 或把 `--svg-snapshot` 的 `_svg.pptx` 当交付物。只用默认 native 输出，`_svg.pptx` 仅作视觉比对 |
| 21 | 满幅照片盖住正文 | 照片只作背景装饰时必须留出文字区；正文、结论、数据一律不得只出现在图里 |

---

## 八、SVG 技术约束（PPTX 通道）

禁止：`mask`、`<style>`/`class`、`foreignObject`、`symbol+use`、`textPath`、动画/脚本。
一行 = 一个 `<text>`；内联 `<tspan>` 不带 `x`/`y`/`dy`。
字符：排版符号用 Unicode；`& < > "` 用 XML 实体。
`<image>` 只用于 LOGO 与照片素材；**正文、表格、图表一律不得用 `<image>` 承载**（导出后即不可编辑）。
**完整规范见 `references/svg-tech.md`**（本通道唯一技术文件）。

---

## 九、扩展新模板

流程：`参考源分析 → 简报 → 用户确认 → 生成 templates/<id>/ → design_spec → 质检 → register_template.py`
并更新本节模板注册表。

模板的视觉语言必须与 `design-system.md` 一致；新模板只换版式，不换令牌。

---

## 十、技能目录

```
wbl-ppt-guoyi/
├── SKILL.md
├── templates/
│   └── guoyi-fen/
│       ├── svg_output/     # 4 个骨架页模板（封面/目录/章节/结尾）
│       ├── images/logo.png # 品牌 LOGO（唯一源）
│       └── design_spec.md
├── scripts/                # source_to_md / svg_to_pptx / 质检 / pptx_editability_check
└── references/
    ├── design-system.md    # 统一设计系统（含规则分级）
    ├── svg-tech.md         # SVG 技术约束（PPTX 通道唯一技术规范）
    ├── html-executor.md    # HTML 通道执行规范
    └── gold-sample/
        └── guoyi-html-deck-v2.html   # 仅版式参考
```
