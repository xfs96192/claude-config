# Implementation Plan: iChoice Financial Data Database with Auto-Update

## Context

The user wants to create a new financial database system (`ichoice_data`) that mirrors the architecture of the existing `data_api` system but uses the iChoice/EMQuantAPI data source instead of Wind. The system should:

1. Store financial market data from iChoice (macro, bonds, equities, rates, FX, commodities)
2. Implement automatic daily data updates with intelligent detection
3. Use the `/ichoice-data` skill for data retrieval
4. Follow the proven architecture from `data_api` (SQLite + scheduler + REST API)

**Key architectural insights from data_api:**
- Uses SQLite with multi-field support (indicators, indicator_fields, time_series_data, update_logs tables)
- Smart incremental update: new indicators get full historical data (from 2000), existing indicators get incremental updates
- Scheduled updates: daily at 18:00 (weekdays), weekly full update on Sundays at 02:00
- Rate limiting and error handling with retry mechanisms
- Multi-field support for indicators with multiple data dimensions (e.g., close price + PE ratio)

## Implementation Plan

### Phase 1: Project Structure Setup

**Directory Structure:**
```
ichoice_data/
├── config/
│   ├── __init__.py
│   └── config.py              # Configuration settings
├── src/
│   ├── __init__.py
│   ├── database/
│   │   ├── __init__.py
│   │   └── models.py          # Database ORM and queries
│   ├── data_fetcher/
│   │   ├── __init__.py
│   │   └── ichoice_client.py  # iChoice API wrapper
│   ├── scheduler/
│   │   ├── __init__.py
│   │   └── data_updater.py    # Update scheduler logic
│   └── api/
│       ├── __init__.py
│       └── main.py            # FastAPI REST endpoints
├── data/
│   ├── 数据指标.xlsx           # Indicator mappings (453 indicators)
│   └── ichoice_data.db        # SQLite database (auto-created)
├── logs/                      # Log files
├── main.py                    # Main entry point
├── requirements.txt
└── README.md
```

### Phase 2: Database Schema Design

**Tables (following data_api multi-field architecture):**

1. **indicators** - Base indicator metadata
   - id (PK, autoincrement)
   - category (债券/宏观/权益/资金/外汇/商品/海外/可转债)
   - name (indicator display name)
   - ichoice_code (unique, e.g., "EMM00087117", "000300.SH")
   - data_source (EDB/CSD based on code pattern)
   - created_at, updated_at

2. **indicator_fields** - Multi-field mapping (NEW)
   - id (PK)
   - ichoice_code (FK to indicators)
   - field_name (e.g., "CLOSE", "PETTM", "value")
   - field_display_name (e.g., "收盘价", "市盈率", "数值")
   - UNIQUE(ichoice_code, field_name)

3. **time_series_data** - Time series storage with field support
   - id (PK)
   - ichoice_code (FK)
   - field_name (e.g., "CLOSE", "value")
   - date (YYYY-MM-DD format)
   - value (float)
   - created_at
   - UNIQUE(ichoice_code, field_name, date)

4. **update_logs** - Update history tracking
   - id (PK)
   - ichoice_code (FK)
   - field_name (nullable, NULL = all fields)
   - update_type (smart/incremental/full/retry)
   - start_date, end_date
   - records_count
   - status (success/failed)
   - error_message
   - update_time

**Indexes:**
- idx_time_series_code_field_date ON time_series_data(ichoice_code, field_name, date)
- idx_indicators_category ON indicators(category)

### Phase 3: iChoice Data Fetcher Implementation

**File: `src/data_fetcher/ichoice_client.py`**

Key implementation details:
- Initialize SDK path: `/Users/fanshengxia/Desktop/ichoice/EMQuantAPI_Python/python3/`
- Login credentials: `xylczh0181` / `ef465509`
- **CRITICAL: Use timeout=300000 (5 min) for all Bash calls** due to initial login download
- Always use `Ispandas=1` to return DataFrames
- Always call `c.stop()` in finally block

