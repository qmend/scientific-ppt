# scientific-ppt

[English](README.en.md)

## 是什么

`scientific-ppt` 是一个用论文、文档或题目生成科研与技术演示文稿的 Agent Skill。Agent 负责查阅材料、组织讲述和选择图件，Python 负责生成可编辑的 PowerPoint、自动分页和渲染检查。适用于组会、论文汇报和技术讲解。

## 效果图

下面是 **Codex 调用 `scientific-ppt` 制作的 30 页 Mamba 架构汇报**。这份成品展示 Codex 在该 Skill 下的实际表现，包含 Drawlib 架构图、实验图表、编号公式和自动分页的原生表格。

[下载 PowerPoint 源文件](examples/mamba-architecture.pptx) · [查看全部 30 页预览](examples/previews/)

<table>
  <tr>
    <td><img src="examples/previews/slide-001.png" alt="1 封面" width="50%"></td>
    <td><img src="examples/previews/slide-002.png" alt="2 目录" width="50%"></td>
  </tr>
  <tr>
    <td><img src="examples/previews/slide-003.png" alt="3 长序列中的状态与记忆" width="50%"></td>
    <td><img src="examples/previews/slide-004.png" alt="4 选择性复制任务" width="50%"></td>
  </tr>
  <tr>
    <td><img src="examples/previews/slide-027.png" alt="27 语言任务与部署评估" width="50%"></td>
    <td><img src="examples/previews/slide-028.png" alt="28 三个核心机制" width="50%"></td>
  </tr>
  <tr>
    <td><img src="examples/previews/slide-029.png" alt="29 参考文献" width="50%"></td>
    <td><img src="examples/previews/slide-030.png" alt="30 结束页" width="50%"></td>
  </tr>
</table>

## 部署步骤

### 选择 Agent 和安装范围

需要 Git、Python 3.11+，以及已安装的 Codex、Claude Code 或 DeepSeek Harness。把整个仓库克隆到选定目录，确保 `SKILL.md` 位于 `scientific-ppt/` 下。

| Agent | 当前用户的所有项目 | 仅当前项目 | 调用 |
| --- | --- | --- | --- |
| OpenAI Codex | `~/.agents/skills/scientific-ppt/` | `.agents/skills/scientific-ppt/` | `$scientific-ppt` |
| Claude Code | `~/.claude/skills/scientific-ppt/` | `.claude/skills/scientific-ppt/` | `/scientific-ppt` |
| DeepSeek Harness（DSH） | `~/.dsh/skills/scientific-ppt/` | `.dsh/skills/scientific-ppt/` | 在对话里要求使用 `scientific-ppt` |

项目路径相对于目标项目根目录。Windows 的 `~` 对应 `%USERPROFILE%`。 [Codex 官方文档](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills) · [Claude Code 官方文档](https://code.claude.com/docs/en/skills)

### Windows（PowerShell）

将仓库 URL 换成实际地址。以下以 Codex 用户级安装为例。Claude Code 用 `.claude/skills`，DeepSeek Harness 用 `.dsh/skills`，均作为 `Join-Path` 的第二个参数。项目专属安装时，在目标项目根目录运行，直接将 `$skillsDir` 设为上表对应的 `skills` 目录。

```powershell
$skillsDir = Join-Path $env:USERPROFILE '.agents/skills'
New-Item -ItemType Directory -Force -Path $skillsDir | Out-Null
git clone '<仓库 URL>' (Join-Path $skillsDir 'scientific-ppt')
Set-Location (Join-Path $skillsDir 'scientific-ppt')
powershell -NoProfile -File scripts/bootstrap.ps1
```

### Linux（Bash）

以下以 Codex 用户级安装为例。Claude Code 使用 `$HOME/.claude/skills`，DeepSeek Harness 使用 `$HOME/.dsh/skills`。项目专属安装时，从目标项目根目录运行，并使用上表的相对路径。

```bash
skills_dir="$HOME/.agents/skills"
mkdir -p "$skills_dir"
git clone '<仓库 URL>' "$skills_dir/scientific-ppt"
cd "$skills_dir/scientific-ppt"
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.lock
.venv/bin/python scripts/scientific_ppt.py doctor
```

初始化后，回到要制作 PPT 的项目，在对应 Agent 中调用 Skill，附上论文、数据或内容要求。

DeepSeek Harness 使用自定义 `DSH_HOME` 时，将用户级 Skill 放在该目录下的 `skills/scientific-ppt/`。DSH 也会扫描项目和用户的 `.agents/skills/`，因此已有的 Codex 安装可直接复用。初始化后，在 Harness 中打开目标项目，输入「使用 scientific-ppt，根据这篇论文制作汇报」。 [DeepSeek Harness Skill 文档](https://deepseek-harness.github.io/deepseek-harness/en/reference/subsystems/skills#local-discovery-priority)

## PPT 风格 · 经典学术课件风格

- 默认 4:3，酒红标题带、黑体标题、浅色背景、加粗宋体正文。蓝色和酒红色只用于少量有意义的关键词组。
- 常规汇报包含封面、竖排目录、独立参考文献页和结束页。图题在图下，表题在表上，公式编号靠右。
- 表头和数据单元格统一加粗。长表按逻辑分组分页，非末页占满正文区，续页重复表头，末页保留自然行高。
- 架构图和流程图使用白底节点，并为每个节点配同风格图标。 [参考风格分析](references/style_guide.md)

## 注意事项

- 实际渲染需要本机 PowerPoint 或 LibreOffice。缺少渲染器时仍可生成 PPTX，预览状态标为 `unverified`。端到端渲染已在 Windows 和 PowerPoint 上验证。
- PowerPoint 表格和原生图表可编辑。Drawlib 图作为整体插入，公式保留 LaTeX 源码。
- 建议检查每页预览，尤其是公式、箭头和续表。生成文件写入 `artifacts/`，仓库只跟踪 `examples/` 下明确选定的展示成品。 [视觉验收](references/visual_qa.md) · [测试记录](references/test_report.md)

## Skill 规则

- **虚拟环境**。项目的 Python 依赖安装在 `.venv/`，由 `requirements.lock` 锁定。
- **绘图库**。计算机架构图、流程图和 Pipeline 优先使用 Drawlib。数据图用 Matplotlib、领域绘图库或可编辑的 PowerPoint 原生图表。Drawlib 用 `requirements-drawlib.lock` 安装到独立环境。 [绘图选库](references/figure_tools.md)
- **PPT 依赖**。`python-pptx` 生成 PPTX，PowerPoint 或 LibreOffice 负责实际渲染。字体与渲染器由 `doctor` 检测。 [安装与依赖](references/installation.md)
- **执行流程**。Agent 按统一 JSON Schema 规划内容，生成 PPTX 后逐页检查。可复现的测试输入在 `tests/fixtures/demo/`。 [SKILL.md](SKILL.md) · [页面 Schema](references/deck.schema.json)

代码采用 [MIT 许可证](LICENSE)。第三方内容见 [许可与第三方说明](THIRD_PARTY_NOTICES.md)。
