<div align="center">

# yfWL — 全球股市看盤

### [English Version](#yfwl--global-stock-monitor)

</div>

---

## 免責聲明 / 重要警語

> **⚠️ 請務必閱讀以下內容再使用本軟體**
> 
> 1. 本軟體所提供之報價資訊 **至少延遲 15 至 20 分鐘**，並非即時（Real-time）資料。
> 2. 所有資訊 **僅供參考**，不構成任何投資建議。實際交易價格請一律以您的券商或交易所報價為準。
> 3. 本軟體之作者及軟體本身 **不對任何投資損失負責**。使用者使用本軟體即表示已閱讀、理解並願意承擔一切風險。
> 4. 投資有風險，入市需謹慎。請在充分了解相關風險後，自行做出投資決策。

---

## 專案背景與起源

### 為什麼做這個專案？

在日常追蹤全球股市的過程中，面臨幾個痛點：

1. **資訊分散**：美股、台股、港股、A 股、全球指數散落在不同平台，切換麻煩
2. **付費門檻高**：多數專業看盤軟體需要付費訂閱，且功能臃腫
3. **免費工具限制多**：免費方案往往有 API 呼叫次數限制、資料不完整、介面不友善
4. **批量查詢效率低**：逐個查詢股票報價，等待時間很長

因此決定打造一個 **免費、開源、跨市場** 的桌面看盤工具。

### 專案目標

- 整合全球主要股市（美股、台股、A 股、港股、歐股、主要指數）
- 提供直覺的觀測清單管理
- 技術分析圖表（K 線、MACD、KDJ、均線）
- 即時新聞聚合
- 價格提醒功能
- 多語言介面

---

## 開發過程

### 階段一：原型驗證

起初使用簡單的 `yfinance` 逐個抓取股票資料，確認技術可行性。此時一個觀測清單 20 支股票需要 **超過 8 秒** 才能載入完成。

### 階段二：功能完善

加入 FastHTML 框架構建 Web UI，使用 pyview 包裝成桌面應用。實現了：

- 觀測清單管理（多清單切換、新增、刪除、排序）
- 股票搜尋（本地 1 萬+ 股票索引 + Yahoo 線上搜尋）
- 技術線圖（日線/週線/月線、KDJ、MACD、均線）
- 相關新聞
- 價格提醒
- 多語言（繁中、簡中、英文）
- 主題切換（淺色/深色/跟隨系統）

### 階段三：效能優化（關鍵突破）

發現逐個呼叫 `yf.Ticker()` 效能瓶頸後，改用 `yf.download()` 批次下載：

| 方法                 | 20 支股票耗時   | 倍率      |
| ------------------ | ---------- | ------- |
| 逐個 `yf.Ticker()`   | ~8.5 秒     | 1x      |
| 批次 `yf.download()` | **~0.4 秒** | **20x** |

**原理**：`yf.download()` 單次 HTTP 請求即可取得所有股票的歷史資料，而逐個呼叫每個 ticker 都是獨立的 HTTP 請求。

### 階段四：穩定與優化

- 建立 HTML 快取機制，避免重複渲染
- 視窗大小自動儲存/還原
- 批次抓取失敗時自動回退到逐個更新
- 整理專案結構，移除暫時性檔案

---

## 技術架構

```
yfWL/
├── app.py              # 主程式（FastHTML + 路由 + 資料層）
├── news.py             # 新聞模組
├── run8.py             # 原始原型腳本
├── tradingView.py      # 原始原型腳本
├── Indexing.json       # 本地股票索引（1 萬+ 筆）
├── watchlist_data.json # 使用者觀測清單資料
├── rows_cache.json     # HTML 快取
├── requirements.txt    # Python 依賴
├── yfWL.bat            # Windows 啟動腳本
├── static/
│   ├── style.css       # 樣式表
│   └── lightweight-charts.js  # 圖表庫
└── README.md
```

### 核心技術

| 技術                     | 用途                |
| ---------------------- | ----------------- |
| **Python**             | 主程式語言             |
| **FastHTML**           | Web UI 框架         |
| **pywebview**          | 桌面視窗包裝            |
| **yfinance**           | Yahoo Finance 資料源 |
| **uvicorn**            | ASGI 伺服器          |
| **pandas**             | 資料處理              |
| **Lightweight Charts** | K 線圖表             |

---

## 功能特色

### 📊 觀測清單管理

- 建立多個觀測清單（例如：美股、台股、指數）
- 支援拖曳排序、快速新增/刪除
- 批次更新全部報價

### 🔍 智慧搜尋

- 本地索引涵蓋 1 萬+ 支股票（A 股、港股、美股、台股）
- Yahoo 線上搜尋補充
- 即時篩選結果

### 📈 技術分析

- K 線圖（日線/週線/月線）
- 技術指標：KDJ(9,3,3)、MACD(12,26,9)、MA5/MA20
- 成交量柱狀圖

