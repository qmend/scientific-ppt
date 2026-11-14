# scientific-ppt

[English](README.en.md)

## 是什么

`scientific-ppt` 是一个用论文、文档或题目生成科研与技术演示文稿的 Agent Skill。Agent 负责查阅材料、组织讲述和选择图件，Python 负责生成可编辑的 PowerPoint、自动分页和渲染检查。适用于组会、论文汇报和技术讲解。

## 效果图

下面是 **Codex 使用 `scientific-ppt` 制作的 16 页汇报《微服务重试风暴：尾延迟如何演变为过载》**。原创 Drawlib 图展示共享队列、重叠执行和多层重试，另有编号公式、可编辑表格，以及每种策略 30 次离散事件模拟的结果图。

[下载 PowerPoint 源文件](examples/retry-storm.pptx) · [查看全部 16 页预览](examples/previews/)

<table>
  <tr>
    <td width="50%"><img src="examples/previews/slide-001.png" alt="1 微服务重试风暴" width="100%"></td>
    <td width="50%"><img src="examples/previews/slide-002.png" alt="2 目录" width="100%"></td>
  </tr>
  <tr>
    <td width="50%"><img src="examples/previews/slide-003.png" alt="3 一次超时可以留下两份工作" width="100%"></td>
    <td width="50%"><img src="examples/previews/slide-004.png" alt="4 超时与重试形成过载反馈" width="100%"></td>
  </tr>
  <tr>
    <td width="50%"><img src="examples/previews/slide-005.png" alt="5 一次逻辑请求的两次执行" width="100%"></td>
    <td width="50%"><img src="examples/previews/slide-006.png" alt="6 重试属主决定调用放大上限" width="100%"></td>
  </tr>
  <tr>
    <td width="50%"><img src="examples/previews/slide-007.png" alt="7 调用次数与负载放大" width="100%"></td>
    <td width="50%"><img src="examples/previews/slide-008.png" alt="8 重试发出前的三个控制点" width="100%"></td>
  </tr>
  <tr>
    <td width="50%"><img src="examples/previews/slide-009.png" alt="9 离散事件模拟的共同条件" width="100%"></td>
    <td width="50%"><img src="examples/previews/slide-010.png" alt="10 三种策略的重试开关" width="100%"></td>
  </tr>
  <tr>
    <td width="50%"><img src="examples/previews/slide-011.png" alt="11 恢复处理速度后，积压仍可能增长" width="100%"></td>
    <td width="50%"><img src="examples/previews/slide-012.png" alt="12 持续过载下，不重试的按期成功率最高" width="100%"></td>
  </tr>
  <tr>
    <td width="50%"><img src="examples/previews/slide-013.png" alt="13 预算限制额外负载，恢复还取决于积压" width="100%"></td>
    <td width="50%"><img src="examples/previews/slide-014.png" alt="14 故障排查中的三组信号" width="100%"></td>
  </tr>
  <tr>
    <td width="50%"><img src="examples/previews/slide-015.png" alt="15 参考资料" width="100%"></td>
    <td width="50%"><img src="examples/previews/slide-016.png" alt="16 结束页" width="100%"></td>
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

以下以 Codex 用户级安装为例。Claude Code 用 `.claude/skills`，DeepSeek Harness 用 `.dsh/skills`，均作为 `Join-Path` 的第二个参数。项目专属安装时，在目标项目根目录运行，直接将 `$skillsDir` 设为上表对应的 `skills` 目录。

```powershell
$skillsDir = Join-Path $env:USERPROFILE '.agents/skills'
New-Item -ItemType Directory -Force -Path $skillsDir | Out-Null
git clone 'https://github.com/qmend/scientific-ppt.git' (Join-Path $skillsDir 'scientific-ppt')
Set-Location (Join-Path $skillsDir 'scientific-ppt')
powershell -NoProfile -File scripts/bootstrap.ps1
```

### Linux（Bash）

以下以 Codex 用户级安装为例。Claude Code 使用 `$HOME/.claude/skills`，DeepSeek Harness 使用 `$HOME/.dsh/skills`。项目专属安装时，从目标项目根目录运行，并使用上表的相对路径。

