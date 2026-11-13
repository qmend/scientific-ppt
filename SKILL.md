---
name: scientific-ppt
description: Generate editable research, academic and technical PowerPoint presentations from topics, papers or documents, using reference-informed design tokens, content-aware layouts, scientific diagrams, LaTeX, lossless table pagination and rendered visual review.
---

# scientific-ppt

Create a coherent presentation from the user's evidence and purpose. This Skill combines **Agent semantic planning** with a deterministic Python execution engine. A topic alone requires researched or user-provided facts; the CLI does not invent a lecture or summarize a paper intelligently by itself.

## Workflow

1. Read [the style guide](references/style_guide.md) and [content planning](references/planning.md). Establish audience, purpose, source provenance and uncertainty from the request. Infer routine choices. The default 4:3 style uses a pale background, burgundy title band and Chinese serif body text. The bundled [PowerPoint master](assets/template.pptx) provides cover, content and closing layouts. Plan the content and slide geometry for the specific deck.
2. Read the source material, including figures and tables. Use `extract` for a text aid; PDF/DOCX extraction does not recover figure semantics or complex tables. For a new reference deck, render **all** slides and inspect structure before changing tokens; follow [reference analysis](references/reference_analysis.md).
3. Write a deck JSON matching [the schema](references/deck.schema.json), following [schema usage](references/schema_usage.md). Plan the narrative and select evidence, figures, editable graphs and tables. Preserve data, units, original LaTeX and sources. Allow page count to increase for readability. When diagrams are too dense, create an overview plus detail slides.
   Include a cover, vertical agenda list and closing page. Set bottom-right page numbers to 18 pt and omit them on the first and last slides. Arrange cover details in a narrow, centered, transparent table with no borders and left-aligned values. Use xxx for missing presenter details. On the cover and closing pages, place the thin header rule just below the centered English text. Place references on a dedicated page. Start references and prose directly below their title bars. Develop prose with a concrete example or explanation where the topic needs it.
   Keep topics on separate pages. Set all table cells in bold, including data rows. For multipage tables, fill the available content height on every page that has a continuation. Use natural row heights on the final page and on single-page tables. Repeat the header and put the caption on the first table page. Keep table explanations on separate slides.
   Use Drawlib first for computer science architecture diagrams, flowcharts, and pipelines, including AI, deep learning, and AIOps. Give every node a meaningful icon alongside its label. Use a consistent icon family, size, and placement within each figure, and leave room for labels and arrows. Choose Matplotlib or a domain-specific plotting library for data figures, such as training curves and evaluation plots. Use a native PowerPoint chart for supported types when the user needs to edit the data in PowerPoint. See [figure tool selection](references/figure_tools.md) for specialist tools and fallbacks.
   Use white boxes for flowchart steps and keep editable source when available. Use SimHei title bars and bold SimSun body text throughout, including bullets and callouts. Use blue or burgundy red only for a meaningful term or short phrase that helps readers find a key mechanism, distinction, or conclusion. Keep numbers, standalone letters and symbols, repeated terms, and routine labels in the default body color. See [schema usage](references/schema_usage.md) for inline colors. Vary circle/square, filled/hollow, red/black bullet symbols by section, consistently within each list. Use a few pale blue/yellow/green panels with varied linear/radial gradients mainly for body text. Include one or two segmented, first-line-indented narrative pages when appropriate and use a few inline highlights to guide reading through their main ideas. Use distinct blue/green/yellow data colors. Figure captions go below figures and initial table captions above tables, centered in black. Give equations numbers and explain symbols in body text. Read [the detailed style guide](references/style_guide.md) before composition.
4. Use the Skill's own `.venv` interpreter. If absent, follow [installation](references/installation.md). Run `doctor`, then `validate`, then `build`. The builder loads the bundled master automatically for the default canvas and colors. Custom canvas, background, primary color or base title-bar height in `--tokens` use the requested design parameters to draw these elements. Do not install Python packages globally.

   Windows (from the Skill directory):
   ```powershell
   .venv/Scripts/python scripts/scientific_ppt.py doctor
   .venv/Scripts/python scripts/scientific_ppt.py validate tests/fixtures/demo/demo.json
   .venv/Scripts/python scripts/scientific_ppt.py build tests/fixtures/demo/demo.json --output artifacts/my-deck --strict
   ```
   Linux/macOS: replace `.venv/Scripts/python` with `.venv/bin/python`.

5. Read `qa_report.json` and inspect **every actual rendered preview**, using the contact sheet only for overview. Compare against the supplied references. Check text fit, captions, formula glyphs, image crops, table continuity, arrow paths, visual balance and consistency. Read [visual QA](references/visual_qa.md) for report interpretation and repair limits. Change content allocation/layout rather than reducing body type. The engine caps repair attempts; limit your own additional manual repair cycles to three, then report unresolved issues.
6. Deliver the PPTX, previews and a concise limitations report. Include the editable JSON when useful. A successful PPTX export or zero geometric errors alone is not visual approval. If no renderer is available, provide the PPTX as **unverified** and explain the missing backend. Never fabricate preview images as proof of PPT rendering.

## Commands and references

- `extract source.pdf --output artifacts/source.txt`: extract text from PDF/DOCX/MD/TXT; Agent still reads figures.
- `analyze reference_directory --output artifacts/reference-study`: analyze every PPT/PPTX with structure and actual renders. Review provisional token candidates before adopting them.
- `plan outline.md --output artifacts/deck.json`: deterministic heading/paragraph intake only.
- `build deck.json --output artifacts/deck [--tokens custom_tokens.json] [--max-repairs 2]`: native PPTX with actual preview when possible.
- `render deck.pptx --output artifacts/previews [--backend libreoffice]`: actual PPT rendering.
- [Architecture](references/architecture.md): module boundaries and chosen dependencies.
- [Diagrams and equations](references/graphics.md): graph routing, LaTeX coverage and editability boundaries.
- [Figure tool selection](references/figure_tools.md): default tools by figure type and optional dependencies.
- [Test results](references/test_report.md): executed validation and known limitations.

Keep outputs local unless the user authorizes publication. Supplied references are stylistic evidence; do not redistribute their images, logos or text without appropriate rights.
