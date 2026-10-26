# SVG 技术约束（PPTX 通道）

> 本文件是 PPTX 通道**唯一**的技术规范，替代原来 4 份英文通用文档。
> 品牌粉固定 1280×720、平面色块语言（无渐变、无阴影、无圆角），所以只保留实际用得到的约束。

---

## 1. XML 合法性（最高优先级）

SVG 是严格 XML，**一个字符错误就导致文件打不开、整份导出中断**。

| 类别 | 正确做法 | 禁止 |
|------|----------|------|
| 排版符号（— – © ® → · 全角标点） | 直接写 Unicode 字符，如 `—` `→` `·` | HTML 命名实体：`&mdash;` `&copy;` `&rarr;` `&nbsp;` `&bull;` |
| XML 保留字符 `& < > " '` | 只用 `&amp;` `&lt;` `&gt;` `&quot;` `&apos;` | 裸写：`R&D`、`误差 < 5%` |

例：`R&amp;D`、`误差 &lt; 5%`。

---

## 2. 禁用项（违反即丢元素）

| 禁用 | 说明 |
|------|------|
| `mask` | 遮罩——PPT 没有逐像素 alpha |
| `<style>` / `class` / 外部 CSS | 样式必须全部内联 |
| `<foreignObject>` | 嵌入外部内容 |
| `<symbol>` + `<use>` | 符号复用 |
| `textPath` | 路径文字 |
| `@font-face` | 自定义字体声明 |
| `<animate*>` / `<set>` / `<script>` | 动画与脚本 |
| `<iframe>` | 嵌入框架 |

**PPT 不认的写法与替代**：

| 禁用写法 | 替代写法 |
|----------|----------|
| `fill="rgba(255,255,255,0.1)"` | `fill="#FFFFFF" fill-opacity="0.1"` |
| `<g opacity="0.2">…</g>` | 给每个子元素单独设 `fill-opacity` / `stroke-opacity` |
| `<image opacity="0.3"/>` | 图片后叠一层半透明 `<rect>` 遮罩 |

**条件允许**：

- `marker-start` / `marker-end`（箭头）：`<marker>` 必须定义在 `<defs>` 内，`orient="auto"`，形状为三角 / 菱形 / 圆形，且 marker 的 `fill` 与线的 `stroke` 同色
- `<image>` 上的 `clip-path`：`<clipPath>` 定义在 `<defs>` 内、只含一个形状子元素；**非图片元素上禁用**

---

## 3. 文本规则（最容易踩）

**一行 = 一个 `<text>`。** 同一逻辑行即使混色、混粗细，也只用一个 `<text>` + 内联 `<tspan>`。多个相邻 `<text>` 在 PPT 里会变成多个独立文本框。

正确：

```xml
<text x="100" y="200" font-size="24" fill="#333333">
  实现<tspan fill="#CF2154" font-weight="bold">10倍</tspan>效率提升
</text>
```

错误（会拆成 3 个文本框）：

```xml
<text x="100" y="200" font-size="24" fill="#333333">实现</text>
<text x="160" y="200" font-size="24" fill="#CF2154" font-weight="bold">10倍</text>
<text x="240" y="200" font-size="24" fill="#333333">效率提升</text>
```

**内联 `<tspan>` 不得带 `x` / `y` / `dy`** —— 带这三个属性会被判定为"换行"，拆成独立文本框。`dx` 是安全的（字距微调，仍在行内）。

多行且逐行强调是允许的：换行 tspan（带 `x` + `dy`）里可以再嵌套内联 tspan：

```xml
<text x="80" y="190" font-size="18" fill="#333333">
  <tspan x="80" dy="0">完成率<tspan fill="#CF2154" font-weight="bold">98%</tspan>超预期</tspan>
  <tspan x="80" dy="35">成本降低<tspan fill="#CF2154" font-weight="bold">¥120万</tspan></tspan>
</text>
```

双栏排版请写**两个独立的 `<text>`**，不要靠 `<tspan x="600">` 跳列。