```bash
skills_dir="$HOME/.agents/skills"
mkdir -p "$skills_dir"
git clone 'https://github.com/qmend/scientific-ppt.git' "$skills_dir/scientific-ppt"
cd "$skills_dir/scientific-ppt"
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.lock
.venv/bin/python scripts/scientific_ppt.py doctor
```

初始化后，回到要制作 PPT 的项目，在对应 Agent 中调用 Skill，附上论文、数据或内容要求。

DeepSeek Harness 使用自定义 `DSH_HOME` 时，将用户级 Skill 放在该目录下的 `skills/scientific-ppt/`。DSH 也会扫描项目和用户的 `.agents/skills/`，因此已有的 Codex 安装可直接复用。初始化后，在 Harness 中打开目标项目，输入「使用 scientific-ppt，根据这篇论文制作汇报」。 [DeepSeek Harness Skill 文档](https://deepseek-harness.github.io/deepseek-harness/en/reference/subsystems/skills#local-discovery-priority)

## PPT 风格 · 经典学术课件风格

- 内置 4:3 PowerPoint 母版，为封面、正文和结束页统一浅色背景、酒红标题带与封尾细线。标题用黑体，正文用加粗宋体。蓝色和酒红色只用于少量有意义的关键词组。 [下载母版](assets/template.pptx)
- 常规汇报包含封面、竖排目录、独立参考文献页和结束页。图题在图下，表题在表上，公式编号靠右。
- 表头和数据单元格统一加粗。长表按逻辑分组分页，非末页占满正文区，续页重复表头，末页保留自然行高。
- 科研图先对齐分支、标签和端口。时间轴用长图，分层关系可用紧凑构图。独页长图和图注在正文区内整体上下居中。同一服务或数据在不同子图中可复用图标。 [科研图设计](references/figure_tools.md#先对齐再定图幅)

## 注意事项

- 实际渲染需要本机 PowerPoint 或 LibreOffice。缺少渲染器时仍可生成 PPTX，预览状态标为 `unverified`。端到端渲染已在 Windows 和 PowerPoint 上验证。
- PowerPoint 表格和原生图表可编辑。Drawlib 图作为整体插入，公式保留 LaTeX 源码。
- 建议检查每页预览，尤其是公式、箭头和续表。生成文件写入 `artifacts/`，仓库只跟踪 `examples/` 下明确选定的展示成品。 [视觉验收](references/visual_qa.md) · [测试记录](references/test_report.md)

## Skill 规则

- **虚拟环境**。项目的 Python 依赖安装在 `.venv/`，由 `requirements.lock` 锁定。
- **绘图库**。计算机架构图、流程图和 Pipeline 优先使用 Drawlib。数据图用 Matplotlib、领域绘图库或可编辑的 PowerPoint 原生图表。Drawlib 用 `requirements-drawlib.lock` 安装到独立环境。 [绘图选库](references/figure_tools.md)
- **PPT 依赖**。`python-pptx` 生成 PPTX，PowerPoint 或 LibreOffice 负责实际渲染。字体与渲染器由 `doctor` 检测。 [安装与依赖](references/installation.md)
- **执行流程**。Agent 按统一 JSON Schema 规划内容。生成器自动加载母版，按内容计算图文布局和分页，再逐页检查渲染结果。自定义画幅、背景色、主色或基础标题带高度时，生成器按指定参数绘制这些元素。可复现的测试输入在 `tests/fixtures/demo/`。 [SKILL.md](SKILL.md) · [页面 Schema](references/deck.schema.json)

代码采用 [MIT 许可证](LICENSE)。第三方内容见 [许可与第三方说明](THIRD_PARTY_NOTICES.md)。

## 更新日志

### 2026-11-14

- 更新展示成品为 16 页《微服务重试风暴》，附 PowerPoint 实际渲染的逐页预览。
- 补充固定首尾页、出处写入演讲者备注，以及科研图对齐与图幅选择规则。

### 2026-11-13

- 加入 4:3 PowerPoint 母版，生成时自动应用封面、正文和结束页版式。
- 保留自定义设计参数支持，长标题仍可按需扩展标题带高度。
- 更新 Windows 和 Linux 安装示例，克隆命令已填入实际仓库地址。
- 更新科研图工作流，复杂方法优先绘制分区、数据形态和反馈路径，操作步骤使用标准流程图。
