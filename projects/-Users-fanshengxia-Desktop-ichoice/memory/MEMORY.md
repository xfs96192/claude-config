# iChoice Project Memory

## Key Files
- SDK: `/Users/fanshengxia/Desktop/ichoice/EMQuantAPI_Python/python3/`
- Account: `xylczh0181` / `ef465509`
- Indicator mapping: `/Users/fanshengxia/Desktop/ichoice/数据指标.xlsx` (453 indicators, Wind->Choice)
- Skill created: `/Users/fanshengxia/.claude/skills/ichoice-data/`

## Skill Structure
- `SKILL.md` - Main instructions with quick start and query patterns
- `references/api_reference.md` - Full EMQuantAPI documentation
- `references/indicator_codes.md` - All 453 indicator code mappings (Wind -> Choice)

## Key Learnings
- Wind `.SI` suffix -> Choice `.SWI` for Shenwan industry indices
- Wind `881001.WI` (万得全A) -> Choice `800000.EI`
- EDB codes use EMM/EMG/EMI/E prefix for macro/bond yield data
- Some indicators have no Choice equivalent (南华指数, USDCNYM.IB)
- `Ispandas=1` returns DataFrame; otherwise returns EmQuantData object
- Rate limits: css/csd 700 req/min, edb max 100 indicators per request