### 📰 新聞聚合

- 個股相關 Yahoo 財經新聞
- 標題、摘要、來源、時間

### 🔔 價格提醒

- 設定高位價 / 低位價
- 觸及提醒

### ⚡ 效能優化

- 批次資料下載（20 倍加速）
- HTML 快取機制
- 非阻塞背景更新

### 🌐 多語言 & 主題

- 繁體中文 / 簡體中文 / English
- 淺色 / 深色 / 跟隨系統

---

## 快速開始

### 環境需求

- Python 3.10 以上
- Windows 10/11（主要測試平台）

### 安裝步驟

**1. 安裝 Python 依賴**

```bash
pip install -r requirements.txt
```

依賴清單：

```
yfinance>=0.2.0
python-fasthtml>=0.14.0
pywebview>=5.0.0
uvicorn>=0.30.0
```

**2. 啟動應用程式**

雙擊 `yfWL.bat` 即可啟動。

或使用命令列：

```bash
python app.py
```

**3. 開始使用**

- 左側為觀測清單，預設載入全球主要指數
- 使用搜尋欄位新增股票到觀測清單
- 點選「瀏覽」查看個股詳細資訊與技術線圖
- 點選「刷新」更新報價資料

---

## 使用者介面預覽

```
┌─────────────────────────────────────────────────────┐
│  yfWL 全球股市看盤                    [搜尋...] 🔍  │
├─────────────────────────────────────────────────────┤
│  觀測清單: [default ▼] [+新增] [🔄更新]            │
├─────────────────────────────────────────────────────┤
│  名稱          代碼      現價    漲跌    漲跌幅  操作│
│  道瓊指數      ^DJI     40,000  +150   +0.38%  🔍  │
│  S&P 500      ^GSPC    5,500   +20    +0.36%  🔍  │
│  台積電        2330.TW   950     -5     -0.52%  🔍  │
│  NVIDIA        NVDA     130     +3     +2.36%  🔍  │
│  ...                                                  │
└─────────────────────────────────────────────────────┘
```

---

## 常見問題

**Q: 為什麼資料不是即時的？**
A: Yahoo Finance 免費 API 提供的資料有 15-20 分鐘延遲，這是免費資料源的限制。

**Q: 支援哪些市場？**
A: 美股、台股、A 股（上海/深圳）、港股、歐洲主要指數、全球主要指數。

**Q: 資料準確嗎？**
A: 資料來自 Yahoo Finance，僅供參考。實際交易請以券商或交易所為準。

**Q: 可以用在 Mac/Linux 嗎？**
A: 目前主要在 Windows 上測試。Mac/Linux 理論上可行，但可能需要調整。

---

## 授權條款

本專案採用 [MIT 授權條款](LICENSE.md)。

---

# yfWL — Global Stock Monitor

### [中文版本](#yfwl--全球股市看盤)

---

## Disclaimer / Important Notice

> **⚠️ Please read the following before using this software**
> 
> 1. All quote information provided by this software is **delayed by at least 15 to 20 minutes** and is NOT real-time data.
> 2. All information is **for reference only** and does not constitute any investment advice. Actual trading prices should always be based on your broker or exchange quotes.
> 3. The author and the software itself are **not responsible for any investment losses**. By using this software, the user acknowledges having read, understood, and accepted all associated risks.
> 4. Investment involves risk. Please trade cautiously and make informed decisions after fully understanding the risks involved.

---

## Project Background

### Why was this project created?

During daily tracking of global stock markets, several pain points were identified:

1. **Fragmented Information**: US, Taiwan, China A-shares, Hong Kong, and global indices scattered across different platforms
2. **High Cost of Professional Tools**: Most professional trading software requires paid subscriptions with bloated features
3. **Free Tool Limitations**: Free alternatives often have API rate limits, incomplete data, and poor UX
4. **Slow Batch Queries**: Querying stocks one-by-one results in long wait times

The goal was to build a **free, open-source, cross-market** desktop stock monitoring tool.

### Project Goals

- Integrate major global markets (US, Taiwan, A-shares, Hong Kong, Europe, major indices)
- Provide intuitive watchlist management
- Technical analysis charts (Candlestick, MACD, KDJ, Moving Averages)
- Real-time news aggregation
- Price alert system
- Multi-language interface

---

## Development Process

### Phase 1: Prototype

Initially used simple `yfinance` individual ticker calls to verify technical feasibility. At this stage, a 20-stock watchlist took **over 8 seconds** to load.

### Phase 2: Feature Development

Built the Web UI with FastHTML framework, wrapped as a desktop app with pyview:

- Watchlist management (multiple lists, add/delete/reorder)
- Stock search (local 10K+ index + Yahoo online search)
- Technical charts (Daily/Weekly/Monthly, KDJ, MACD, Moving Averages)
- Related news
- Price alerts
- Multi-language (zh-TW, zh-CN, English)
- Theme switching (Light/Dark/System)