**关键信息加粗**：数字（百分比、倍数、金额）、对比（增/减、前/后）、每句 1–2 个承载洞察的名词，用 `<tspan fill="#CF2154" font-weight="bold">` 标出。
**不要标**：连接词、普通动词、句中每个名词、装饰形容词、页脚 / 页码 / 图表轴标签等结构文字。

### ⚠️ 字重只能写在 `<tspan>` 上，不能写在 `<text>` 上

`<text font-weight="bold">` 会被内部**未声明字重**的 `<tspan>` 继承。一旦出现这种写法，导出的 PPTX 里整段正文都会变粗——而 SVG 预览时往往看不出来。

```xml
<!-- 错：正文的"闲聊内容"会跟着变粗 -->
<text font-size="18" font-weight="bold">
  <tspan font-weight="bold">标题　</tspan><tspan>正文应保持常规，却继承了加粗</tspan>
</text>

<!-- 对：字重下移到每个该加粗的 tspan，<text> 不带 font-weight -->
<text font-size="18">
  <tspan font-weight="bold">标题　</tspan><tspan>正文保持常规</tspan>
</text>
```

**自查**：`<text>` 带 `font-weight="bold"` 但其内存在不带字重的 `<tspan>` → 中招。
**验收**：导出后用 python-pptx 按 run 的字号统计加粗占比，正文（≤15pt）加粗占比超过 60% 即异常。注意文本在**组合形状**里，遍历必须递归进 group。

---

## 4. 元素分组（必须）

相关元素用顶层 `<g id="...">` 包起来——导出后成为 PPT 的"组合"，便于选中 / 移动 / 编辑。

- 每个顶层语义组**必须有描述性 id**（`card-1`、`step-discover`、`header`、`footer`）
- 目标：每页 **3–8 个**顶层内容组
- 不要把整页塞进一个 `<g>`；也不要让大量 `<rect>` / `<text>` 裸在顶层
- 页面 chrome 组的 id 用固定词，便于识别：`bg` / `header` / `footer` / `watermark` / `pagenumber` / `logo` / `rule` / `decor`

**分组单元**：卡片 / 面板（底色块 + 图标 + 标题 + 正文）、流程步骤、列表项、图标+文字、页眉、页脚、装饰簇。

> 品牌粉用平面色块分层，卡片**不加阴影 filter**。

---

## 5. 常用效果写法

**虚线**（分隔、时间轴连接线）：

| `stroke-dasharray` | 用途 |
|---|---|
| `4,4` | 短划线，分隔线 |
| `2,2` | 点线，细虚线 |
| `8,4` | 长划线，时间轴 / 流程箭头 |

**旋转**：`transform="rotate(角度)"` 或 `rotate(角度, cx, cy)`，正角顺时针。支持 rect / circle / line / path / polygon / text 等所有元素。

**圆弧路径**（环形进度、饼图）：端点坐标**必须用三角函数精确计算**，不要估算。

```
x = cx + r × cos(θ × π / 180)
y = cy + r × sin(θ × π / 180)
```

规则：

1. 从 **-90°（12 点方向）** 起，顺时针走
2. 每扇区角度 = `百分比 × 360°`
3. 扇区 > 180° 时 large-arc flag = **1**，否则 **0**
4. 外弧 sweep = 1，回程内弧 sweep = 0
5. 校验：所有扇区角度和 = 360°，且末扇区终点 = 首扇区起点

例（75% 环形，圆心 400,400，外 r=180，内 r=100）：

```xml
<path d="M 400,220 A 180,180 0 1,1 220,400 L 300,400 A 100,100 0 1,0 400,300 Z"/>
```

**箭头**：连接线优先用 `marker-end`；粗大实心箭头用独立 `<polygon>`。**斜线上的三角箭头必须按方向向量旋转**，不能用固定朝下 / 朝右的三角（会指错方向）。

**图标**：用 `<use data-icon="<库>/<名称>" x="" y="" width="48" height="48" fill="#HEX"/>`，后处理自动嵌入。同一份 PPT 只用一种图标库。

---

## 6. 基本规则

