# scientific-ppt

[中文说明](README.md)

An Agent Skill for reference-informed academic and technical PowerPoint authoring. The Agent reads evidence and plans the narrative; a modular Python engine validates JSON, measures content, chooses layouts, draws editable objects, paginates tables and checks actual slide renders.

The default design language was derived from **448 slides across five reference decks**: 4:3 canvas, wine-red header, pale background and serif Chinese typography. No discipline-specific content is embedded in the engine.

## Setup and run

Use Python 3.11+ and the repository-local virtual environment:

```bash
python -m venv .venv
# Windows uses .venv/Scripts/python instead
.venv/bin/python -m pip install -r requirements.lock
.venv/bin/python scripts/scientific_ppt.py doctor
.venv/bin/python scripts/scientific_ppt.py build examples/demo.json --output artifacts/my-demo --strict
.venv/bin/python -m pytest
```

See [installation](references/installation.md) for optional Office support and lock-file scope. PowerPoint or LibreOffice is required for actual PPT rendering, but neither is required to generate an editable PPTX. No draw.io, TeX distribution, model API key or Node runtime is required.

Copy the complete Skill source directory into your Agent's skills directory as `scientific-ppt`. Install the locked dependencies and run `scripts/scientific_ppt.py` directly. `SKILL.md` defines the Agent workflow, and `references/` contains the detailed specifications.

## Outputs

- The demo command above generates a PPTX, PDF, slide previews, and a QA report in the local `artifacts/my-demo/` directory. Git ignores the entire `artifacts/` directory.
- Native editable text, graph nodes, connectors, tables and bar/line charts with embedded workbooks.
- Mixed aspect-ratio image layouts, EXIF orientation and bounded crop policies.
- LaTeX matrices, sums, integrals, cases and scripts, retaining `.tex`, MathML, SVG and high-resolution PNG.
- Lossless text pagination and table pagination with repeated headers, stable row IDs and contiguous group preservation.
- Bounded repair loops, PowerPoint text measurements and explicit unverified status when no renderer is available.

All demo data are synthetic. `plan` converts an existing Markdown outline deterministically; semantic summarization, source research and topic expansion remain the Agent's responsibility.

## Documentation

[Style evidence](references/style_guide.md) · [Architecture](references/architecture.md) · [Schema](references/deck.schema.json) · [Schema usage](references/schema_usage.md) · [Visual QA](references/visual_qa.md) · [Executed tests and limitations](references/test_report.md)

Detailed reference specifications are currently in Chinese; commands, JSON and Python APIs are language-independent.

## Limits and licensing

Automated geometry checks cannot certify scientific accuracy or visual quality. Inspect every rendered page. Equations are inserted as images, not native Office equation objects; editable LaTeX/SVG sources are retained. Complex graph routing needs review. Oversized rows, overly narrow table columns and dense diagrams fail explicitly instead of losing data or endlessly shrinking text.

Fonts are not bundled. Cross-platform substitutions can change appearance. Real integration testing in this repository uses Windows, Python 3.11 and PowerPoint 2013; LibreOffice support is separately documented and must not be described as tested unless exercised.

Code is [MIT licensed](LICENSE). Reference slides and third-party artwork are not relicensed. See [third-party notices](THIRD_PARTY_NOTICES.md). The virtual environment, reference conversion artifacts and temporary build attempts are ignored by Git. No GitHub upload is performed.