### Phase 3: Performance Optimization (Key Breakthrough)

After discovering the bottleneck with individual `yf.Ticker()` calls, switched to `yf.download()` batch download:

| Method                   | Time for 20 stocks | Speedup |
| ------------------------ | ------------------ | ------- |
| Individual `yf.Ticker()` | ~8.5 seconds       | 1x      |
| Batch `yf.download()`    | **~0.4 seconds**   | **20x** |

**Principle**: `yf.download()` fetches all stocks' historical data in a single HTTP request, while individual calls make separate requests for each ticker.

### Phase 4: Stabilization

- HTML caching mechanism to avoid redundant rendering
- Window size auto-save/restore
- Batch fetch fallback to individual updates on failure
- Project structure cleanup

---

## Technical Architecture

```
yfWL/
├── app.py              # Main app (FastHTML + Routes + Data Layer)
├── news.py             # News module
├── run8.py             # Original prototype script
├── tradingView.py      # Original prototype script
├── Indexing.json       # Local stock index (10K+ entries)
├── watchlist_data.json # User watchlist data
├── rows_cache.json     # HTML cache
├── requirements.txt    # Python dependencies
├── yfWL.bat            # Windows launcher
├── static/
│   ├── style.css       # Stylesheet
│   └── lightweight-charts.js  # Chart library
└── README.md
```

### Core Technologies

| Technology             | Purpose                   |
| ---------------------- | ------------------------- |
| **Python**             | Main programming language |
| **FastHTML**           | Web UI framework          |
| **pywebview**          | Desktop window wrapper    |
| **yfinance**           | Yahoo Finance data source |
| **uvicorn**            | ASGI server               |
| **pandas**             | Data processing           |
| **Lightweight Charts** | K-line charting           |

---

## Features

### Watchlist Management

- Create multiple watchlists (e.g., US stocks, Taiwan stocks, indices)
- Drag-to-reorder, quick add/remove
- Batch update all quotes

### Smart Search

- Local index covering 10K+ stocks (A-shares, Hong Kong, US, Taiwan)
- Yahoo online search as supplement
- Real-time filtering

### Technical Analysis

- Candlestick charts (Daily/Weekly/Monthly)
- Indicators: KDJ(9,3,3), MACD(12,26,9), MA5/MA20
- Volume bar chart

### News Aggregation

- Individual stock Yahoo Finance news
- Title, summary, source, timestamp

### Price Alerts

- Set high/low price thresholds
- Alert on trigger

### Performance Optimization

- Batch data download (20x speedup)
- HTML caching mechanism
- Non-blocking background updates

### Multi-language & Themes

- Traditional Chinese / Simplified Chinese / English
- Light / Dark / System

---

## Quick Start

### Requirements

- Python 3.10+
- Windows 10/11 (primary test platform)

### Installation

**1. Install Python dependencies**

```bash
pip install -r requirements.txt
```

Dependencies:

```
yfinance>=0.2.0
python-fasthtml>=0.14.0
pywebview>=5.0.0
uvicorn>=0.30.0
```

**2. Launch the application**

Double-click `yfWL.bat` to start.

Or use command line:

```bash
python app.py
```

**3. Start using**

- Left panel is the watchlist, pre-loaded with global major indices
- Use the search bar to add stocks to your watchlist
- Click "Browse" to view detailed stock info and technical charts
- Click "Refresh" to update quote data

---

## UI Preview

```
┌─────────────────────────────────────────────────────┐
│  yfWL Global Stock Monitor          [Search...] 🔍  │
├─────────────────────────────────────────────────────┤
│  Watchlist: [default ▼] [+New] [🔄Refresh]          │
├─────────────────────────────────────────────────────┤
│  Name          Ticker    Price   Change   Chg%  Act │
│  Dow Jones     ^DJI     40,000  +150    +0.38%  🔍  │
│  S&P 500      ^GSPC    5,500   +20     +0.36%  🔍  │
│  TSMC          2330.TW   950     -5     -0.52%  🔍  │
│  NVIDIA        NVDA     130     +3      +2.36%  🔍  │
│  ...                                                  │
└─────────────────────────────────────────────────────┘
```

---

## FAQ

**Q: Why isn't the data real-time?**
A: Yahoo Finance free API provides data with a 15-20 minute delay. This is a limitation of the free data source.

**Q: Which markets are supported?**
A: US, Taiwan, A-shares (Shanghai/Shenzhen), Hong Kong, major European indices, and global indices.

**Q: Is the data accurate?**
A: Data comes from Yahoo Finance and is for reference only. Always verify with your broker or exchange for actual trading.

**Q: Can I use this on Mac/Linux?**
A: Currently primarily tested on Windows. Mac/Linux may work but might require adjustments.

---

## License

This project is licensed under the [MIT License](LICENSE.md).
