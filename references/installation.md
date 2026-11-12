# 环境初始化和复现

支持Python 3.11及以上。首次安装在项目根目录创建`.venv`，所有pip命令使用该解释器。不要复制其他机器的.venv。

Windows可以直接运行`powershell -NoProfile -File scripts/bootstrap.ps1`。Linux/macOS：

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.lock
.venv/bin/python scripts/scientific_ppt.py doctor
```

`requirements.lock`记录 Skill 运行、测试与示例绘图所需的精确依赖版本。安装这些依赖后直接执行源码脚本。`pyproject.toml`用于配置 pytest。

锁定版本已在 Python 3.11 和 Windows 上验证。`pywin32` 与 `colorama` 通过平台条件仅在 Windows 上安装。更新依赖时，在独立虚拟环境中检查新版本及其传递依赖，再更新锁文件并运行 `pip check` 和 pytest。

本机官方PyPI下载站出现TLS失败，开发安装使用清华PyPI镜像。锁文件不嵌入镜像地址，用户可使用默认索引或通过`--index-url`选择可信镜像；不关闭TLS校验。

## 可选渲染器

- Windows PowerPoint：使用本机 PowerPoint 和锁文件中的 pywin32。`doctor`检查 COM 注册，实际启动失败会进入报告。
- LibreOffice：安装后确保`soffice`或`libreoffice`在PATH，或设置`SCIENTIFIC_PPT_SOFFICE`为可执行文件绝对路径。支持无GUI的headless导出，每次使用隔离profile。
- 两者均无：仍可生成PPTX，状态为unverified。`--no-render`显式跳过渲染；`--strict`会返回非零。不会自动下载安装Office或改系统设置。

## 字体

默认中文SimSun、西文Times New Roman。Windows检测Fonts目录；Linux/macOS尝试`fc-match`。可用`SCIENTIFIC_PPT_FONT_PATH`指定合法TTF/TTC文件，但其字体族名称仍应在自定义tokens中同步设定。项目不分发商业字体。

## 可选绘图库

根据[图件用途](figure_tools.md)启用对应工具。Drawlib 默认用于计算机示意图，作为独立绘图环境运行。以下命令在仓库根目录执行：

```powershell
.venv/Scripts/python -m venv .cache/drawlib-preview-venv
.cache/drawlib-preview-venv/Scripts/python -m pip install -r requirements-drawlib.lock
.cache/drawlib-preview-venv/Scripts/python -m pip check
.cache/drawlib-preview-venv/Scripts/python scripts/make_drawlib_chatgpt_architecture.py
```

首次使用 Phosphor 图标时，Drawlib 会从其官方 GitHub Release 下载资源到本地缓存。示例输出位于 `artifacts/drawlib-chatgpt/`。在其它平台可切换为 `bin/python` 并通过 `--font` 和 `--bold-font` 提供本地中文字体路径。

## 目录与清理

用户输出指定在`--output`目录。每轮尝试在`attempt-N/`，最终PPTX、PDF、previews和qa_report在输出根目录；不要把旧attempt当作最终结果。参考转换保存在被忽略的`artifacts/reference-analysis/`。

发布内容包括锁文件、pyproject、SKILL、src、scripts、references、tests 和 examples。`artifacts/` 是 Git 忽略的本地生成目录。源代码仓库无外部下载的字体、参考图片和教材副本。