- `viewBox` 必须等于画布尺寸（`0 0 1280 720`），它是画布尺寸的唯一权威
- 背景用 `<rect>`
- 字体族必须落在系统预装字体：**Microsoft YaHei**（中文，不要写中文名「微软雅黑」）/ **Arial**（数字）/ **Consolas**（URL、代码）
  - 从已有 PPTX 反向提取回来的 SVG 会带 `font-family="&quot;微软雅黑&quot;, sans-serif"`，**必须统一替换为 `Microsoft YaHei, sans-serif`**（同一字体，渲染不变，但中文名在部分渲染器里会走形或变方块）
- 颜色只用 HEX；透明度用 `fill-opacity` / `stroke-opacity`
- 图片：`<image href="../images/xxx.png" preserveAspectRatio="xMidYMid slice"/>`

---

## 7. 项目结构

```
<project>/
├── images/        # 图片资产（含 logo.png）
├── svg_output/    # 原始 SVG（外部引用，生成阶段）
├── svg_final/     # 后处理产物（图片已转 base64，导出用）
├── notes/         # 演讲备注（与 SVG 同名的 .md）
│   └── total.md   # 拆分前的完整备注
└── *.pptx         # 导出的 PPT
```

---

## 8. 后处理流水线（3 步，顺序不可乱）

```bash
python scripts/total_md_split.py <project_path>          # 1. 拆分演讲备注
python scripts/finalize_svg.py <project_path>            # 2. SVG 后处理（图片自动转 base64）
python scripts/svg_to_pptx.py <project_path> -s final    # 3. 导出 PPTX
```

生成阶段 SVG 里图片用外部引用 `../images/xxx.png`（便于快速迭代），`finalize_svg.py` 会自动转成 base64 写入 `svg_final/`，导出的 PPTX 不依赖外部文件。

**依赖**：`finalize_svg.py` 需要 Pillow，`svg_to_pptx.py` 需要 python-pptx。导入失败时先确认解释器环境，不要改脚本。导出建议加 `--only native`。

**已知无害报错**：`svg_to_pptx.py` 末段可能抛一条 `UnicodeDecodeError` 回溯，但前面已打印 `[Done] Saved`，产物正常，不必重跑。

**写入失败（最常见）**：目标 .pptx 若正在**预览器中打开**，写入会报 `PermissionError`，改名替换也会报 `Device or resource busy`。导出前先确认文件已关闭；无法关闭时先另存为新文件名，不要覆盖写。

---

## 9. 在已有 PPTX 上改稿（不要重建）

需要改一份已经做好的 deck（改数字、加页、删页、调版式）时，**不要从零重画**，先反向取源：

```bash
python scripts/pptx_to_svg.py <现有.pptx> -o <输出目录> --inheritance-mode flat
# 产物：<输出目录>/svg/slide_01.svg … slide_NN.svg
```

然后：把 `svg/slide_NN.svg` 按目标页码命名放进 `<project>/svg_output/`，把 href 里的 `../assets/imageN.png` 改为 `../images/xxx.png`（logo 用 `../images/logo.png`），再走第 8 节流水线重新导出。

> 这样出来的页面与原件像素级一致，只改需要改的地方，避免"改一份 deck 结果整份视觉都变了"。

**两个必查项**：

1. **反向提取只拿得到幻灯片上的文字，拿不到演讲备注。** 改任何数字或结论前，先读一遍备注——备注里常写着"为什么和早期资料不一样"。查看方式：
   ```bash
   unzip -p <现有.pptx> ppt/slides/_rels/slide4.xml.rels   # 看指向哪个 notesSlideM.xml
   unzip -p <现有.pptx> ppt/notesSlides/notesSlide1.xml    # 取出备注文字
   ```
   注意 notesSlide 的编号与页码**不是 1:1**，必须通过上述 rels 文件确认对应关系。
2. **对比两版差异时，不要只看文件时间戳**。同一份 deck 可能同时存在"新版结构 + 旧版样式"和"旧版结构 + 新版样式"两个分支。判断版式新旧要看实际渲染（`slidep screenshot`），不要凭时间猜。
