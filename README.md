# TMmonitor

AI 台灣商標自動監控系統（TIPO OpenData API）

## 功能重點
- 監控名單（Watchlist）同步：依「代理人名稱包含關鍵字」增量建立監控名單。
- 候選案件同步：
  - TmarkRights 註冊公告
  - TmarkAppl 一年內申請案
- 必做前置條件：只比對 goods-group 有交集的案件。
- 近似比對：形（文字）、音（拼音）、義（語意向量）及可選圖像比對。
- 可配置分級門檻（高/中/低），並輸出理由。
- Email / Slack 示警與 CSV 報表輸出。

## 需求
- Python 3.11+
- PostgreSQL（或使用 SQLite 進行開發測試）

## 安裝
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 環境變數
複製 `.env.example` 並填入 `TIPO_TK`。

```bash
cp .env.example .env
```

## 初始化資料庫
```bash
python -m tmmonitor.cli init-db
```

## CLI 使用範例
```bash
# 同步 watchlist（初次可用 --no-incremental）
python -m tmmonitor.cli sync-watchlist --start 2015-01-01 --end 2015-12-31 --no-incremental

# 取得候選案件（註冊公告與一年內申請案）
python -m tmmonitor.cli fetch-candidates --start 2024-01-01 --end 2024-01-31

# 執行比對
python -m tmmonitor.cli run-similarity

# 產出報表（CSV）
python -m tmmonitor.cli report --run-id 1 --format csv

# 產出報表（Excel）
python -m tmmonitor.cli report --run-id 1 --format excel

# 發送告警
python -m tmmonitor.cli send-alerts --run-id 1
```

## API 使用
```bash
uvicorn tmmonitor.api:app --reload --port 8000
```

## 相似度分級
預設分級（可透過環境變數調整）：
- 高（high）：≥ 0.85
- 中（medium）：0.75–0.85
- 低（low）：0.65–0.75

## 圖像比對
若 `SIM_ENABLE_IMAGE=true`：
- 感知哈希（pHash）作為基本相似度
- 若已安裝 OpenCV，會加上 ORB 特徵比對

## 測試
```bash
pytest
```