**Data Source Logic:**
```python
def determine_data_source(ichoice_code: str) -> str:
    """Determine if code uses EDB or CSD API"""
    if ichoice_code.startswith(('EMM', 'EMG', 'EMI', 'E')):
        return 'EDB'  # Macro/bond yields
    elif '.' in ichoice_code:  # Has exchange suffix
        return 'CSD'  # Market data (equities, FX, rates, commodities)
    else:
        return 'UNKNOWN'

def fetch_edb_data(codes: List[str], start_date: str, end_date: str) -> pd.DataFrame:
    """Fetch EDB data (max 100 indicators per call)"""
    # Batch into groups of 100
    # c.edb("EMM00072301,EMM00073348", "StartDate=2024-01-01,EndDate=2025-01-31,Ispandas=1")

def fetch_csd_data(code: str, field: str, start_date: str, end_date: str) -> pd.DataFrame:
    """Fetch CSD time series (one code at a time for long periods)"""
    # c.csd("000300.SH", "CLOSE", "2025-01-01", "2025-01-31", "Ispandas=1")
    # For multi-year: loop codes individually to avoid timeout
```

**Multi-field handling:**
- Some indicators have multiple fields (e.g., stock indices: CLOSE + PETTM)
- Fetch each field separately and store with field_name differentiation
- EDB indicators always use field_name="value"
- CSD indicators specify field (CLOSE, PETTM, etc.)

### Phase 4: Smart Update Logic Implementation

**File: `src/scheduler/data_updater.py`**

Implement three update strategies:

**1. Smart Incremental Update (Default, recommended)**
```python
def smart_incremental_update(self):
    """
    Intelligent update strategy:
    - NEW indicators (no data in DB): Full historical from 2000-01-01
    - EXISTING indicators: Incremental from last_date + 1 to today
    """
    indicators = self.db.get_indicators()

    for indicator in indicators:
        last_date = self.db.get_last_update_date(indicator['ichoice_code'])

        if last_date is None:
            # New indicator: full historical
            self.update_indicator(indicator, "2000-01-01", today, "smart_new")
        else:
            # Existing: incremental
            start = (datetime.strptime(last_date, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')
            if start <= today:
                self.update_indicator(indicator, start, today, "smart_existing")

        time.sleep(1)  # Rate limiting
```

**2. Full Historical Update**
- All indicators from 2000-01-01 to today
- Use for initial setup or complete refresh

**3. Retry Failed Indicators**
- Query indicators with 0 data points or failed status in update_logs
- Attempt full historical update for these only

**Multi-field update handling:**
```python
def update_indicator(self, indicator: Dict, start_date: str, end_date: str, update_type: str):
    """Update single indicator with multi-field support"""
    ichoice_code = indicator['ichoice_code']

    # Get fields for this indicator
    fields = self.db.get_indicator_fields(ichoice_code)

    for field_info in fields:
        field_name = field_info['field_name']

        try:
            # Fetch data based on source
            if indicator['data_source'] == 'EDB':
                data = self.fetcher.fetch_edb(ichoice_code, start_date, end_date)
            else:  # CSD
                data = self.fetcher.fetch_csd(ichoice_code, field_name, start_date, end_date)

            # Store with field_name
            self.db.insert_time_series_data(ichoice_code, field_name, data)

            # Log success
            self.db.log_update(ichoice_code, field_name, update_type, start_date, end_date,
                             len(data), "success", None)
        except Exception as e:
            # Log failure
            self.db.log_update(ichoice_code, field_name, update_type, start_date, end_date,
                             0, "failed", str(e))
```

### Phase 5: Scheduler Configuration

**File: `src/scheduler/data_updater.py`**

```python
def setup_schedule(self):
    """Configure scheduled tasks"""
    # Daily incremental update (weekdays at 18:00)
    schedule.every().monday.at("18:00").do(self.smart_incremental_update)
    schedule.every().tuesday.at("18:00").do(self.smart_incremental_update)
    schedule.every().wednesday.at("18:00").do(self.smart_incremental_update)
    schedule.every().thursday.at("18:00").do(self.smart_incremental_update)
    schedule.every().friday.at("18:00").do(self.smart_incremental_update)

    # Weekly full update (Sunday at 02:00)
    schedule.every().sunday.at("02:00").do(lambda: self.full_update(2000))

def run_scheduler(self):
    """Run scheduler in background thread"""
    self.setup_schedule()
    while self.is_running:
        schedule.run_pending()
        time.sleep(60)  # Check every minute
```

### Phase 6: Configuration File

