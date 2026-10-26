# HTML PPT 执行规范（品牌粉）

生成 HTML 演示文稿时必读。视觉以金样与设计系统为准。

**必读**：
1. `./design-system.md`
2. `./gold-sample/guoyi-html-deck-v2.html`（结构/CSS/组件金样）
3. 已确认的大纲 Markdown

---

## 1. 输出物

单文件 HTML：

```
<输出目录>/
  ├── 第一步：<标题>-大纲内容.md
  └── 第二步：<标题>-演示文稿.html
```

若同时选 PPTX，HTML 与 SVG/PPTX 流程并行交付，文件命名：

- HTML：`第二步：<标题>-演示文稿.html`
- SVG 目录：`第二步：<标题>-SVG图片/`
- PPTX：`第三步：<标题>-最终成稿.pptx`

---

## 2. 生成策略

1. **先复制金样壳**：以 `guoyi-html-deck-v2.html` 的 `<style>`、侧栏、`#stage` 缩放、翻页脚本为底座，不要另起一套 CSS。
2. **按大纲替换页面**：只改 `#stage` 内 `.slide` 与侧栏 `tocData`，不改设计令牌。
3. **组件化填内容**：页内结构优先用组件类名（见第 4 节）。
4. **可一次写入完整 HTML**（比 SVG 更稳），写入后打开预览，请用户抽查关键页。
5. 用户指出某页问题时，**只改该页 DOM**，不重写全文件样式。

---

## 3. HTML 壳必备能力

| 能力 | 要求 |
|------|------|
| 画布 | `#stage` 固定 1280×720，`fitStage()` 按窗口 scale |
| 侧栏 | 品牌 + 版本 chip + 目录点击跳转 |
| 翻页 | 左右箭头、键盘、触摸滑动 |
| 进度条 | 底部主色进度 |
| 页码 | 仅幻灯内 `.page-foot` 右下角，13px `#6B7280`，不加横线 |

---

## 4. 页型 HTML 骨架

### 内容页

```html
<div class="slide" data-page="N">
  <div class="page-head">
    <div class="page-title">页面标题</div>
  </div>
  <div class="content">
    <!-- eyebrow / lead / two / three / table ... -->
  </div>
  <div class="page-foot"><span>NN / TT</span></div>
</div>
```

**页头只有标题。** 不要写 `.top-bar`、`.mark`、`.part-chip`、全宽分隔线——这些是"死板感"的主要来源。

### 章节页

```html
<div class="slide" data-page="N">
  <div class="chapter">
    <div class="chapter-label">PART 0X</div>
    <div class="chapter-title">章节标题</div>
    <div class="chapter-line"></div>
    <ul class="chapter-points">
      <li><span class="i">1</span>要点一</li>
      <li><span class="i">2</span>要点二</li>
    </ul>
    <div class="chapter-num">0X</div>
  </div>
</div>
```

`.chapter-num` 是 160px 极浅粉水印数字，**每个章节页都要有**。

### 封面 / 结尾

封面：`cover-deco-bar` + `cover-blob` + `cover-blob-2` + `cover-body`（brand → title → sub → line）+ `cover-meta`
结尾：`ending`（p 行动句 → h1 结语 → line → brand）

两页都左对齐，不加顶部装饰条。

---

## 5. 组件类名对照

| 用途 | 类名 | 说明 |
|------|------|------|
| 结论条 | `.lead` + `.tag` | `#F7F8FA` 底 + 深色正文 + `.num` 粉色关键词 |
| 副标题 | `.eyebrow` | 13–14px `#6B7280` |
| 双栏 / 三栏 / 四宫格 | `.two` / `.three` / `.four` | 内部用 `.panel` |
| 面板 | `.panel` + `.panel-h` + `.panel-h .badge` | `#F7F8FA` 底，无边框无圆角；badge 是粉色数字 |
| 表格 | `.table` + `.hl` | 零边框；表头 `#EEF0F3` 底深字；隔行填色 |
| 列表 | `.bullets` / `.bullets.lg` | • 用 `#6B7280` |
| 编号列表 | `.steps` + `.meta` | 序号是大号粉色数字（30px），独立成列 |
| 流程条 | `.flow` + `.flow-lane` + `.node`（`.accent` / `.final`） | 等宽色块横排 |
| 角色卡 | `.role-grid` + `.role-card` | |
| 阶段卡 | `.phase` + `.phase-top` + `.phase-goal` + `.phase-pass` | |
| 时限速查 | `.sla-grid` + `.sla-box` + `.sla-line` | |
| 时间轴 | `.tl-wrap` > `.timeline` + `.tl-item` | 见 5.1 |
| KPI | `.kpi-row` + `.kpi` | |
| 数字强调 | `.num` | 粉色加粗，**内联在句子里** |
| URL / 代码 | `.mono` | Consolas 13px |

需要组件库之外的结构时，按"色块 + 左右对齐 + 5 档字阶"的原则自己搭即可，不加边框和阴影。

### 5.1 水平时间轴（已知坑，强制结构）

```html
<div class="tl-wrap">
  <div class="timeline">
    <div class="tl-item">
      <div class="tl-dot"></div>
      <div class="tl-name">阶段名</div>
      <div class="tl-desc">要点1<br>要点2</div>
    </div>
    <!-- 2–4 列 -->
  </div>
</div>
```

| 正确 | 错误 |
|------|------|
| 外层 `.tl-wrap` 负责垂直居中 | 给 `.timeline` 写 `style="flex:1;align-content:center"` |
| `::before` 用 `top:5px; left/right:12.5%` 穿圆点 | `top:20px` 等固定猜值，线悬空成双线框 |
| 圆点 `z-index:1` 压在线上 | 连接线盖住圆点 |

连接线颜色用 `#E3E6EB`（灰），圆点用主色——粉色只落在圆点上。

---

## 6. 排版规则（分级，不要硬套）

完整清单见 `design-system.md`。执行时记住：

**硬约束（必须满足）**
- 正文 ≥13px；已知投屏场合 ≥15px
- 字体族：微软雅黑 / Arial / Consolas
- 只有 `#CF2154` 一种彩色
- 无 emoji

**判断依据（按页面情况用）**
- 字阶层级要拉得开，不要把 15/16/17px 堆在一起
- 容器用填色分层，不用描边
- 每页一个视觉锚点
- 相邻页不要同骨架
- 文字块按信息组拆分

**参考区间（没想法时的起点）**
- 左右边距 80px，内容宽 1120px
- 色块内边距 14–20px，块间距 12–16px
- 页尾留白 15–25%

---

## 7. 自检（写入后）

硬约束：

- [ ] 无 emoji
- [ ] 正文字号 ≥13px（投屏 ≥15px）
- [ ] 只有 `#CF2154` 一种彩色
- [ ] 无 `.top-bar` / `.mark` / `.part-chip` 残留

观感三问：

- [ ] 一眼能找到视觉锚点
- [ ] 把粉色全部拿掉，页面结构依然清楚
- [ ] 字号层级拉得开

其他：

- [ ] CSS 来自金样，未另起配色
- [ ] 页脚页码总数正确，`tocData` 与页一一对应
- [ ] 双栏等高
- [ ] 每个章节页都有 160px 水印数字
- [ ] 若有时间轴：连接线穿过圆点，结构为 `.tl-wrap > .timeline`
- [ ] 浏览器打开无裁切、无横向滚动
