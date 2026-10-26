# wbl-skills

个人 Agent 技能源码。每个技能放在 `skills/` 下，目录名与该技能 `SKILL.md` 里的 `name` 一致。

安装时，把对应技能目录整个复制到当前 AI 应用的技能目录。

## 技能清单

| 技能名 | 名称 | 版本 | 说明 |
| --- | --- | --- | --- |
| wbl-note-extract | 核心内容抓取 | 3.0.0 | 从公开网页或文章链接提取核心要点，生成结构化 Markdown 笔记。 |

SkillHub 页面：https://skillhub.cn/skills/user_79141fa8/wbl-note-extract

## 安装 wbl-note-extract

把 `skills/wbl-note-extract` 复制到当前 AI 应用的技能目录，目录名保持 `wbl-note-extract`。例如 Cursor 使用 `~/.cursor/skills/wbl-note-extract`。

## 新增一个技能

1. 在 `skills/` 下新建目录，名字与新技能 `SKILL.md` 的 `name` 相同。
2. 只放入可安装源码：`SKILL.md`，以及实际用到的 `scripts/`、`references/`。
3. 在上面的技能清单补一行：技能名、中文名、版本、一句话说明。
4. 单独提交一次，说明里写技能名和版本号。
