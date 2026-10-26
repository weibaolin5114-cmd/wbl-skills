# wbl-skills

个人 Agent 技能源码。每个技能一个目录，放在 `skills/` 下，目录名与该技能 `SKILL.md` 里的 `name` 一致。

## 技能清单

| 技能名 | 名称 | 版本 | 说明 |
| --- | --- | --- | --- |
| wbl-note-extract | 核心内容抓取 | 3.0.0 | 从公开网页或文章链接提取核心要点，生成结构化 Markdown 笔记。SkillHub：https://skillhub.cn/skills/user_79141fa8/wbl-note-extract |
| wbl-ppt-guoyi | 生成汇报PPT | 1.4.0 | 按品牌粉设计系统生成 HTML 演示文稿和 PPTX。仓库中的副本已去掉真实品牌标识和原始成稿。 |

## 只下载其中一个技能

仓库是公开的，克隆不需要登录。把下面命令里的 `wbl-note-extract` 换成技能清单中的技能名。

这台电脑的全局 Git 配置会把 GitHub 转到 `ghfast.top`，直连 `github.com` 又会被重置。克隆前在同一窗口先执行下面几行，只对当前窗口生效，不改全局配置：

```powershell
$tmp = Join-Path $env:TEMP "gitconfig-empty-wbl.txt"
Set-Content -Path $tmp -Value "" -Encoding ascii
$env:GIT_CONFIG_GLOBAL = $tmp
$env:HTTP_PROXY = "http://127.0.0.1:7892"
$env:HTTPS_PROXY = "http://127.0.0.1:7892"
```

然后下载指定技能：

```powershell
git clone --depth 1 --filter=blob:none --sparse https://github.com/weibaolin5114-cmd/wbl-skills.git
cd wbl-skills
git sparse-checkout set skills/wbl-note-extract
```

完成后，文件在 `wbl-skills\skills\wbl-note-extract`。把这个文件夹整个复制到当前 AI 应用的技能目录，文件夹名保持不变。

| 应用 | 技能目录 |
| --- | --- |
| Cursor | `%USERPROFILE%\.cursor\skills\` |
| WorkBuddy | `%USERPROFILE%\.workbuddy\skills\` |

复制后新开一轮对话，该技能即可被触发。

## 新增一个技能

1. 在 `skills/` 下新建目录，名字与新技能 `SKILL.md` 的 `name` 相同。
2. 只放入可安装源码：`SKILL.md`，以及实际用到的 `scripts/`、`references/`、`templates/`。
3. 在技能清单补一行：技能名、中文名、版本、一句话说明。
4. 单独提交一次，说明里写技能名和版本号。