**File: `config/config.py`**

```python
class Settings(BaseSettings):
    # Database
    DATABASE_PATH: str = "data/ichoice_data.db"

    # iChoice SDK
    ICHOICE_SDK_PATH: str = "/Users/fanshengxia/Desktop/ichoice/EMQuantAPI_Python/python3/"
    ICHOICE_USERNAME: str = "xylczh0181"
    ICHOICE_PASSWORD: str = "ef465509"
    ICHOICE_TIMEOUT: int = 300000  # 5 minutes in ms

    # Data settings
    HISTORICAL_START_YEAR: int = 2000
    INDICATOR_EXCEL_PATH: str = "data/数据指标.xlsx"

    # Rate limits (from iChoice skill documentation)
    EDB_MAX_INDICATORS_PER_REQUEST: int = 100
    CSD_RATE_LIMIT: int = 700  # requests per minute
    REQUEST_INTERVAL: float = 1.0  # seconds between requests

    # Scheduler
    DAILY_UPDATE_TIME: str = "18:00"
    WEEKLY_UPDATE_TIME: str = "02:00"

    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8001  # Different from data_api (8000)

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_DIR: str = "logs"
```

### Phase 7: Main Entry Point

**File: `main.py`**

Command structure (following data_api pattern):
```bash
# Initialize database and load indicators from Excel
python main.py init

# Smart incremental update (default, recommended)
python main.py update

# Specific update types
python main.py update --update-type smart        # Smart (default)
python main.py update --update-type incremental  # Traditional incremental
python main.py update --update-type full         # Full historical
python main.py update --update-type retry        # Retry failed only

# Start REST API server
python main.py server

# Start background scheduler
python main.py scheduler

# Check system status
python main.py status

# Analyze multi-field indicators
python main.py fields
```

### Phase 8: Indicator Data Loading

**Load from `/Users/fanshengxia/Desktop/ichoice/数据指标.xlsx`:**
- 453 indicator code mappings (Wind → Choice)
- Parse to determine:
  - Category (债券/宏观/权益 etc.)
  - iChoice code (EMM00087117, 000300.SH, etc.)
  - Data source (EDB vs CSD based on code pattern)
  - Fields (for CSD: CLOSE, PETTM; for EDB: value)

**Multi-field detection:**
- Stock indices (000300.SH, etc.): CLOSE + PETTM
- Shenwan industries (801*.SWI): CLOSE + PETTM
- Bond yields, macro, rates, FX: single field "value"

### Phase 9: REST API Endpoints

**File: `src/api/main.py`**

```python
# GET /indicators?category=宏观
# Returns: List of indicators

# GET /data/{ichoice_code}?field_name=CLOSE&start_date=2024-01-01&end_date=2025-01-31
# Returns: Time series data for specific field

# GET /data/{ichoice_code}?start_date=2024-01-01
# Returns: All fields for the indicator (multi-field support)

# POST /batch-data
# Body: {"codes": ["000300.SH", "EMM00072301"], "start_date": "2024-01-01", "end_date": "2025-01-31"}
# Returns: Batch data for multiple indicators

# POST /update
# Body: {"update_type": "smart"}
# Triggers manual update

# GET /status
# Returns: System status, data completeness, update logs
```

### Phase 10: Error Handling & Rate Limiting

**Key safeguards:**

1. **iChoice API timeout handling:**
   - All Python script calls via Bash must use `timeout=300000` (5 min)
   - First login downloads config files (ChoiceToHQ.xml), can take 2-3 min
   - Always use single-script execution (not fragmented calls)

2. **Rate limiting:**
   - EDB: Max 100 indicators per request, batch accordingly
   - CSD: 700 requests/min limit
   - Add 1-second delay between indicator updates

3. **Long-period data fetching:**
   - For multi-year CSD queries with multiple codes: fetch codes individually
   - Example: Don't do `c.csd("000300.SH,000905.SH", "CLOSE", "2000-01-01", "2025-01-31")`
   - Instead: Loop each code separately to avoid timeout

4. **Retry logic:**
   - Log all failures with error messages
   - Provide `retry` update type to re-attempt only failed indicators
   - Max 3 retry attempts with exponential backoff

