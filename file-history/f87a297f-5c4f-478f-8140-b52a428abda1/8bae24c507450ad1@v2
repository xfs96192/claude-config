# Memory Notes

## Weekly Report Pipeline - FULLY TESTED (2026-02-09)
- Full end-to-end pipeline working: Steps 1-5 all automated
- Scripts: `/tmp/generate_excel_screenshots_v2.py` (Step 4), `/tmp/assemble_word_report.py` (Step 5)
- config.py YUNZUOGAILAN_DATE at ~line 46 is the master date

## Step 4: Screenshot Pipeline (WORKING)
- Script: `/tmp/generate_excel_screenshots_v2.py` (~600 lines)
- Generates HTML from Excel VBA workbook sheets, resolves VLOOKUP formulas, screenshots via Playwright
- **Critical fix**: openpyxl `read_only=True` creates `EmptyCell` without `.row`/`.column` - use `data_only=True` only
- External file mapping: [1]=合享承诺收益率, [2]=输出结果, [3]=运作概览, [4]=产品业绩, [5]=合享底表, [6]=悦动稳享底表
- Formula resolution handles: IF+VLOOKUP, IFERROR+VALUE+VLOOKUP, SUM, ext cell refs, MATCH (full-row refs), arithmetic
- Multi-pass resolution (5 passes) for formula dependencies
- 59/59 screenshots generated in ~30 seconds
- Some sheets have low fill rates due to unresolved formulas (SUMPRODUCT, complex nested IF) - acceptable

## Step 5: Word/PDF Assembly (WORKING)
- Script: `/tmp/assemble_word_report.py`
- Converts .docm → .docx by stripping VBA (zipfile approach: remove vbaProject.bin, change content types)
- python-docx CANNOT open .docm files (ValueError on content_type) - use zipfile + lxml directly
- Inserts text at bookmarks (规模/中收/到期文字, 首页/到期日期)
- Inserts 59 PNG images at bookmarks using OOXML inline drawing XML
- PDF via LibreOffice headless: `soffice --headless --convert-to pdf`
- LibreOffice installed via `brew install --cask libreoffice`
- AppleScript "save as" does NOT work with Word for Mac (use JXA `exportAs` instead, but LibreOffice more reliable)
- Output: 57-page PDF, 12.3MB

## Step 3: Excel Link Update
- Works well with openpyxl: update 链接数据表 B/C columns, replace date strings in formulas
- Must use `keep_vba=True` when saving .xlsm

## Bookmark Mapping
- 书签表 sheet: 59 rows mapping Excel sheet names → Word bookmark names
- 66 total bookmarks in Word template: 59 image + 7 text (规模文字, 中收文字, 到期文字, 市场文字, 首页日期, 到期日期, 目标盈)
- 市场文字 and 目标盈 are typically manual/empty

## Web Dashboard (WORKING)
- Script: `generate_weekly_dashboard.py` (also at `/tmp/generate_weekly_dashboard.py`)
- Generates self-contained HTML (~340KB) from `/tmp/weekly_report_data.json`
- 20 sections, 39 tables, sidebar navigation, search, column sorting
- **Excel Upload**: Client-side SheetJS parsing, rebuilds all tables dynamically
- **PDF Export**: `window.print()` with @media print CSS, A4 landscape, 23 pages
- **Kangxi radical fix**: Sheet name `3、本⽉` uses U+2F49 (Kangxi) vs U+6708 (standard 月). Added `normalizeSheetName()` + `findSheet()` JS functions for fuzzy matching
- Output: `输出结果/周报仪表板-{DATE}.html`

## iChoice Data Source Integration (2026-02-10)
- `market_data_provider.py` now supports both Wind and iChoice(EMQuantAPI) backends
- Config: `DATA_SOURCE = 'ichoice'` in config.py (default), switch to 'wind' if needed
- SDK path: `/Users/fanshengxia/Desktop/ichoice/EMQuantAPI_Python/python3`
- **Working codes**: All .WI→.EI mappings (885005→809008, 885006→809009, 885007→809010, 885008→809007, 885001→809002), 000832.CSI→000832.SH, all .SH/.SZ/.CSI stock indices, H30269.CSI
- **No data permission**: CBA*.CS (中债指数), USDCNY.IB (汇率) - codes valid but return None
- **Unavailable**: NH0100.NHF, SPTAUUSDOZ.IDC - no iChoice equivalent
- iChoice `c.csd()` with `Ispandas=1` returns DataFrame(CODES, DATES, CLOSE)
- Login: `c.start("ForceLogin=1,UserName=xxx,Password=xxx")`, must call `c.stop()` on exit

## Project Architecture
- `generate_report.py` is the main script (~1800 lines), generates 40+ sheets
- `load_data.py` has NAV caching in `.nav_cache/` - first run slow (~30min), cached runs fast
- `market_data_provider.py` supports Wind and iChoice - singleton pattern, config-driven source
- All config in `config.py` via `Config` class with auto-calculated dates
- 链接数据表 sheet in Excel workbook tracks 6 external file references
