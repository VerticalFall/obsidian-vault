# 巴菲特公司研究助手 · Share Edition v2.1

Chinese display name: 巴菲特公司研究助手. After uploading the portable guide or installing the skill, use the natural-language launch phrase `巴菲特研究 [company/ticker]`. Example: `巴菲特研究 贵州茅台（600519），生成Excel和图表。` The internal skill identifier remains `buffett` for compatibility. The guide must be accessible in the current conversation.

[中文使用说明](README.zh.md)

A model-neutral Buffett-inspired company research workflow with optional Excel workbooks and editable charts. The original eight references are preserved. Three new references cover data provenance, industry-specific valuation and workbook delivery.

## Regular AI chat

Upload `巴菲特公司研究助手-通用精简版.md` from the share archive and use the short launch phrase above, or the detailed request below:

```text
Use the attached Buffett research guide for [company, ticker, exchange]
using disclosures available as of [date]. Deliver a full report and an Excel
workbook with editable charts. Separate facts, calculations, assumptions and
judgments. Cite decisive sources. Use industry-appropriate valuation methods,
bear/base/bull cases, margins of safety and monitoring triggers.
If browsing or file generation is unavailable, explain the limitation and
provide usable tables, formulas and chart instructions instead.
```

Specify text only or Excel without charts if preferred. Unspecified chart preferences are asked once, without delaying independent research. Explicit requests are not reconfirmed.

The compact prompt includes the entrypoint and three execution references. For deeper conceptual material, upload individual original references or the full portable prompt, subject to context limits. Never claim to have read omitted references.

## Native skills agent

Import the entire `skills/buffett/` folder using the product's supported mechanism. Installation locations differ. Invoke `buffett` or ask the agent to read `SKILL.md`. This package does not install itself or change settings.

Portable instructions do not grant browsing, calculation, xlsx generation, native charts or rendering capabilities. Outputs depend on the host's actual tools. This edition has not been tested on every model.

## Research and delivery

Full research covers business economics, moats, management, financial quality, dividends, industry-specific valuation, scenarios, risks and monitoring. Workbooks typically include a dashboard, business quality, financials, shareholder returns, valuation assumptions, risk tracking and source data. Smaller tasks can combine sections.

Banks, insurers, resource producers, utilities, manufacturers and growth companies use different metrics and valuation anchors. Charts are optional. Missing data, unverifiable quotations and unperformed recalculation or visual checks must be disclosed.

The original references are historical/conceptual material rather than current data. New references 09 and 10 override generic multiples and formulas in the originals. The broken thermal-power reference was removed. Original benchmark claims are not repeated because those evaluations were not rerun for this edition.

## Rebuild

Use standard Python, no third-party dependencies, with a fresh output directory:

```text
python scripts/build_share.py --output dist-new
```

The archive contains the skill, references, documentation and portable prompts. It excludes private research, chat history, machine paths and the old demo video. Edit source files and rebuild rather than editing generated prompts.

Original project: [agi-now/buffett-skills](https://github.com/agi-now/buffett-skills). The eight original references are preserved. No author licensing terms are added or replaced; the supplied directory contained no LICENSE file. Retain attribution and separately verify redistribution permission.