5. **Data validation:**
   - Check for null/empty DataFrames before insertion
   - Validate date formats (CSD returns "YYYY/MM/DD", convert to "YYYY-MM-DD")
   - Ensure field_name consistency

## Critical Files to Create/Modify

### Must Create:
1. `/Users/fanshengxia/Desktop/ichoice_data/` - Project root
2. `config/config.py` - Settings with iChoice credentials
3. `src/database/models.py` - SQLite ORM with multi-field support
4. `src/data_fetcher/ichoice_client.py` - iChoice API wrapper using EMQuantAPI
5. `src/scheduler/data_updater.py` - Smart update logic + scheduler
6. `src/api/main.py` - FastAPI REST endpoints
7. `main.py` - CLI entry point
8. `requirements.txt` - Dependencies
9. `data/数据指标.xlsx` - Copy from `/Users/fanshengxia/Desktop/ichoice/数据指标.xlsx`

### Dependencies (requirements.txt):
```
pandas>=2.0.0
openpyxl>=3.1.0
schedule>=1.2.0
fastapi>=0.109.0
uvicorn>=0.27.0
pydantic-settings>=2.1.0
python-dotenv>=1.0.0
```

## Testing & Validation Strategy

1. **Database initialization:**
   ```bash
   python main.py init
   # Verify: 453 indicators loaded, multi-field mappings created
   ```

2. **Single indicator test:**
   - Test EDB indicator: `EMM00072301` (CPI)
   - Test CSD indicator: `000300.SH` with CLOSE field
   - Verify data stored with correct field_name

3. **Smart update test:**
   ```bash
   python main.py update --update-type smart
   # Verify: New indicators get 2000-present data, existing get incremental
   ```

4. **Scheduler test:**
   ```bash
   python main.py scheduler
   # Verify: Schedules created for 18:00 weekdays, 02:00 Sunday
   ```

5. **API test:**
   ```bash
   python main.py server
   curl "http://localhost:8001/status"
   curl "http://localhost:8001/data/000300.SH?field_name=CLOSE&start_date=2025-01-01"
   ```

## Execution Sequence

1. Create project directory structure
2. Implement database models (multi-field schema)
3. Implement iChoice data fetcher (EDB + CSD with proper timeout handling)
4. Load indicators from Excel and populate database
5. Implement smart update logic
6. Test single indicator updates (EDB and CSD)
7. Implement scheduler
8. Implement REST API
9. Run initial full update: `python main.py update --update-type full`
10. Set up scheduler as background service: `python main.py scheduler`

## Key Differences from data_api

| Aspect | data_api (Wind) | ichoice_data (iChoice/EMQuant) |
|--------|----------------|--------------------------------|
| Data source | WindPy (direct) | EMQuantAPI Python SDK |
| SDK path | N/A (pip install) | `/Users/fanshengxia/Desktop/ichoice/EMQuantAPI_Python/python3/` |
| Auth | Wind client login | Username/password in script |
| Timeout | Default (2 min) | **300000ms (5 min) CRITICAL** |
| API pattern | w.wsd() / w.edb() | c.csd() / c.edb() |
| Code suffix | .WI / .SI | .EI / .SWI |
| Rate limits | Not specified | 700 req/min (CSD), 100 indicators/req (EDB) |
| Date format | YYYY-MM-DD | YYYY/MM/DD (needs conversion) |
| Multi-code fetch | Supports batch | **Split for long periods** |
| Script execution | Direct function calls | **Single heredoc script** |

## Success Criteria

✅ Database initialized with 453 indicators and field mappings
✅ Smart incremental update working: new indicators get full history, existing get daily updates
✅ Multi-field support: stock indices store both CLOSE and PETTM separately
✅ Scheduler running: daily 18:00 updates, weekly Sunday 02:00 full refresh
✅ REST API serving data queries with field filtering
✅ Error handling and retry mechanism for failed indicators
✅ Data completeness > 95% after initial full update
✅ No timeout errors due to proper 5-minute timeout configuration
✅ Logging system tracking all updates and failures

## Post-Implementation

- Document API usage in README.md
- Create data query examples (similar to data_api's QUICK_REFERENCE.md)
- Set up systemd service (Linux) or launchd (macOS) for background scheduler
- Implement data quality checks (missing dates, outliers)
- Add monitoring dashboard for update status
- Create backup strategy for SQLite database
