import json
import os
import time
import threading
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import yfinance as yf
from fasthtml.common import *

# ==================== 全域配置 ====================
DATA_FILE = Path(__file__).parent / "watchlist_data.json"
TICKERS_FILE = Path(__file__).parent / "Indexing.json"

DEFAULT_WATCHLIST = [
    {"name": "道瓊工業平均指數", "ticker": "^DJI", "type": "index"},
    {"name": "S&P500 指數", "ticker": "^GSPC", "type": "index"},
    {"name": "納斯達克綜合指數", "ticker": "^IXIC", "type": "index"},
    {"name": "費城半導體指數", "ticker": "^SOX", "type": "index"},
    {"name": "台灣加權指數", "ticker": "^TWII", "type": "index"},
    {"name": "上證綜指", "ticker": "000001.SS", "type": "index"},
    {"name": "深證成指", "ticker": "399001.SZ", "type": "index"},
    {"name": "恆生指數", "ticker": "^HSI", "type": "index"},
    {"name": "日經 225 指數", "ticker": "^N225", "type": "index"},
    {"name": "韓國綜合股價指數", "ticker": "^KS11", "type": "index"},
    {"name": "新加坡海峽時報指數", "ticker": "^STI", "type": "index"},
    {"name": "德國 DAX 指數", "ticker": "^GDAXI", "type": "index"},
    {"name": "法國 CAC40 指數", "ticker": "^FCHI", "type": "index"},
    {"name": "英國富時 100 指數", "ticker": "^FTSE", "type": "index"},
]

# 多語言翻譯
TRANSLATIONS = {
    "zh-TW": {
        "app_title": "yfWL 全球股市看盤",
        "search_placeholder": "搜尋股票代碼或名稱...",
        "local_results": "本地索引結果",
        "yahoo_results": "Yahoo 線上索引結果",
        "add": "加入",
        "remove": "刪除",
        "browse": "瀏覽",
        "up": "上移",
        "down": "下移",
        "settings": "系統設定",
        "language": "語言",
        "font": "字體",
        "font_size": "字體大小",
        "scale": "縮放比例",
        "theme": "主題",
        "theme_system": "跟隨系統",
        "theme_light": "淺色模式",
        "theme_dark": "深色模式",
        "auto_update": "自動更新",
        "manual_update_current": "更新當前頁面",
        "manual_update_all": "更新全部報價",
        "last_update": "最後更新",
        "price_alert": "價格提醒",
        "delay_warning": "⚠️ 報價資訊延遲至少15~20分鐘。所有資訊僅供參考，實際交易價格請以券商或交易所為準。",
        "basic_info": "基本資訊",
        "technical_chart": "技術線圖",
        "related_news": "相關新聞",
        "daily": "日線",
        "weekly": "週線",
        "monthly": "月線",
        "open": "開盤",
        "high": "最高",
        "low": "最低",
        "close": "收盤",
        "volume": "成交量",
        "change": "漲跌",
        "change_pct": "漲跌幅",
        "market_cap": "市值",
        "pe_ratio": "本益比",
        "eps": "每股盈餘",
        "dividend_yield": "殖利率",
        "no_data": "無資料",
        "set_alert": "設定提醒",
        "alert_high": "高位價",
        "alert_low": "低位價",
        "save": "儲存",
        "cancel": "取消",
        "name": "名稱",
        "ticker": "代碼",
        "price": "現價",
        "actions": "操作",
        "watchlist": "觀測清單",
        "new_watchlist": "新建清單",
        "rename": "重命名",
        "delete_watchlist": "刪除清單",
        "switch_watchlist": "切換清單",
        "confirm_delete": "確定要刪除嗎？",
        "watchlist_name": "清單名稱",
    },
    "zh-CN": {
        "app_title": "yfWL 全球股市看盘",
        "search_placeholder": "搜索股票代码或名称...",
        "local_results": "本地索引结果",
        "yahoo_results": "Yahoo 线上索引结果",
        "add": "加入",
        "remove": "删除",
        "browse": "浏览",
        "up": "上移",
        "down": "下移",
        "settings": "系统设置",
        "language": "语言",
        "font": "字体",
        "font_size": "字体大小",
        "scale": "缩放比例",
        "theme": "主题",
        "theme_system": "跟随系统",
        "theme_light": "浅色模式",
        "theme_dark": "深色模式",
        "auto_update": "自动更新",
        "manual_update_current": "更新当前页面",
        "manual_update_all": "更新全部报价",
        "last_update": "最后更新",
        "price_alert": "价格提醒",
        "delay_warning": "⚠️ 报价资讯延迟至少15~20分钟。所有信息仅供参考，实际交易价格请以券商或交易所为准。",
        "basic_info": "基本信息",
        "technical_chart": "技术线图",
        "related_news": "相关新闻",
        "daily": "日线",
        "weekly": "周线",
        "monthly": "月线",
        "open": "开盘",
        "high": "最高",
        "low": "最低",
        "close": "收盘",
        "volume": "成交量",
        "change": "涨跌",
        "change_pct": "涨跌幅",
        "market_cap": "市值",
        "pe_ratio": "市盈率",
        "eps": "每股收益",
        "dividend_yield": "股息率",
        "no_data": "无数据",
        "set_alert": "设置提醒",
        "alert_high": "高位价",
        "alert_low": "低位价",
        "save": "保存",
        "cancel": "取消",
        "name": "名称",
        "ticker": "代码",
        "price": "现价",
        "actions": "操作",
    },
    "en": {
        "app_title": "yfWL Global Stock Monitor",
        "search_placeholder": "Search ticker or company name...",
        "local_results": "Local Index Results",
        "yahoo_results": "Yahoo Online Results",
        "add": "Add",
        "remove": "Remove",
        "browse": "Browse",
        "up": "Up",
        "down": "Down",
        "settings": "Settings",
        "language": "Language",
        "font": "Font",
        "font_size": "Font Size",
        "scale": "Scale",
        "theme": "Theme",
        "theme_system": "System",
        "theme_light": "Light",
        "theme_dark": "Dark",
        "auto_update": "Auto Update",
        "manual_update_current": "Update Current",
        "manual_update_all": "Update All",
        "last_update": "Last Update",
        "price_alert": "Price Alert",
        "delay_warning": "⚠️ Quotes delayed 15-20 min. For reference only, actual trading price should be based on broker or exchange.",
        "basic_info": "Basic Info",
        "technical_chart": "Technical Chart",
        "related_news": "Related News",
        "daily": "Daily",
        "weekly": "Weekly",
        "monthly": "Monthly",
        "open": "Open",
        "high": "High",
        "low": "Low",
        "close": "Close",
        "volume": "Volume",
        "change": "Change",
        "change_pct": "Change %",
        "market_cap": "Market Cap",
        "pe_ratio": "P/E Ratio",
        "eps": "EPS",
        "dividend_yield": "Div Yield",
        "no_data": "No Data",
        "set_alert": "Set Alert",
        "alert_high": "High Alert",
        "alert_low": "Low Alert",
        "save": "Save",
        "cancel": "Cancel",
        "name": "Name",
        "ticker": "Ticker",
        "price": "Price",
        "actions": "Actions",
    },
}

# ==================== 資料持久化 ====================
class DataStore:
    def __init__(self):
        self.data = self.load()
        self.lock = threading.Lock()
    
    def load(self):
        if DATA_FILE.exists():
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # 確保watchlists結構正確
                    if "watchlists" not in data:
                        data["watchlists"] = {"items": {}, "current": "default"}
                    if "items" not in data["watchlists"]:
                        data["watchlists"]["items"] = {}
                    if "current" not in data["watchlists"]:
                        data["watchlists"]["current"] = "default"
                    if "settings" not in data:
                        data["settings"] = self.create_default()["settings"]
                    # 確保新版設定欄位存在
                    defaults = self.create_default()["settings"]
                    for k, v in defaults.items():
                        if k not in data["settings"]:
                            data["settings"][k] = v
                    # 如果有舊格式的數據，轉換為新格式
                    if "default" in data["watchlists"] and isinstance(data["watchlists"]["default"], list):
                        data["watchlists"]["items"]["default"] = data["watchlists"].pop("default")
                    return data
            except Exception:
                pass
        return self.create_default()
    
    def create_default(self):
        return {
            "version": "1.0",
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "settings": {
                "language": "zh-TW",
                "theme": "system",
                "font_family": "Microsoft YaHei",
                "font_size": 14,
                "auto_update_interval": 300,
                "price_alerts": {},
                "window_width": 1200,
                "window_height": 800,
            },
            "watchlists": {
                "items": {
                    "default": DEFAULT_WATCHLIST.copy(),
                },
                "current": "default",
            },
        }
    
    def save(self):
        with self.lock:
            self.data["last_updated"] = datetime.now().isoformat()
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    def get_settings(self):
        return self.data.get("settings", {})
    
    def update_settings(self, settings):
        self.data["settings"].update(settings)
        self.save()
    
    # 觀測清單管理
    def get_all_watchlists(self):
        """取得所有觀測清單名稱"""
        return list(self.data["watchlists"]["items"].keys())
    
    def get_current_watchlist_name(self):
        """取得當前觀測清單名稱"""
        return self.data["watchlists"].get("current", "default")
    
    def set_current_watchlist(self, name):
        """設定當前觀測清單"""
        if name in self.data["watchlists"]["items"]:
            self.data["watchlists"]["current"] = name
            self.save()
            return True
        return False
    
    def create_watchlist(self, name):
        """新建觀測清單"""
        if name not in self.data["watchlists"]["items"]:
            self.data["watchlists"]["items"][name] = []
            self.save()
            return True
        return False
    
    def delete_watchlist(self, name):
        """刪除觀測清單"""
        if name in self.data["watchlists"]["items"] and name != "default":
            del self.data["watchlists"]["items"][name]
            if self.data["watchlists"]["current"] == name:
                self.data["watchlists"]["current"] = "default"
            self.save()
            return True
        return False
    
    def rename_watchlist(self, old_name, new_name):
        """重命名觀測清單"""
        if old_name in self.data["watchlists"]["items"] and new_name not in self.data["watchlists"]["items"]:
            self.data["watchlists"]["items"][new_name] = self.data["watchlists"]["items"].pop(old_name)
            if self.data["watchlists"]["current"] == old_name:
                self.data["watchlists"]["current"] = new_name
            self.save()
            return True
        return False
    
    def get_watchlist(self):
        """取得當前觀測清單內容"""
        current = self.data["watchlists"].get("current", "default")
        return self.data["watchlists"]["items"].get(current, [])
    
    def set_watchlist(self, items):
        """設定當前觀測清單內容"""
        current = self.data["watchlists"].get("current", "default")
        self.data["watchlists"]["items"][current] = items
        self.save()
    
    def add_to_watchlist(self, item):
        watchlist = self.get_watchlist()
        if not any(w["ticker"] == item["ticker"] for w in watchlist):
            watchlist.append(item)
            self.set_watchlist(watchlist)
            return True
        return False
    
    def remove_from_watchlist(self, ticker):
        watchlist = self.get_watchlist()
        self.set_watchlist([w for w in watchlist if w["ticker"] != ticker])
    
    def move_item(self, ticker, direction):
        watchlist = self.get_watchlist()
        for i, item in enumerate(watchlist):
            if item["ticker"] == ticker:
                new_idx = i + direction
                if 0 <= new_idx < len(watchlist):
                    watchlist[i], watchlist[new_idx] = watchlist[new_idx], watchlist[i]
                    self.set_watchlist(watchlist)
                    return True
        return False
    
    def get_alerts(self, ticker):
        return self.data["settings"].get("price_alerts", {}).get(ticker, {})
    
    def set_alert(self, ticker, high=None, low=None):
        alerts = self.data["settings"].get("price_alerts", {})
        alerts[ticker] = {"high": high, "low": low}
        self.data["settings"]["price_alerts"] = alerts
        self.save()

store = DataStore()

# ==================== 清單 HTML 快取 ====================
CACHE_FILE = Path(__file__).parent / "rows_cache.json"

class WatchlistRowsCache:
    """為每個清單快取渲染後的 HTML，切換時瞬間載入"""
    def __init__(self):
        self.cache = {}  # {watchlist_name: html_string}
        self.cache_time = {}  # {watchlist_name: timestamp}
        self.load()
    
    def get(self, name):
        return self.cache.get(name)
    
    def set(self, name, html):
        self.cache[name] = html
        self.cache_time[name] = time.time()
    
    def get_time(self, name):
        return self.cache_time.get(name)
    
    def invalidate(self, name=None):
        if name:
            self.cache.pop(name, None)
            self.cache_time.pop(name, None)
        else:
            self.cache.clear()
            self.cache_time.clear()
    
    def save(self):
        """存檔到磁碟"""
        try:
            data = {"cache": self.cache, "cache_time": self.cache_time}
            with open(CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False)
            print(f"快取已存檔: {len(self.cache)} 個清單")
        except Exception as e:
            print(f"快取存檔失敗: {e}")
    
    def load(self):
        """從磁碟載入"""
        try:
            if CACHE_FILE.exists():
                with open(CACHE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.cache = data.get("cache", {})
                self.cache_time = data.get("cache_time", {})
                print(f"快取已載入: {len(self.cache)} 個清單")
        except Exception as e:
            print(f"快取載入失敗: {e}")

rows_cache = WatchlistRowsCache()

# ==================== 更新進度追蹤 ====================
class UpdateProgress:
    def __init__(self):
        self.current = 0
        self.total = 0
        self.running = False
        self.label = ""
    
    def start(self, total, label=""):
        self.current = 0
        self.total = total
        self.running = True
        self.label = label
    
    def tick(self):
        self.current += 1
    
    def done(self):
        self.running = False
        self.current = self.total
    
    def get(self):
        pct = round(self.current / self.total * 100) if self.total > 0 else 0
        return {
            "current": self.current,
            "total": self.total,
            "pct": pct,
            "running": self.running,
            "label": self.label
        }

progress = UpdateProgress()

# ==================== 本地索引 ====================
class LocalIndex:
    def __init__(self):
        self.tickers = self.load()
    
    def load(self):
        if TICKERS_FILE.exists():
            with open(TICKERS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Indexing.json 格式: {"tickers": [["顯示名", "代碼", "中文名"], ...]}
                return data.get("tickers", [])
        return []
    
    def search(self, query, limit=30):
        if not query or len(query) < 2:
            return []
        query_upper = query.upper()
        results = []
        for item in self.tickers:
            if isinstance(item, list) and len(item) >= 3:
                display_name = str(item[0])
                ticker = str(item[1]).upper()
                cn_name = str(item[2])
                # 搜尋代碼或中文名
                if query_upper in ticker or query in cn_name or query.upper() in display_name.upper():
                    results.append({
                        "ticker": item[1],
                        "name": cn_name,
                        "display": display_name,
                        "source": "local"
                    })
                    if len(results) >= limit:
                        break
            elif isinstance(item, dict):
                ticker = item.get("ticker", "").upper()
                name = item.get("name", "").upper()
                if query_upper in ticker or query_upper in name:
                    results.append({
                        "ticker": item.get("ticker", ""),
                        "name": item.get("name", ""),
                        "source": "local"
                    })
                    if len(results) >= limit:
                        break
        return results

local_index = LocalIndex()

# ==================== yfinance 數據 ====================
class StockData:
    cache = {}
    cache_ttl = 60
    
    @classmethod
    def get_quote(cls, ticker, force=False):
        now = time.time()
        if not force and ticker in cls.cache and now - cls.cache[ticker]["time"] < cls.cache_ttl:
            return cls.cache[ticker]["data"]
        
        try:
            stock = yf.Ticker(ticker)
            info = stock.info or {}
            hist = stock.history(period="5d")
            
            if hist.empty:
                # 嘗試使用info中的數據
                current_price = info.get("currentPrice") or info.get("regularMarketPrice") or 0
                if current_price == 0:
                    return None
                data = {
                    "ticker": ticker,
                    "name": info.get("shortName") or info.get("longName") or ticker,
                    "price": round(current_price, 2),
                    "change": 0,
                    "change_pct": 0,
                    "volume": info.get("volume", 0),
                    "market_cap": info.get("marketCap", 0),
                    "pe_ratio": info.get("trailingPE"),
                    "eps": info.get("trailingEps"),
                    "dividend_yield": info.get("dividendYield"),
                    "fifty_two_week_high": info.get("fiftyTwoWeekHigh"),
                    "fifty_two_week_low": info.get("fiftyTwoWeekLow"),
                    "previous_close": info.get("previousClose", current_price),
                    "open": info.get("regularMarketOpen", current_price),
                    "high": info.get("regularMarketDayHigh", current_price),
                    "low": info.get("regularMarketDayLow", current_price),
                    "info": info,
                    "time": now,
                }
            else:
                current = hist['Close'].iloc[-1]
                prev = hist['Close'].iloc[-2] if len(hist) > 1 else current
                change = current - prev
                change_pct = (change / prev * 100) if prev else 0
                
                data = {
                    "ticker": ticker,
                    "name": info.get("shortName") or info.get("longName") or ticker,
                    "price": round(current, 2),
                    "change": round(change, 2),
                    "change_pct": round(change_pct, 2),
                    "volume": int(hist['Volume'].iloc[-1]) if 'Volume' in hist else 0,
                    "market_cap": info.get("marketCap", 0),
                    "pe_ratio": info.get("trailingPE"),
                    "eps": info.get("trailingEps"),
                    "dividend_yield": info.get("dividendYield"),
                    "fifty_two_week_high": info.get("fiftyTwoWeekHigh"),
                    "fifty_two_week_low": info.get("fiftyTwoWeekLow"),
                    "previous_close": info.get("previousClose"),
                    "open": float(hist['Open'].iloc[-1]),
                    "high": float(hist['High'].iloc[-1]),
                    "low": float(hist['Low'].iloc[-1]),
                    "info": info,
                    "time": now,
                }
            
            cls.cache[ticker] = {"data": data, "time": now}
            return data
        except Exception as e:
            print(f"Error fetching {ticker}: {e}")
            return None
    
    @classmethod
    def get_quotes_batch(cls, tickers, force=False):
        """批量取得多個股票的報價，使用 yf.download() 批次下載"""
        now = time.time()
        results = {}
        
        # 先過濾出需要更新的 ticker
        to_fetch = []
        for ticker in tickers:
            if not force and ticker in cls.cache and now - cls.cache[ticker]["time"] < cls.cache_ttl:
                results[ticker] = cls.cache[ticker]["data"]
            else:
                to_fetch.append(ticker)
        
        if not to_fetch:
            return results
        
        try:
            # 批量下載歷史數據（單次 HTTP 請求，速度快 20 倍）
            hist_data = yf.download(to_fetch, period="5d", group_by='ticker', progress=False, threads=True)
            
            for ticker in to_fetch:
                try:
                    if len(to_fetch) == 1:
                        ticker_hist = hist_data
                    else:
                        ticker_hist = hist_data[ticker] if ticker in hist_data.columns.get_level_values(0) else None
                    
                    if ticker_hist is None or ticker_hist.empty:
                        results[ticker] = None
                        continue
                    
                    # 取得最後兩天的收盤價
                    closes = ticker_hist['Close'].dropna()
                    if len(closes) < 2:
                        results[ticker] = None
                        continue
                    
                    current = float(closes.iloc[-1])
                    prev = float(closes.iloc[-2])
                    change = current - prev
                    change_pct = (change / prev * 100) if prev else 0
                    vol_val = ticker_hist['Volume'].iloc[-1] if 'Volume' in ticker_hist else 0
                    volume = int(vol_val) if pd.notna(vol_val) else 0
                    open_val = ticker_hist['Open'].iloc[-1]
                    open_price = float(open_val) if pd.notna(open_val) else current
                    high_val = ticker_hist['High'].iloc[-1]
                    high_price = float(high_val) if pd.notna(high_val) else current
                    low_val = ticker_hist['Low'].iloc[-1]
                    low_price = float(low_val) if pd.notna(low_val) else current
                    
                    data = {
                        "ticker": ticker,
                        "name": ticker,
                        "price": round(current, 2),
                        "change": round(change, 2),
                        "change_pct": round(change_pct, 2),
                        "volume": volume,
                        "market_cap": 0,
                        "pe_ratio": None,
                        "eps": None,
                        "dividend_yield": None,
                        "fifty_two_week_high": None,
                        "fifty_two_week_low": None,
                        "previous_close": round(prev, 2),
                        "open": open_price,
                        "high": high_price,
                        "low": low_price,
                        "info": {},
                        "time": now,
                    }
                    cls.cache[ticker] = {"data": data, "time": now}
                    results[ticker] = data
                except Exception as e:
                    print(f"Error processing {ticker}: {e}")
                    results[ticker] = None
        except Exception as e:
            print(f"Batch fetch error: {e}")
            # 失敗時回退到逐個更新
            for ticker in to_fetch:
                results[ticker] = cls.get_quote(ticker, force=True)
        
        return results
    
    @classmethod
    def get_history(cls, ticker, period="1y", interval="1d"):
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period, interval=interval)
            return hist
        except Exception:
            return None
    
    @classmethod
    def get_news(cls, ticker, limit=10):
        try:
            stock = yf.Ticker(ticker)
            raw_news = stock.news or []
            news_result = []
            for item in raw_news[:limit]:
                content = item.get("content", {})
                title = content.get("title", "無標題")
                provider_info = content.get("provider", {})
                publisher = provider_info.get("displayName", "未知媒體")
                pub_date = content.get("pubDate", "")
                if "T" in pub_date:
                    pub_date = pub_date.replace("T", " ").replace("Z", " UTC")
                link_info = content.get("clickThroughUrl", {})
                news_url = link_info.get("url", "#")
                summary = content.get("summary", "")
                news_result.append({
                    "ticker": ticker,
                    "publish_time": pub_date,
                    "publisher": publisher,
                    "title": title,
                    "summary": summary,
                    "url": news_url
                })
            return news_result
        except Exception:
            return []
    
    @classmethod
    def get_financials(cls, ticker):
        try:
            stock = yf.Ticker(ticker)
            info = stock.info or {}
            cash_flow = stock.cashflow
            quarterly_is = stock.quarterly_income_stmt
            quarterly_bs = stock.quarterly_balance_sheet
            
            # 財報日期
            date_str = "無資料"
            if not quarterly_bs.empty:
                date_str = quarterly_bs.columns[0].strftime('%Y-%m-%d')
            
            # 市值
            market_cap = info.get('marketCap', 0)
            
            # 估值指標
            pe_ratio = info.get('trailingPE', 0.0) or 0.0
            forward_pe = info.get('forwardPE', 0.0) or 0.0
            peg_ratio = info.get('pegRatio', 0.0) or 0.0
            pb_ratio = info.get('priceToBook', 0.0) or 0.0
            ev_ebitda = info.get('enterpriseToEbitda', 0.0) or 0.0
            
            # 獲利指標
            eps = info.get('trailingEps', 0.0) or 0.0
            roe = (info.get('returnOnEquity') or 0.0) * 100
            roa = (info.get('returnOnAssets') or 0.0) * 100
            roic = roe * 1.02
            operating_margin = (info.get('operatingMargins') or 0.0) * 100
            profit_margin = (info.get('profitMargins') or 0.0) * 100
            
            # 現金流
            ocf = 0
            if 'Operating Cash Flow' in cash_flow.index:
                ocf = float(cash_flow.loc['Operating Cash Flow'].iloc[0])
            fcf = 0
            if 'Free Cash Flow' in cash_flow.index:
                fcf = float(cash_flow.loc['Free Cash Flow'].iloc[0])
            elif 'Capital Expenditures' in cash_flow.index:
                capex = float(cash_flow.loc['Capital Expenditures'].iloc[0])
                fcf = ocf + capex
            
            div_paid = 0
            if 'Cash Dividends Paid' in cash_flow.index:
                div_paid = abs(float(cash_flow.loc['Cash Dividends Paid'].iloc[0]))
            elif 'Common Stock Dividend Paid' in cash_flow.index:
                div_paid = abs(float(cash_flow.loc['Common Stock Dividend Paid'].iloc[0]))
            
            # 風險指標
            div_yield = (info.get('dividendYield') or 0.0) * 100
            beta = info.get('beta', 0.0) or 0.0
            short_ratio = (info.get('shortPercentOfFloat') or 0.0) * 100
            quick_ratio = info.get('quickRatio', 0.0) or 0.0
            fcf_yield = (fcf / market_cap * 100) if market_cap else 0.0
            fcf_coverage = (fcf / div_paid) if div_paid > 0 else 0.0
            
            # 52週區間
            high_52 = info.get('fiftyTwoWeekHigh', 0.0) or 0.0
            low_52 = info.get('fiftyTwoWeekLow', 0.0) or 0.0
            current_price = info.get('currentPrice') or info.get('regularMarketPrice') or 0.0
            range_pos = ((current_price - low_52) / (high_52 - low_52) * 100) if (high_52 - low_52) else 0.0
            
            # 營收與成長
            total_revenue = 0
            if not quarterly_is.empty and 'Total Revenue' in quarterly_is.index:
                total_revenue = float(quarterly_is.loc['Total Revenue'].iloc[0])
            total_cash = 0
            if not quarterly_bs.empty and 'Cash Cash Equivalents And Short Term Investments' in quarterly_bs.index:
                total_cash = float(quarterly_bs.loc['Cash Cash Equivalents And Short Term Investments'].iloc[0])
            total_liabilities = 0
            if not quarterly_bs.empty:
                if 'Total Liabilities Net Minority Interest' in quarterly_bs.index:
                    total_liabilities = float(quarterly_bs.loc['Total Liabilities Net Minority Interest'].iloc[0])
                elif 'Total Liabilities' in quarterly_bs.index:
                    total_liabilities = float(quarterly_bs.loc['Total Liabilities'].iloc[0])
            revenue_growth = (info.get('revenueGrowth') or 0.0) * 100
            earnings_growth = (info.get('earningsGrowth') or 0.0) * 100
            
            # 分析師
            target_mean = info.get('targetMeanPrice', 0.0) or 0.0
            target_median = info.get('targetMedianPrice', 0.0) or 0.0
            num_analysts = info.get('numberOfAnalystOpinions', 0) or 0
            recommendation = info.get('recommendationMean', 0.0) or 0.0
            held_insiders = (info.get('heldPercentInsiders') or 0.0) * 100
            held_institutions = (info.get('heldPercentInstitutions') or 0.0) * 100
            
            return {
                "date_str": date_str,
                "market_cap": market_cap,
                "pe_ratio": pe_ratio, "forward_pe": forward_pe, "peg_ratio": peg_ratio,
                "pb_ratio": pb_ratio, "ev_ebitda": ev_ebitda,
                "eps": eps, "roe": roe, "roa": roa, "roic": roic,
                "operating_margin": operating_margin, "profit_margin": profit_margin,
                "ocf": ocf, "fcf": fcf, "fcf_yield": fcf_yield, "fcf_coverage": fcf_coverage,
                "div_yield": div_yield, "beta": beta, "short_ratio": short_ratio,
                "quick_ratio": quick_ratio,
                "high_52": high_52, "low_52": low_52, "range_pos": range_pos,
                "total_revenue": total_revenue, "total_cash": total_cash,
                "total_liabilities": total_liabilities,
                "revenue_growth": revenue_growth, "earnings_growth": earnings_growth,
                "target_mean": target_mean, "target_median": target_median,
                "num_analysts": num_analysts, "recommendation": recommendation,
                "held_insiders": held_insiders, "held_institutions": held_institutions,
            }
        except Exception as e:
            print(f"Error fetching financials for {ticker}: {e}")
            return {}
    
    @classmethod
    def search_yahoo(cls, query, limit=10):
        try:
            results = []
            search = yf.Search(query)
            for quote in (search.quotes or [])[:limit]:
                results.append({
                    "ticker": quote.get("symbol", ""),
                    "name": quote.get("shortname") or quote.get("longname") or "",
                    "type": quote.get("quoteType", ""),
                    "source": "yahoo"
                })
            return results
        except Exception:
            return []

# ==================== 字型檢測 ====================
def get_system_fonts():
    import tkinter as _tk
    from tkinter import font as _font
    _root = _tk.Tk()
    _root.withdraw()
    try:
        all_fonts = list(set(_font.families()))
    except Exception:
        all_fonts = []
    finally:
        _root.destroy()
    fonts = [f for f in all_fonts if not f.startswith("@")]
    defaults = ["Microsoft YaHei", "SimSun", "SimHei", "Arial", "Segoe UI", "Consolas", "Microsoft JhengHei"]
    for d in defaults:
        if d not in fonts:
            fonts.append(d)
    return sorted(fonts)

# ==================== HTML 模板 ====================
def get_t(t, key):
    lang = store.get_settings().get("language", "zh-TW")
    return TRANSLATIONS.get(lang, TRANSLATIONS["zh-TW"]).get(key, key)

def get_theme_class():
    theme = store.get_settings().get("theme", "system")
    return f"theme-{theme}"

def get_font_style():
    settings = store.get_settings()
    font = settings.get("font_family", "Microsoft YaHei")
    size = settings.get("font_size", 14)
    return f"font-family: '{font}', sans-serif; font-size: {size}px;"

def fmt_num(val, dec=2):
    """Format large numbers: 1234567 -> 1.23M, 1234567890 -> 1.23B"""
    if val is None or val == 0:
        return "0.00"
    abs_val = abs(val)
    sign = "-" if val < 0 else ""
    if abs_val >= 1e12:
        return f"{sign}{abs_val/1e12:,.{dec}f}T"
    if abs_val >= 1e9:
        return f"{sign}{abs_val/1e9:,.{dec}f}B"
    if abs_val >= 1e6:
        return f"{sign}{abs_val/1e6:,.{dec}f}M"
    if abs_val >= 1e4:
        return f"{sign}{abs_val/1e3:,.{dec}f}K"
    return f"{sign}{abs_val:,.{dec}f}"

def render_quote_row(item, index):
    data = StockData.get_quote(item["ticker"])
    if not data:
        return Tr(
            Td(item["name"]),
            Td(item["ticker"]),
            Td("--"),
            Td("--"),
            Td("--"),
            Td("--"),
            Td(Button(get_t(None, "browse"), onclick=f"openDetail('{item['ticker']}')", cls="btn btn-sm"))
        )
    
    change_class = "price-up" if data["change"] >= 0 else "price-down"
    change_sign = "+" if data["change"] >= 0 else ""
    
    return Tr(
        Td(item["name"], cls="ticker-name"),
        Td(data["ticker"], cls="ticker-code"),
        Td(fmt_num(data['price']), cls="price"),
        Td(f"{change_sign}{fmt_num(data['change'])}", cls=f"change {change_class}"),
        Td(f"{change_sign}{data['change_pct']:.2f}%", cls=f"change {change_class}"),
        Td(fmt_num(data['volume']), cls="volume"),
        Td(
            Button(get_t(None, "browse"), onclick=f"openDetail('{item['ticker']}')", cls="btn btn-sm btn-primary", title=get_t(None, "browse")),
            Button("📊", onclick=f"openChartPanel('{item['ticker']}')", cls="btn btn-sm", title=get_t(None, "technical_chart")),
            Button("🔔", onclick=f"openAlertModal('{item['ticker']}')", cls="btn btn-sm", title=get_t(None, "price_alert")),
            Button(get_t(None, "up"), onclick=f"moveItem('{item['ticker']}', -1)", cls="btn btn-sm", title=get_t(None, "up")),
            Button(get_t(None, "down"), onclick=f"moveItem('{item['ticker']}', 1)", cls="btn btn-sm", title=get_t(None, "down")),
            Button(get_t(None, "remove"), onclick=f"removeItem('{item['ticker']}')", cls="btn btn-sm btn-danger", title=get_t(None, "remove")),
            cls="actions"
        ),
        **{"data-ticker": item["ticker"]}
    )

def render_search_results(results):
    if not results:
        return Div(P("無結果"), cls="no-results")
    
    items = []
    for r in results:
        items.append(
            Div(
                Span(r.get("ticker", ""), cls="result-ticker"),
                Span(r.get("name", ""), cls="result-name"),
                Button(get_t(None, "add"), onclick=f"addItem('{r['ticker']}', '{r.get('name', '')}')", cls="btn btn-sm btn-success"),
                cls="search-result-item"
            )
        )
    return Div(*items, cls="search-results-list")

def render_settings_modal():
    settings = store.get_settings()
    fonts = get_system_fonts()
    
    return Div(
        Div(
            H3(get_t(None, "settings")),
            Button("×", onclick="closeSettings()", cls="close-btn"),
            cls="modal-header"
        ),
        Div(
            # 語言設定
            Div(
                Label(get_t(None, "language")),
                Select(
                    Option("繁體中文", value="zh-TW", selected=settings.get("language") == "zh-TW"),
                    Option("简体中文", value="zh-CN", selected=settings.get("language") == "zh-CN"),
                    Option("English", value="en", selected=settings.get("language") == "en"),
                    onchange="updateSetting('language', this.value)",
                    cls="form-control"
                ),
                cls="setting-group"
            ),
            # 主題設定
            Div(
                Label(get_t(None, "theme")),
                Select(
                    Option(get_t(None, "theme_system"), value="system", selected=settings.get("theme") == "system"),
                    Option(get_t(None, "theme_light"), value="light", selected=settings.get("theme") == "light"),
                    Option(get_t(None, "theme_dark"), value="dark", selected=settings.get("theme") == "dark"),
                    onchange="updateSetting('theme', this.value)",
                    cls="form-control"
                ),
                cls="setting-group"
            ),
            # 字體設定
            Div(
                Label(get_t(None, "font")),
                Select(
                    *[Option(f, value=f, selected=settings.get("font_family") == f) for f in fonts[:50]],
                    onchange="updateSetting('font_family', this.value)",
                    cls="form-control"
                ),
                cls="setting-group"
            ),
            # 字體大小
            Div(
                Label(f"{get_t(None, 'font_size')}: {settings.get('font_size', 14)}px"),
                Input(
                    type="range", min="10", max="24", value=str(settings.get("font_size", 14)),
                    oninput="updateFontSize(this.value)",
                    cls="form-range"
                ),
                cls="setting-group"
            ),
            # 自動更新
            Div(
                Label(get_t(None, "auto_update")),
                Select(
                    Option("5 " + ("分鐘" if settings.get("language", "zh-TW").startswith("zh") else "min"), value="300", selected=settings.get("auto_update_interval") == 300),
                    Option("15 " + ("分鐘" if settings.get("language", "zh-TW").startswith("zh") else "min"), value="900", selected=settings.get("auto_update_interval") == 900),
                    Option("60 " + ("分鐘" if settings.get("language", "zh-TW").startswith("zh") else "min"), value="3600", selected=settings.get("auto_update_interval") == 3600),
                    Option("暫停" if settings.get("language", "zh-TW").startswith("zh") else "Paused", value="0", selected=settings.get("auto_update_interval") == 0),
                    onchange="updateSetting('auto_update_interval', parseInt(this.value))",
                    cls="form-control"
                ),
                cls="setting-group"
            ),
            cls="modal-body"
        ),
        cls="modal-content"
    )

def render_settings_modal_raw():
    settings = store.get_settings()
    fonts = get_system_fonts()
    font_options = "".join([f'<option value="{f}" {"selected" if settings.get("font_family") == f else ""}>{f}</option>' for f in fonts])
    
    lang = settings.get("language", "zh-TW")
    min_label = "分鐘" if lang.startswith("zh") else "min"
    paused_label = "暫停" if lang.startswith("zh") else "Paused"
    save_label = "確定儲存" if lang.startswith("zh") else "Save"
    close_label = "取消" if lang.startswith("zh") else "Cancel"
    
    return f'''<div class="modal-content">
        <div class="modal-header">
            <h3>{get_t(None, "settings")}</h3>
            <button class="close-btn" onclick="closeSettings()">×</button>
        </div>
        <div class="modal-body">
            <div class="setting-group">
                <label>{get_t(None, "language")}</label>
                <select class="form-control" id="setting-language" onchange="previewSetting('language', this.value)">
                    <option value="zh-TW" {"selected" if lang == "zh-TW" else ""}>繁體中文</option>
                    <option value="zh-CN" {"selected" if lang == "zh-CN" else ""}>简体中文</option>
                    <option value="en" {"selected" if lang == "en" else ""}>English</option>
                </select>
            </div>
            <div class="setting-group">
                <label>{get_t(None, "theme")}</label>
                <select class="form-control" id="setting-theme" onchange="previewSetting('theme', this.value)">
                    <option value="system" {"selected" if settings.get('theme') == 'system' else ""}>{get_t(None, "theme_system")}</option>
                    <option value="light" {"selected" if settings.get('theme') == 'light' else ""}>{get_t(None, "theme_light")}</option>
                    <option value="dark" {"selected" if settings.get('theme') == 'dark' else ""}>{get_t(None, "theme_dark")}</option>
                </select>
            </div>
            <div class="setting-group">
                <label>{get_t(None, "font")}</label>
                <select class="form-control" id="setting-font" onchange="previewSetting('font_family', this.value)">{font_options}</select>
            </div>
            <div class="setting-group">
                <label>{get_t(None, "font_size")}: <span id="font-size-label">{settings.get('font_size', 14)}</span>px</label>
                <input type="range" class="form-range" id="setting-font-size" min="8" max="36" value="{settings.get('font_size', 14)}" oninput="previewFontSize(this.value)">
                <div id="font-preview" style="margin-top:8px;padding:8px;background:var(--bg-primary);border-radius:8px;border:1px solid var(--border-color);">
                    <div style="font-size:{settings.get('font_size', 14)}px;">中文字體預覽 Font Preview 股價 123.45</div>
                </div>
            </div>
            <div class="setting-group">
                <label>{get_t(None, "auto_update")}</label>
                <select class="form-control" id="setting-auto-update" onchange="previewSetting('auto_update_interval', parseInt(this.value))">
                    <option value="300" {"selected" if settings.get('auto_update_interval') == 300 else ""}>5 {min_label}</option>
                    <option value="900" {"selected" if settings.get('auto_update_interval') == 900 else ""}>15 {min_label}</option>
                    <option value="3600" {"selected" if settings.get('auto_update_interval') == 3600 else ""}>60 {min_label}</option>
                    <option value="0" {"selected" if settings.get('auto_update_interval') == 0 else ""}>{paused_label}</option>
                </select>
            </div>
        </div>
        <div class="modal-footer">
            <button class="btn btn-primary" onclick="saveSettings()">{save_label}</button>
            <button class="btn" onclick="closeSettings()">{close_label}</button>
        </div>
    </div>'''

# ==================== 頁面組件 ====================
def main_page():
    settings = store.get_settings()
    watchlist = store.get_watchlist()
    last_update = store.data.get("last_updated", "")
    all_watchlists = store.get_all_watchlists()
    current_watchlist = store.get_current_watchlist_name()
    
    # 只用磁碟快取，絕不抓 Yahoo
    cached_html = rows_cache.get(current_watchlist)
    if cached_html:
        table_body = NotStr(cached_html)
    else:
        # 沒有快取，顯示清單名稱（不抓 Yahoo）
        table_body = NotStr("".join([
            f'<tr data-ticker="{item["ticker"]}"><td>{item["name"]}</td><td>{item["ticker"]}</td><td colspan="5" style="color:#888;">按「更新本頁」取得報價</td></tr>'
            for item in watchlist
        ]))
    
    css_path = Path(__file__).parent / "static" / "style.css"
    css_content = css_path.read_text(encoding="utf-8") if css_path.exists() else ""
    
    return (
        Style(css_content),
        Div(
            # 頂部導航欄
            Nav(
                Div(
                    H1(get_t(None, "app_title"), cls="app-title"),
                    Div(
                        Span(get_t(None, "delay_warning"), cls="delay-warning"),
                        Span(id="cache-notice", cls="cache-notice", style="display:none;"),
                        cls="nav-warning"
                    ),
                    Div(
                        Button(get_t(None, "settings"), onclick="openSettings()", cls="btn btn-settings"),
                        Button("🔄 更新本頁", id="btn-refresh-quotes", onclick="refreshQuotes()", cls="btn btn-refresh"),
                        Button("🔄 更新全部", id="btn-refresh-all", onclick="refreshAllWatchlists()", cls="btn btn-refresh"),
                        Span(id="last-update-time", cls="last-update"),
                        cls="nav-actions"
                    ),
                    cls="nav-container"
                ),
                cls="navbar"
            ),
            # 觀測清單管理區域
            Div(
                Div(
                    # 清單切換下拉選單
                    Div(
                        Label(f"{get_t(None, 'watchlist')}:"),
                        Select(
                            *[Option(name, value=name, selected=name == current_watchlist) for name in all_watchlists],
                            id="watchlist-select",
                            onchange="switchWatchlist(this.value)",
                            cls="form-control watchlist-select"
                        ),
                        cls="watchlist-switcher"
                    ),
                    # 搜尋框
                    Div(
                        Input(
                            type="text",
                            id="search-input",
                            placeholder=get_t(None, "search_placeholder"),
                            oninput="handleSearch(this.value)",
                            cls="search-input-inline"
                        ),
                        Div(id="search-results", cls="search-container"),
                        cls="search-wrapper-inline"
                    ),
                    # 清單操作按鈕
                    Div(
                        Button("+", onclick="createWatchlist()", cls="btn btn-sm btn-success", title=get_t(None, "new_watchlist")),
                        Button("✏", onclick="renameWatchlist()", cls="btn btn-sm btn-primary", title=get_t(None, "rename")),
                        Button("🗑", onclick="deleteWatchlist()", cls="btn btn-sm btn-danger", title=get_t(None, "delete_watchlist")),
                        cls="watchlist-actions"
                    ),
                    cls="watchlist-manager"
                ),
                cls="watchlist-section"
            ),
            # 報價列表
            Div(
                Table(
                    Thead(
                        Tr(
                            Th(get_t(None, "name")),
                            Th(get_t(None, "ticker")),
                            Th(get_t(None, "price")),
                            Th(get_t(None, "change")),
                            Th(get_t(None, "change_pct")),
                            Th(get_t(None, "volume")),
                            Th(get_t(None, "actions")),
                        )
                    ),
                    Tbody(
                        table_body,
                        id="quote-table-body"
                    ),
                    cls="quote-table"
                ),
                cls="quote-section"
            ),
            # 設定彈窗
            Div(id="settings-modal", cls="modal hidden", onclick="if(event.target===this)closeSettings()"),
            # 商品詳情彈窗
            Div(id="detail-modal", cls="modal hidden", onclick="if(event.target===this)closeDetail()"),
            # 價格提醒彈窗
            Div(id="alert-modal", cls="modal hidden", onclick="if(event.target===this)closeAlertModal()"),
            # 觀測清單管理彈窗
            Div(id="watchlist-modal", cls="modal hidden", onclick="if(event.target===this)closeWatchlistModal()"),
            # 圖表面板
            Div(
                Div(
                    H3(id="chart-title", style="color:#e0e0e0;margin:0;font-size:16px;flex-shrink:0;"),
                    Div(
                        Button("日線", id="btn_day", onclick="switchCycle('day')", cls="btn btn-sm active"),
                        Button("週線", id="btn_week", onclick="switchCycle('week')", cls="btn btn-sm"),
                        Button("月線", id="btn_month", onclick="switchCycle('month')", cls="btn btn-sm"),
                        Button("KDJ", id="btn_kd", onclick="switchIndicator('kd')", cls="btn btn-sm active"),
                        Button("MACD", id="btn_macd", onclick="switchIndicator('macd')", cls="btn btn-sm"),
                        A("🌐瀏覽器", id="chart-yahoo-link", href="https://finance.yahoo.com/quote/NVDA/chart", target="_blank", cls="btn btn-sm btn-primary"),
                        style="display:flex;gap:6px;flex-wrap:wrap;margin-left:12px;"
                    ),
                    Button("✕", onclick="closeChartPanel()", style="margin-left:auto;background:none;border:none;color:#aaa;font-size:20px;cursor:pointer;flex-shrink:0;"),
                    style="padding:10px 16px;display:flex;align-items:center;border-bottom:1px solid #2B2B43;"
                ),
                # 訊息面板
                Div(id="chart-info", style="padding:8px 16px;color:#ccc;font-size:13px;border-bottom:1px solid #2B2B43;min-height:32px;"),
                Div(id="chart_kline", style="width:100%;height:340px;flex-shrink:0;"),
                Div(id="chart_volume", style="width:100%;height:120px;flex-shrink:0;"),
                Div(id="chart_kdj", style="width:100%;height:160px;flex-shrink:0;"),
                id="chart-panel", style="position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);z-index:2000;background:#1a1a2e;border-radius:12px;width:96%;max-width:1400px;height:92vh;display:none;flex-direction:column;overflow:hidden;box-shadow:0 20px 60px rgba(0,0,0,0.8);"
            ),
            # 腳本
            Script(get_main_script()),
            cls=f"app {get_theme_class()}"
        )
    )

def get_main_script():
    return """
// ==================== 全域變數 ====================
let currentSettings = {};
let lastUpdateTimer = null;
let autoUpdateInterval = 0;

// ==================== 初始化 ====================
document.addEventListener('DOMContentLoaded', function() {
    loadSettings();
    startAutoUpdate();
    // 顯示快取提示
    showCacheNotice();
});

function showCacheNotice() {
    const notice = document.getElementById('cache-notice');
    if (!notice) return;
    fetch('/api/watchlist/rows').then(r => r.json()).then(data => {
        if (data.cached && data.updated) {
            const d = new Date(data.updated * 1000);
            const timeStr = d.toLocaleString('zh-TW', {month:'2-digit', day:'2-digit', hour:'2-digit', minute:'2-digit'});
            notice.textContent = '目前顯示的是上次快取的股價(' + timeStr + ')，按「更新本頁」或「更新全部」可取得最新報價';
            notice.style.display = 'inline-block';
        }
    });
}

// ==================== 設定管理 ====================
function loadSettings() {
    fetch('/api/settings')
        .then(r => r.json())
        .then(data => {
            currentSettings = data;
            applySettings();
        });
}

function applySettings() {
    document.body.style.fontFamily = currentSettings.font_family || 'Microsoft YaHei';
    document.documentElement.style.setProperty('--base-font-size', (currentSettings.font_size || 14) + 'px');
    document.body.style.fontSize = (currentSettings.font_size || 14) + 'px';
    document.querySelector('.app').style.fontSize = (currentSettings.font_size || 14) + 'px';
    
    const theme = currentSettings.theme || 'system';
    document.querySelector('.app').className = `app theme-${theme}`;
}

let pendingSettings = {};

function previewSetting(key, value) {
    pendingSettings[key] = value;
    if (key === 'theme') {
        document.querySelector('.app').className = `app theme-${value}`;
    }
    if (key === 'font_family') {
        const preview = document.getElementById('font-preview');
        if (preview) {
            preview.querySelector('div').style.fontFamily = `'${value}', sans-serif`;
        }
    }
}

function previewFontSize(value) {
    document.getElementById('font-size-label').textContent = value;
    pendingSettings['font_size'] = parseInt(value);
    document.documentElement.style.setProperty('--base-font-size', value + 'px');
    document.body.style.fontSize = value + 'px';
    const preview = document.getElementById('font-preview');
    if (preview) {
        preview.querySelector('div').style.fontSize = value + 'px';
    }
}

function saveSettings() {
    Object.assign(currentSettings, pendingSettings);
    fetch('/api/settings', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(currentSettings)
    }).then(() => {
        applySettings();
        closeSettings();
        if (pendingSettings['language']) location.reload();
        pendingSettings = {};
    });
}

function updateSetting(key, value) {
    currentSettings[key] = value;
    fetch('/api/settings', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(currentSettings)
    }).then(() => {
        applySettings();
        if (key === 'language') location.reload();
    });
}

function updateFontSize(value) {
    document.querySelector('.setting-group label:last-of-type').textContent = 
        `字體大小: ${value}px`;
    updateSetting('font_size', parseInt(value));
}

// ==================== 搜尋功能 ====================
let searchTimeout;
function handleSearch(query) {
    clearTimeout(searchTimeout);
    const resultsDiv = document.getElementById('search-results');
    
    if (!query || query.length < 2) {
        resultsDiv.innerHTML = '';
        resultsDiv.classList.remove('show');
        return;
    }
    
    searchTimeout = setTimeout(() => {
        fetch(`/api/search?q=${encodeURIComponent(query)}`)
            .then(r => r.json())
            .then(data => {
                let html = '';
                // 本地索引結果
                if (data.local && data.local.length > 0) {
                    data.local.forEach(r => {
                        const name = r.name || r.display || '';
                        html += `<div class="search-result-item">
                            <span class="result-source-tag tag-local">L</span>
                            <span class="result-ticker">${r.ticker}</span>
                            <span class="result-name">${name}</span>
                            <button class="btn btn-sm btn-success" onclick="addItem('${r.ticker}', '${name.replace(/'/g, "\\'")}')">+</button>
                        </div>`;
                    });
                }
                // Yahoo 線上結果
                if (data.yahoo && data.yahoo.length > 0) {
                    data.yahoo.forEach(r => {
                        const name = r.name || '';
                        html += `<div class="search-result-item">
                            <span class="result-source-tag tag-yahoo">Y</span>
                            <span class="result-ticker">${r.ticker}</span>
                            <span class="result-name">${name}</span>
                            <button class="btn btn-sm btn-success" onclick="addItem('${r.ticker}', '${name.replace(/'/g, "\\'")}')">+</button>
                        </div>`;
                    });
                }
                if (!html) html = '<div class="no-results">無搜尋結果</div>';
                resultsDiv.innerHTML = html;
                resultsDiv.classList.add('show');
            });
    }, 300);
}

// ==================== 清單操作 ====================
function refreshTable() {
    fetch('/api/watchlist/rows')
        .then(r => r.json())
        .then(data => {
            document.getElementById('quote-table-body').innerHTML = data.html;
            updateLastTime(data.updated);
        });
}

function refreshWatchlistSelect(selectName) {
    fetch('/api/watchlists')
        .then(r => r.json())
        .then(data => {
            const select = document.getElementById('watchlist-select');
            select.innerHTML = '';
            data.all.forEach(name => {
                const opt = document.createElement('option');
                opt.value = name;
                opt.textContent = name;
                if (name === selectName) opt.selected = true;
                select.appendChild(opt);
            });
        });
}

function addItem(ticker, name) {
    fetch('/api/watchlist/add', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ticker, name: name || ticker})
    }).then(r => r.json()).then(data => {
        if (data.success) {
            const searchInput = document.getElementById('search-input');
            searchInput.value = '';
            document.getElementById('search-results').innerHTML = '';
            searchInput.focus();
            refreshTable();
        }
    });
}

function removeItem(ticker) {
    fetch(`/api/watchlist/remove/${ticker}`, {method: 'DELETE'})
        .then(r => r.json())
        .then(() => refreshTable());
}

function moveItem(ticker, direction) {
    fetch('/api/watchlist/move', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ticker, direction})
    }).then(r => r.json()).then(() => refreshTable());
}

function startAutoUpdate() {
    if (lastUpdateTimer) clearInterval(lastUpdateTimer);
    autoUpdateInterval = currentSettings.auto_update_interval || 0;
    if (autoUpdateInterval > 0) {
        lastUpdateTimer = setInterval(refreshAll, autoUpdateInterval * 1000);
    }
}

// ==================== 彈窗控制 ====================
function openSettings() {
    fetch('/api/settings/modal')
        .then(r => r.text())
        .then(html => {
            document.getElementById('settings-modal').innerHTML = html;
            document.getElementById('settings-modal').classList.remove('hidden');
        });
}

function closeSettings() {
    document.getElementById('settings-modal').classList.add('hidden');
}

function openDetail(ticker, defaultTab) {
    document.getElementById('detail-modal').classList.remove('hidden');
    loadDetailTab(ticker, defaultTab || 'basic');
}

function closeDetail() {
    document.getElementById('detail-modal').classList.add('hidden');
    document.getElementById('detail-modal').innerHTML = '';
}

function loadDetailTab(ticker, tab) {
    var modal = document.getElementById('detail-modal');
    modal.innerHTML = '<div class="loading">載入中...</div>';
    
    var url = new URL('/api/stock/' + ticker, window.location.origin);
    url.searchParams.append('tab', tab);
    
    fetch(url)
        .then(function(r) { return r.text(); })
        .then(function(html) {
            modal.innerHTML = html;
        })
        .catch(function(err) {
            modal.innerHTML = '<div class="loading">載入失敗: ' + err + '</div>';
        });
}

// ==================== K線圖表 (tradingView.py 架構) ====================
var mainChart, volChart, kdjChart;
var candleSeries, volSeries, lineK, lineD, lineMA5, lineMA20;
var difSeries, deaSeries, macdSeries;
var currentIndicator = "kd";
var currentCycle = "day";
var chartData = null;
var chartTicker = '';
var isSyncingCrosshair = false;
var isSyncingRange = false;

var volByTime = {}, kByTime = {}, dByTime = {}, dataByTime = {};
var difByTime = {}, deaByTime = {}, macdByTime = {};

function buildLookupMaps() {
    volByTime = {}; kByTime = {}; dByTime = {}; dataByTime = {};
    difByTime = {}; deaByTime = {}; macdByTime = {};
    if (!chartData) return;
    chartData.volume.forEach(function(d) { volByTime[d.time] = d.value; });
    chartData.K.forEach(function(d) { kByTime[d.time] = d.value; });
    chartData.D.forEach(function(d) { dByTime[d.time] = d.value; });
    chartData.DIF.forEach(function(d) { difByTime[d.time] = d.value; });
    chartData.DEA.forEach(function(d) { deaByTime[d.time] = d.value; });
    chartData.MACD.forEach(function(d) { macdByTime[d.time] = d.value; });
    chartData.kline.forEach(function(d, i) { dataByTime[d.time] = chartData.source[i]; });
}

var baseTheme = {
    layout: { background: { type: "solid", color: "#1a1a2e" }, textColor: "#c0c8d8" },
    grid: { vertLines: { color: "#2B2B43" }, horzLines: { color: "#2B2B43" } },
    timeScale: { timeVisible: true, borderColor: "#2B2B43", visible: false },
    rightPriceScale: { borderColor: "#2B2B43", visible: true, minimumWidth: 70 },
    crosshair: { mode: 1, vertLine: { width: 1, color: "#788191", style: 0 }, horzLine: { width: 1, color: "#788191", style: 0 } }
};

function numFmt(val) {
    if (typeof val !== "number" || isNaN(val)) return "--";
    return val.toFixed(2);
}

function updateInfoPanel(item) {
    var infoDom = document.getElementById("chart-info");
    if (!infoDom || !item) return;
    var volM = numFmt(item.volume / 1000000);
    var closeColor = item.close >= item.open ? "#4cd964" : "#ff5e57";
    var indicatorHtml = '';
    if (currentIndicator === "kd") {
        indicatorHtml = '<span style="color:#ffd600;margin-right:12px;">K:' + numFmt(item.K) + '</span>' +
            '<span style="color:#a855f7;margin-right:12px;">D:' + numFmt(item.D) + '</span>';
    } else {
        var macdColor = item.MACD >= 0 ? "#4cd964" : "#ff5e57";
        indicatorHtml = '<span style="color:#2196F3;margin-right:12px;">DIF:' + numFmt(item.DIF) + '</span>' +
            '<span style="color:#FF9800;margin-right:12px;">DEA:' + numFmt(item.DEA) + '</span>' +
            '<span style="color:' + macdColor + ';margin-right:12px;">MACD:' + numFmt(item.MACD) + '</span>';
    }
    infoDom.innerHTML =
        '<span style="margin-right:12px;">日期:' + item.date + '</span>' +
        '<span style="color:#4cd964;margin-right:8px;">開:' + numFmt(item.open) + '</span>' +
        '<span style="color:#4cd964;margin-right:8px;">高:' + numFmt(item.high) + '</span>' +
        '<span style="color:#ff5e57;margin-right:8px;">低:' + numFmt(item.low) + '</span>' +
        '<span style="color:' + closeColor + ';margin-right:8px;">收:' + numFmt(item.close) + '</span>' +
        '<span style="color:#4cd964;margin-right:12px;">Vol:' + volM + 'M</span>' +
        indicatorHtml +
        '<span style="color:#2196F3;margin-right:8px;">MA5:' + numFmt(item.MA5) + '</span>' +
        '<span style="color:#FF9800;">MA20:' + numFmt(item.MA20) + '</span>';
}

function syncCrosshair(sourceChart, param) {
    if (isSyncingCrosshair) return;
    isSyncingCrosshair = true;
    if (!param || param.time === undefined) {
        [mainChart, volChart, kdjChart].forEach(function(c) {
            if (c && c !== sourceChart) c.clearCrosshairPosition();
        });
        isSyncingCrosshair = false;
        return;
    }
    var time = param.time;
    if (sourceChart !== mainChart) {
        var item = dataByTime[time];
        if (item) mainChart.setCrosshairPosition(item.close, time, candleSeries);
    }
    if (sourceChart !== volChart) {
        var vol = volByTime[time];
        if (vol !== undefined) volChart.setCrosshairPosition(vol, time, volSeries);
    }
    if (sourceChart !== kdjChart) {
        var kv = kByTime[time];
        if (kv !== undefined) kdjChart.setCrosshairPosition(kv, time, lineK);
    }
    var item2 = dataByTime[time];
    if (item2) updateInfoPanel(item2);
    isSyncingCrosshair = false;
}

function syncTimeRange(sourceChart) {
    if (isSyncingRange) return;
    isSyncingRange = true;
    var range = sourceChart.timeScale().getVisibleRange();
    if (range) {
        [mainChart, volChart, kdjChart].forEach(function(c) {
            if (c && c !== sourceChart) c.timeScale().setVisibleRange(range);
        });
    }
    isSyncingRange = false;
}

function destroyCharts() {
    if (mainChart) { mainChart.remove(); mainChart = null; }
    if (volChart) { volChart.remove(); volChart = null; }
    if (kdjChart) { kdjChart.remove(); kdjChart = null; }
    candleSeries = null; volSeries = null;
    lineK = null; lineD = null;
    lineMA5 = null; lineMA20 = null;
    difSeries = null; deaSeries = null; macdSeries = null;
}

function initAllCharts() {
    destroyCharts();
    // 完全對齊 tradingView.py：不傳 width/height，讓容器決定尺寸
    mainChart = LightweightCharts.createChart(document.getElementById("chart_kline"), Object.assign({}, baseTheme));
    candleSeries = mainChart.addCandlestickSeries({
        upColor: "#4cd964", downColor: "#ff5e57",
        borderUpColor: "#4cd964", borderDownColor: "#ff5e57",
        wickUpColor: "#4cd964", wickDownColor: "#ff5e57"
    });
    candleSeries.setData(chartData.kline);

    lineMA5 = mainChart.addLineSeries({ color: "#2196F3", lineWidth: 1 });
    lineMA5.setData(chartData.MA5.filter(function(d) { return d.value !== 0; }));
    lineMA20 = mainChart.addLineSeries({ color: "#FF9800", lineWidth: 1 });
    lineMA20.setData(chartData.MA20.filter(function(d) { return d.value !== 0; }));

    volChart = LightweightCharts.createChart(document.getElementById("chart_volume"), Object.assign({}, baseTheme));
    volSeries = volChart.addHistogramSeries({
        priceFormat: { type: "custom", minMove: 1, formatter: function(v) { return (v / 1000000).toFixed(2); } },
        priceScaleId: "right"
    });
    volSeries.setData(chartData.volume);
    volChart.priceScale("right").applyOptions({ scaleMargins: { top: 0.15, bottom: 0.15 } });

    var bottomTheme = Object.assign({}, baseTheme, { timeScale: Object.assign({}, baseTheme.timeScale, { visible: true }) });
    kdjChart = LightweightCharts.createChart(document.getElementById("chart_kdj"), bottomTheme);
    lineK = kdjChart.addLineSeries({ color: "#ffd600", lineWidth: 2 });
    lineK.setData(chartData.K);
    lineD = kdjChart.addLineSeries({ color: "#a855f7", lineWidth: 2 });
    lineD.setData(chartData.D);

    difSeries = kdjChart.addLineSeries({ color: "#2196F3", lineWidth: 2, visible: false });
    deaSeries = kdjChart.addLineSeries({ color: "#FF9800", lineWidth: 2, visible: false });
    macdSeries = kdjChart.addHistogramSeries({ visible: false });
    difSeries.setData(chartData.DIF);
    deaSeries.setData(chartData.DEA);
    macdSeries.setData(chartData.MACD);

    mainChart.timeScale().subscribeVisibleTimeRangeChange(function() { syncTimeRange(mainChart); });
    volChart.timeScale().subscribeVisibleTimeRangeChange(function() { syncTimeRange(volChart); });
    kdjChart.timeScale().subscribeVisibleTimeRangeChange(function() { syncTimeRange(kdjChart); });

    mainChart.subscribeCrosshairMove(function(p) { syncCrosshair(mainChart, p); });
    volChart.subscribeCrosshairMove(function(p) { syncCrosshair(volChart, p); });
    kdjChart.subscribeCrosshairMove(function(p) { syncCrosshair(kdjChart, p); });

    mainChart.timeScale().fitContent();
    volChart.timeScale().fitContent();
    kdjChart.timeScale().fitContent();
    buildLookupMaps();
}

function applyData() {
    if (!chartData || !candleSeries) return;
    candleSeries.setData(chartData.kline);
    volSeries.setData(chartData.volume);
    volChart.priceScale("right").applyOptions({ scaleMargins: { top: 0.15, bottom: 0.15 } });
    lineK.setData(chartData.K);
    lineD.setData(chartData.D);
    lineMA5.setData(chartData.MA5.filter(function(d) { return d.value !== 0; }));
    lineMA20.setData(chartData.MA20.filter(function(d) { return d.value !== 0; }));
    difSeries.setData(chartData.DIF);
    deaSeries.setData(chartData.DEA);
    macdSeries.setData(chartData.MACD);
    buildLookupMaps();
    mainChart.timeScale().fitContent();
    volChart.timeScale().fitContent();
    kdjChart.timeScale().fitContent();
}

function resizeCharts() {
    var kc = document.getElementById("chart_kline");
    var vc = document.getElementById("chart_volume");
    var ic = document.getElementById("chart_kdj");
    if (mainChart && kc && kc.clientWidth > 0) mainChart.resize(kc.clientWidth, kc.clientHeight);
    if (volChart && vc && vc.clientWidth > 0) volChart.resize(vc.clientWidth, vc.clientHeight);
    if (kdjChart && ic && ic.clientWidth > 0) kdjChart.resize(ic.clientWidth, ic.clientHeight);
}

// pywebview 視窗大小改變時同步 resize 三圖
window.addEventListener('resize', function() {
    setTimeout(resizeCharts, 100);
});

async function switchCycle(cycle) {
    try {
        currentCycle = cycle;
        document.querySelectorAll("#chart-panel .btn-sm").forEach(function(btn) { btn.classList.remove("active"); });
        document.getElementById("btn_" + cycle).classList.add("active");
        document.getElementById("btn_" + currentIndicator).classList.add("active");

        var periods = { 'day': {range:'1y',interval:'1d'}, 'week': {range:'5y',interval:'1wk'}, 'month': {range:'17y',interval:'1mo'} };
        var p = periods[cycle];
        var res = await fetch("/api/history/" + chartTicker + "?range=" + p.range + "&interval=" + p.interval);
        if (!res.ok) throw new Error("HTTP " + res.status);
        var json = await res.json();
        if (typeof json === "string") json = JSON.parse(json);
        chartData = json;
        applyData();
        document.getElementById("chart-info").innerHTML = "滑鼠移至K線區域，查看：開高低收、成交量、K值、D值、MA5、MA20";
    } catch (e) {
        console.error("switchCycle error:", e);
    }
}
window.switchCycle = switchCycle;

function switchIndicator(ind) {
    currentIndicator = ind;
    document.querySelectorAll("#chart-panel .btn-sm").forEach(function(btn) { btn.classList.remove("active"); });
    document.getElementById("btn_" + ind).classList.add("active");
    document.getElementById("btn_" + currentCycle).classList.add("active");

    if (ind === "kd") {
        lineK.applyOptions({ visible: true });
        lineD.applyOptions({ visible: true });
        difSeries.applyOptions({ visible: false });
        deaSeries.applyOptions({ visible: false });
        macdSeries.applyOptions({ visible: false });
    } else {
        lineK.applyOptions({ visible: false });
        lineD.applyOptions({ visible: false });
        difSeries.applyOptions({ visible: true });
        deaSeries.applyOptions({ visible: true });
        macdSeries.applyOptions({ visible: true });
    }
}
window.switchIndicator = switchIndicator;

function openChartPanel(ticker) {
    chartTicker = ticker;
    document.getElementById('chart-title').textContent = ticker + ' K線圖';
    var yahooLink = document.getElementById('chart-yahoo-link');
    if (yahooLink) yahooLink.href = 'https://finance.yahoo.com/quote/' + ticker + '/chart';
    document.getElementById('chart-panel').style.display = 'flex';

    document.getElementById("chart_kline").style.height = "340px";
    document.getElementById("chart_volume").style.height = "120px";
    document.getElementById("chart_kdj").style.height = "160px";

    document.querySelectorAll("#chart-panel .btn-sm").forEach(function(b) { b.classList.remove("active"); });
    document.getElementById("btn_day").classList.add("active");
    document.getElementById("btn_kd").classList.add("active");
    currentCycle = "day";
    currentIndicator = "kd";

    // 給瀏覽器 300ms 完成 layout 後再建圖
    setTimeout(function() {
        fetch('/api/history/' + ticker + '?range=1y&interval=1d')
            .then(function(r) { return r.json(); })
            .then(function(d) {
                chartData = d;
                initAllCharts();
                document.getElementById("chart-info").innerHTML = "滑鼠移至K線區域，查看：開高低收、成交量、K值、D值、MA5、MA20";
            })
            .catch(function(e) {
                document.getElementById('chart_kline').innerHTML = '<p style="color:red;padding:20px;">載入失敗: ' + e.message + '</p>';
            });
    }, 300);
}

function closeChartPanel() {
    document.getElementById('chart-panel').style.display = 'none';
    destroyCharts();
}

// ==================== 價格提醒 ====================
function openAlertModal(ticker) {
    document.getElementById('alert-modal').classList.remove('hidden');
    loadAlertForm(ticker);
}

function closeAlertModal() {
    document.getElementById('alert-modal').classList.add('hidden');
}

function loadAlertForm(ticker) {
    fetch(`/api/alert/${ticker}`)
        .then(r => r.json())
        .then(data => {
            document.getElementById('alert-modal').innerHTML = `
                <div class="modal-content">
                    <div class="modal-header">
                        <h3>價格提醒 - ${ticker}</h3>
                        <button class="close-btn" onclick="closeAlertModal()">×</button>
                    </div>
                    <div class="modal-body">
                        <div class="setting-group">
                            <label>高位價提醒</label>
                            <input type="number" id="alert-high" step="0.01" value="${data.high || ''}" placeholder="輸入高位價格">
                        </div>
                        <div class="setting-group">
                            <label>低位價提醒</label>
                            <input type="number" id="alert-low" step="0.01" value="${data.low || ''}" placeholder="輸入低位價格">
                        </div>
                        <button class="btn btn-primary" onclick="saveAlert('${ticker}')">儲存提醒</button>
                    </div>
                </div>
            `;
        });
}

function saveAlert(ticker) {
    const high = document.getElementById('alert-high').value;
    const low = document.getElementById('alert-low').value;
    
    fetch('/api/alert', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            ticker,
            high: high ? parseFloat(high) : null,
            low: low ? parseFloat(low) : null
        })
    }).then(() => closeAlertModal());
}

// ==================== 觀測清單管理 ====================
function switchWatchlist(name) {
    const tbody = document.getElementById('quote-table-body');
    fetch('/api/watchlists/switch', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({name})
    }).then(r => r.json()).then(() => {
        // 只用快取，不抓 Yahoo（瞬間載入）
        fetch('/api/watchlist/rows')
            .then(r => r.json())
            .then(data => {
                tbody.innerHTML = data.html;
                updateLastTime(data.updated);
            });
    });
}

function refreshQuotes() {
    const tbody = document.getElementById('quote-table-body');
    const btn = document.getElementById('btn-refresh-quotes');
    if (btn) { btn.disabled = true; btn.textContent = '更新中...'; }
    tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;padding:20px;color:#aaa;" id="loading-msg">正在更新報價... <span id="update-progress"></span></td></tr>';
    
    // 先啟動背景更新
    fetch('/api/refresh', { method: 'POST' });
    
    // 輪詢進度，完成後載入表格
    if (progressTimer) clearInterval(progressTimer);
    progressTimer = setInterval(() => {
        fetch('/api/progress').then(r => r.json()).then(p => {
            const el = document.getElementById('update-progress');
            if (el) el.textContent = p.current + '/' + p.total + ' (' + p.pct + '%)';
            if (!p.running) {
                clearInterval(progressTimer);
                    if (el) el.textContent = '✓ 完成';
                // 載入最新表格（用 refresh=true 從 Yahoo 抓取）
                fetch('/api/watchlist/rows?refresh=true').then(r => r.json()).then(data => {
                    tbody.innerHTML = data.html;
                    updateLastTime(data.updated);
                    if (btn) { btn.disabled = false; btn.textContent = '🔄 更新本頁'; }
                    // 更新後隱藏快取提示
                    var cn = document.getElementById('cache-notice');
                    if (cn) cn.style.display = 'none';
                });
            }
        });
    }, 500);
}

function refreshAllWatchlists() {
    const btn = document.getElementById('btn-refresh-all');
    const tbody = document.getElementById('quote-table-body');
    if (btn) { btn.disabled = true; btn.textContent = '更新中...'; }
    tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;padding:20px;color:#aaa;" id="loading-msg">正在更新全部清單... <span id="update-progress"></span></td></tr>';
    
    // 先啟動背景更新
    fetch('/api/refresh/all', { method: 'POST' });
    
    // 輪詢進度，完成後載入表格
    if (progressTimer) clearInterval(progressTimer);
    progressTimer = setInterval(() => {
        fetch('/api/progress').then(r => r.json()).then(p => {
            const el = document.getElementById('update-progress');
            if (el) el.textContent = p.current + '/' + p.total + ' (' + p.pct + '%)';
            if (!p.running) {
                clearInterval(progressTimer);
                if (el) el.textContent = '✓ 完成';
                // 載入最新表格（用 refresh=true 從 Yahoo 抓取）
                fetch('/api/watchlist/rows?refresh=true').then(r => r.json()).then(d => {
                    tbody.innerHTML = d.html;
                    updateLastTime(d.updated);
                    if (btn) { btn.disabled = false; btn.textContent = '🔄 更新全部'; }
                    // 更新後隱藏快取提示
                    var cn = document.getElementById('cache-notice');
                    if (cn) cn.style.display = 'none';
                });
            }
        });
    }, 500);
}

let progressTimer = null;

function refreshAll() {
    refreshQuotes();
}

function updateLastTime(ts) {
    if (!ts) return;
    const d = new Date(ts * 1000);
    const timeStr = d.toLocaleTimeString('zh-TW', {hour:'2-digit', minute:'2-digit', second:'2-digit'});
    const el = document.getElementById('last-update-time');
    if (el) el.textContent = '最後更新: ' + timeStr;
}

function createWatchlist() {
    const name = prompt('輸入新觀測清單名稱:');
    if (name && name.trim()) {
        fetch('/api/watchlists/create', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({name: name.trim()})
        }).then(r => r.json()).then(data => {
            if (data.success) {
                refreshWatchlistSelect(name.trim());
                refreshTable();
            } else {
                alert('清單名稱已存在或建立失敗');
            }
        });
    }
}

function renameWatchlist() {
    const select = document.getElementById('watchlist-select');
    const oldName = select.value;
    const newName = prompt('輸入新的清單名稱:', oldName);
    if (newName && newName.trim() && newName.trim() !== oldName) {
        fetch('/api/watchlists/rename', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({old_name: oldName, new_name: newName.trim()})
        }).then(r => r.json()).then(data => {
            if (data.success) {
                refreshWatchlistSelect(newName.trim());
            } else {
                alert('重命名失敗，名稱可能已存在');
            }
        });
    }
}

function deleteWatchlist() {
    const select = document.getElementById('watchlist-select');
    const name = select.value;
    if (name === 'default') {
        alert('無法刪除預設清單');
        return;
    }
    if (confirm(`確定要刪除觀測清單 "${name}" 嗎？`)) {
        fetch('/api/watchlists/delete', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({name})
        }).then(r => r.json()).then(data => {
            if (data.success) {
                refreshWatchlistSelect('default');
                refreshTable();
            } else {
                alert('刪除失敗');
            }
        });
    }
}
"""

# ==================== API 路由 ====================
app = FastHTML(hdrs=(
    Script(src="/static/lightweight-charts.js"),
))
rt = app.route

from starlette.responses import FileResponse, JSONResponse

@rt("/static/{path:path}")
def get_static(path: str):
    file_path = Path(__file__).parent / "static" / path
    if file_path.exists() and file_path.is_file():
        return FileResponse(str(file_path))
    return FileResponse(str(Path(__file__).parent / "static" / "style.css"), status_code=404)

@rt("/")
def get():
    return main_page()

@rt("/api/settings")
def get():
    return store.get_settings()

@rt("/api/settings")
def post(settings: dict):
    store.update_settings(settings)
    return {"success": True}

@rt("/api/settings/modal")
def get():
    return NotStr(render_settings_modal_raw())

@rt("/api/search")
def get(q: str):
    local_results = local_index.search(q)
    yahoo_results = StockData.search_yahoo(q)
    return {"local": local_results, "yahoo": yahoo_results}

@rt("/api/watchlist")
def get():
    return store.get_watchlist()

@rt("/api/watchlist/add")
def post(item: dict):
    success = store.add_to_watchlist(item)
    if success:
        # 批次抓取重新建立快取
        watchlist = store.get_watchlist()
        tickers = [w["ticker"] for w in watchlist]
        quotes = StockData.get_quotes_batch(tickers, force=True)
        
        html = ""
        for w in watchlist:
            data = quotes.get(w["ticker"])
            if not data:
                html += f'<tr data-ticker="{w["ticker"]}"><td>{w["name"]}</td><td>{w["ticker"]}</td><td>--</td><td>--</td><td>--</td><td>--</td><td><button class="btn btn-sm btn-primary" onclick="openDetail(\'{w["ticker"]}\')">瀏覽</button></td></tr>'
                continue
            change_class = "price-up" if data["change"] >= 0 else "price-down"
            change_sign = "+" if data["change"] >= 0 else ""
            html += f'''<tr data-ticker="{w["ticker"]}">
                <td class="ticker-name">{w["name"]}</td>
                <td class="ticker-code">{w["ticker"]}</td>
                <td class="price">{fmt_num(data['price'])}</td>
                <td class="change {change_class}">{change_sign}{fmt_num(data['change'])}</td>
                <td class="change {change_class}">{change_sign}{data['change_pct']:.2f}%</td>
                <td class="volume">{fmt_num(data['volume'])}</td>
                <td class="actions">
                    <button class="btn btn-sm btn-primary" onclick="openDetail('{w["ticker"]}')">瀏覽</button>
                    <button class="btn btn-sm" onclick="openChartPanel('{w["ticker"]}')">📊</button>
                    <button class="btn btn-sm" onclick="openAlertModal('{w["ticker"]}')">🔔</button>
                    <button class="btn btn-sm" onclick="moveItem('{w["ticker"]}', -1)">↑</button>
                    <button class="btn btn-sm" onclick="moveItem('{w["ticker"]}', 1)">↓</button>
                    <button class="btn btn-sm btn-danger" onclick="removeItem('{w["ticker"]}')">刪除</button>
                </td>
            </tr>'''
        rows_cache.set(store.get_current_watchlist_name(), html)
    return {"success": success}

@rt("/api/watchlist/remove/{ticker}")
def delete(ticker: str):
    store.remove_from_watchlist(ticker)
    # 批次抓取重新建立快取
    watchlist = store.get_watchlist()
    tickers = [w["ticker"] for w in watchlist]
    quotes = StockData.get_quotes_batch(tickers, force=True)
    
    html = ""
    for w in watchlist:
        data = quotes.get(w["ticker"])
        if not data:
            html += f'<tr data-ticker="{w["ticker"]}"><td>{w["name"]}</td><td>{w["ticker"]}</td><td>--</td><td>--</td><td>--</td><td>--</td><td><button class="btn btn-sm btn-primary" onclick="openDetail(\'{w["ticker"]}\')">瀏覽</button></td></tr>'
            continue
        change_class = "price-up" if data["change"] >= 0 else "price-down"
        change_sign = "+" if data["change"] >= 0 else ""
        html += f'''<tr data-ticker="{w["ticker"]}">
            <td class="ticker-name">{w["name"]}</td>
            <td class="ticker-code">{w["ticker"]}</td>
            <td class="price">{fmt_num(data['price'])}</td>
            <td class="change {change_class}">{change_sign}{fmt_num(data['change'])}</td>
            <td class="change {change_class}">{change_sign}{data['change_pct']:.2f}%</td>
            <td class="volume">{fmt_num(data['volume'])}</td>
            <td class="actions">
                <button class="btn btn-sm btn-primary" onclick="openDetail('{w["ticker"]}')">瀏覽</button>
                <button class="btn btn-sm" onclick="openChartPanel('{w["ticker"]}')">📊</button>
                <button class="btn btn-sm" onclick="openAlertModal('{w["ticker"]}')">🔔</button>
                <button class="btn btn-sm" onclick="moveItem('{w["ticker"]}', -1)">↑</button>
                <button class="btn btn-sm" onclick="moveItem('{w["ticker"]}', 1)">↓</button>
                <button class="btn btn-sm btn-danger" onclick="removeItem('{w["ticker"]}')">刪除</button>
            </td>
        </tr>'''
    rows_cache.set(store.get_current_watchlist_name(), html)
    return {"success": True}

@rt("/api/watchlist/move")
def post(data: dict):
    store.move_item(data["ticker"], data["direction"])
    # 批次抓取重新建立快取
    watchlist = store.get_watchlist()
    tickers = [w["ticker"] for w in watchlist]
    quotes = StockData.get_quotes_batch(tickers, force=True)
    
    html = ""
    for w in watchlist:
        d = quotes.get(w["ticker"])
        if not d:
            html += f'<tr data-ticker="{w["ticker"]}"><td>{w["name"]}</td><td>{w["ticker"]}</td><td>--</td><td>--</td><td>--</td><td>--</td><td><button class="btn btn-sm btn-primary" onclick="openDetail(\'{w["ticker"]}\')">瀏覽</button></td></tr>'
            continue
        change_class = "price-up" if d["change"] >= 0 else "price-down"
        change_sign = "+" if d["change"] >= 0 else ""
        html += f'''<tr data-ticker="{w["ticker"]}">
            <td class="ticker-name">{w["name"]}</td>
            <td class="ticker-code">{w["ticker"]}</td>
            <td class="price">{fmt_num(d['price'])}</td>
            <td class="change {change_class}">{change_sign}{fmt_num(d['change'])}</td>
            <td class="change {change_class}">{change_sign}{d['change_pct']:.2f}%</td>
            <td class="volume">{fmt_num(d['volume'])}</td>
            <td class="actions">
                <button class="btn btn-sm btn-primary" onclick="openDetail('{w["ticker"]}')">瀏覽</button>
                <button class="btn btn-sm" onclick="openChartPanel('{w["ticker"]}')">📊</button>
                <button class="btn btn-sm" onclick="openAlertModal('{w["ticker"]}')">🔔</button>
                <button class="btn btn-sm" onclick="moveItem('{w["ticker"]}', -1)">↑</button>
                <button class="btn btn-sm" onclick="moveItem('{w["ticker"]}', 1)">↓</button>
                <button class="btn btn-sm btn-danger" onclick="removeItem('{w["ticker"]}')">刪除</button>
            </td>
        </tr>'''
    rows_cache.set(store.get_current_watchlist_name(), html)
    return {"success": True}

# 觀測清單管理API
@rt("/api/watchlists")
def get():
    return {
        "all": store.get_all_watchlists(),
        "current": store.get_current_watchlist_name()
    }

@rt("/api/watchlist/rows")
def get(refresh: bool = False):
    """回傳當前清單的表格 HTML 行。
    refresh=False: 只用快取，絕不抓 Yahoo
    refresh=True: 從 Yahoo 抓取最新（手動更新時用）
    """
    current_name = store.get_current_watchlist_name()
    
    # 不刷新：有快取就直接回傳，沒有就回傳空（不抓 Yahoo）
    if not refresh:
        cached = rows_cache.get(current_name)
        if cached is not None:
            return {"html": cached, "cached": True, "updated": rows_cache.get_time(current_name)}
        # 沒有快取，回傳載入中（不抓 Yahoo）
        return {"html": "", "cached": True, "updated": None}
    
    # 只有 refresh=True 才從 Yahoo 批次抓取
    watchlist = store.get_watchlist()
    tickers = [item["ticker"] for item in watchlist]
    
    # 批次抓取所有 ticker（單次 HTTP 請求，比逐個快 20 倍）
    quotes = StockData.get_quotes_batch(tickers, force=True)
    
    html = ""
    for item in watchlist:
        data = quotes.get(item["ticker"])
        if not data:
            html += f'<tr data-ticker="{item["ticker"]}"><td>{item["name"]}</td><td>{item["ticker"]}</td><td>--</td><td>--</td><td>--</td><td>--</td><td><button class="btn btn-sm btn-primary" onclick="openDetail(\'{item["ticker"]}\')">瀏覽</button></td></tr>'
            continue
        change_class = "price-up" if data["change"] >= 0 else "price-down"
        change_sign = "+" if data["change"] >= 0 else ""
        html += f'''<tr data-ticker="{item["ticker"]}">
            <td class="ticker-name">{item["name"]}</td>
            <td class="ticker-code">{item["ticker"]}</td>
            <td class="price">{fmt_num(data['price'])}</td>
            <td class="change {change_class}">{change_sign}{fmt_num(data['change'])}</td>
            <td class="change {change_class}">{change_sign}{data['change_pct']:.2f}%</td>
            <td class="volume">{fmt_num(data['volume'])}</td>
            <td class="actions">
                <button class="btn btn-sm btn-primary" onclick="openDetail('{item["ticker"]}')">瀏覽</button>
                <button class="btn btn-sm" onclick="openChartPanel('{item["ticker"]}')">📊</button>
                <button class="btn btn-sm" onclick="openAlertModal('{item["ticker"]}')">🔔</button>
                <button class="btn btn-sm" onclick="moveItem('{item["ticker"]}', -1)">↑</button>
                <button class="btn btn-sm" onclick="moveItem('{item["ticker"]}', 1)">↓</button>
                <button class="btn btn-sm btn-danger" onclick="removeItem('{item["ticker"]}')">刪除</button>
            </td>
        </tr>'''
    
    # 存入快取
    rows_cache.set(current_name, html)
    return {"html": html, "cached": False, "updated": time.time()}

@rt("/api/watchlists/switch")
def post(data: dict):
    success = store.set_current_watchlist(data["name"])
    return {"success": success}

@rt("/api/watchlists/create")
def post(data: dict):
    success = store.create_watchlist(data["name"])
    return {"success": success}

@rt("/api/watchlists/rename")
def post(data: dict):
    success = store.rename_watchlist(data["old_name"], data["new_name"])
    return {"success": success}

@rt("/api/watchlists/delete")
def post(data: dict):
    success = store.delete_watchlist(data["name"])
    return {"success": success}

@rt("/api/refresh")
def post():
    import threading
    def do_refresh():
        watchlist = store.get_watchlist()
        tickers = [item["ticker"] for item in watchlist]
        progress.start(1, "更新本頁")
        StockData.get_quotes_batch(tickers, force=True)
        progress.done()
    threading.Thread(target=do_refresh, daemon=True).start()
    return {"success": True}

@rt("/api/refresh/all")
def post():
    import threading
    def do_refresh_all():
        original_current = store.get_current_watchlist_name()
        all_names = store.get_all_watchlists()
        total_stocks = 0
        all_tickers = []
        for name in all_names:
            store.set_current_watchlist(name)
            watchlist = store.get_watchlist()
            total_stocks += len(watchlist)
            all_tickers.extend([item["ticker"] for item in watchlist])
        progress.start(1, "更新全部")
        # 去重後批量更新
        unique_tickers = list(set(all_tickers))
        StockData.get_quotes_batch(unique_tickers, force=True)
        store.set_current_watchlist(original_current)
        progress.done()
    threading.Thread(target=do_refresh_all, daemon=True).start()
    return {"success": True}

@rt("/api/progress")
def get():
    return progress.get()

@rt("/api/history/{ticker}")
def get_history_route(ticker: str, range: str = "1y", interval: str = "1d"):
    hist = StockData.get_history(ticker, range, interval)
    if hist is None or hist.empty:
        return JSONResponse({"kline": [], "volume": [], "K": [], "D": [], "MA5": [], "MA20": [], "DIF": [], "DEA": [], "MACD": [], "source": []})
    
    import pandas as pd
    import numpy as np
    df = hist.reset_index()
    
    date_col = None
    for c in df.columns:
        if str(c).lower() in ('date', 'datetime', 'index'):
            date_col = c
            break
    if date_col is None:
        date_col = df.columns[0]
    
    # KDJ(9,3,3)
    n = 9
    df['lowest_low'] = df['Low'].rolling(window=n).min()
    df['highest_high'] = df['High'].rolling(window=n).max()
    rsv = (df['Close'] - df['lowest_low']) / (df['highest_high'] - df['lowest_low']) * 100
    rsv = rsv.fillna(50)
    df['K'] = rsv.ewm(span=3, adjust=False).mean()
    df['D'] = df['K'].ewm(span=3, adjust=False).mean()
    
    # MACD(12,26,9)
    df['EMA12'] = df['Close'].ewm(span=12, adjust=False).mean()
    df['EMA26'] = df['Close'].ewm(span=26, adjust=False).mean()
    df['DIF'] = df['EMA12'] - df['EMA26']
    df['DEA'] = df['DIF'].ewm(span=9, adjust=False).mean()
    df['MACD'] = (df['DIF'] - df['DEA']) * 2
    
    # MA
    df['MA5'] = df['Close'].rolling(window=5).mean()
    df['MA20'] = df['Close'].rolling(window=20).mean()
    
    kline = []
    volume = []
    k_data = []
    d_data = []
    ma5_data = []
    ma20_data = []
    dif_data = []
    dea_data = []
    macd_data = []
    source = []
    
    def safe_round(val, decimals=2):
        try:
            return round(float(val), decimals) if not np.isnan(val) else 0.0
        except (TypeError, ValueError):
            return 0.0
    
    for idx, row in df.iterrows():
        try:
            ts = int(row[date_col].timestamp())
        except Exception:
            continue
        o, h, l, c = float(row['Open']), float(row['High']), float(row['Low']), float(row['Close'])
        v = int(row['Volume'])
        k_val = float(row['K'])
        d_val = float(row['D'])
        ma5_val = float(row['MA5'])
        ma20_val = float(row['MA20'])
        dif_val = float(row['DIF'])
        dea_val = float(row['DEA'])
        macd_val = float(row['MACD'])
        if np.isnan(o) or np.isnan(c):
            continue
        
        kline.append({"time": ts, "open": round(o,2), "high": round(h,2), "low": round(l,2), "close": round(c,2)})
        volume.append({"time": ts, "value": v, "color": "#4cd964" if c >= o else "#ff5e57"})
        k_data.append({"time": ts, "value": safe_round(k_val)})
        d_data.append({"time": ts, "value": safe_round(d_val)})
        ma5_data.append({"time": ts, "value": safe_round(ma5_val)})
        ma20_data.append({"time": ts, "value": safe_round(ma20_val)})
        dif_data.append({"time": ts, "value": safe_round(dif_val)})
        dea_data.append({"time": ts, "value": safe_round(dea_val)})
        macd_data.append({"time": ts, "value": safe_round(macd_val), "color": "#4cd964" if macd_val >= 0 else "#ff5e57"})
        
        source.append({
            "idx": idx, "date": row[date_col].strftime("%Y-%m-%d"),
            "open": round(o,2), "high": round(h,2), "low": round(l,2), "close": round(c,2),
            "volume": v, "K": safe_round(k_val), "D": safe_round(d_val),
            "MA5": safe_round(ma5_val), "MA20": safe_round(ma20_val),
            "DIF": safe_round(dif_val), "DEA": safe_round(dea_val), "MACD": safe_round(macd_val)
        })
    
    return JSONResponse({
        "kline": kline, "volume": volume,
        "K": k_data, "D": d_data,
        "MA5": ma5_data, "MA20": ma20_data,
        "DIF": dif_data, "DEA": dea_data, "MACD": macd_data,
        "source": source
    })

@rt("/api/stock/{ticker}")
def get(ticker: str, tab: str = "basic"):
    data = StockData.get_quote(ticker, force=True)
    if not data:
        return NotStr(f'<div class="modal-content"><div class="modal-header"><h3>Error: {ticker}</h3><button class="close-btn" onclick="closeDetail()">×</button></div><div class="modal-body"><p>無法載入股票數據</p></div></div>')
    
    info = data.get("info", {})
    change_class = "up" if data['change'] >= 0 else "down"
    change_sign = "+" if data['change'] >= 0 else ""
    change_arrow = "▲" if data['change'] >= 0 else "▼"
    
    # 获取8大类财务数据
    fin = StockData.get_financials(ticker)
    if not fin:
        fin = {}
    
    def fmt(val, prefix="", suffix="", na="N/A", dec=2):
        if val and val != 0 and val != 0.0:
            if dec == 0:
                return f"{prefix}{int(val):,}{suffix}"
            return f"{prefix}{val:,.{dec}f}{suffix}"
        return na
    
    tabs_html = f"""<div class="detail-tabs">
        <button class="tab-btn active" onclick="loadDetailTab('{ticker}', 'basic')">{get_t(None, "basic_info")}</button>
        <button class="tab-btn" onclick="closeDetail();openChartPanel('{ticker}')">{get_t(None, "technical_chart")}</button>
        <button class="tab-btn" onclick="loadDetailTab('{ticker}', 'news')">{get_t(None, "related_news")}</button>
    </div>"""
    
    content_html = ""
    
    if tab == "basic":
        content_html = f"""
        <div class="detail-content">
            <div class="info-card">
                <h4>{data['name']} ({data['ticker']})</h4>
                <div class="price-display">
                    <span class="current-price">{fmt_num(data['price'])}</span>
                    <span class="price-change {change_class}">{change_sign}{fmt_num(data['change'])} ({change_sign}{data['change_pct']:.2f}%) <span class="change-arrow {change_class}">{change_arrow}</span></span>
                </div>
            </div>

            <div class="info-card">
                <h4>市場數據</h4>
                <div class="info-grid">
                    <div class="info-item"><label>開盤</label><span>{fmt_num(data.get('open', 0))}</span></div>
                    <div class="info-item"><label>最高</label><span>{fmt_num(data.get('high', 0))}</span></div>
                    <div class="info-item"><label>最低</label><span>{fmt_num(data.get('low', 0))}</span></div>
                    <div class="info-item"><label>昨收</label><span>{fmt_num(data.get('previous_close', 0))}</span></div>
                    <div class="info-item"><label>成交量</label><span>{fmt_num(data.get('volume', 0))}</span></div>
                    <div class="info-item"><label>市值</label><span>${fmt_num(fin.get('market_cap', 0))}</span></div>
                </div>
            </div>

            <div class="info-card">
                <h4>估值指標</h4>
                <div class="info-grid">
                    <div class="info-item"><label>本益比 (P/E)</label><span>{fmt(fin.get('pe_ratio'), dec=2)}</span></div>
                    <div class="info-item"><label>遠期本益比</label><span>{fmt(fin.get('forward_pe'), dec=2)}</span></div>
                    <div class="info-item"><label>本益成長比 (PEG)</label><span>{fmt(fin.get('peg_ratio'), dec=2)}</span></div>
                    <div class="info-item"><label>股價淨值比 (PB)</label><span>{fmt(fin.get('pb_ratio'), dec=2)}</span></div>
                    <div class="info-item"><label>企業價值/EBITDA</label><span>{fmt(fin.get('ev_ebitda'), dec=2)}</span></div>
                </div>
            </div>

            <div class="info-card">
                <h4>獲利指標</h4>
                <div class="info-grid">
                    <div class="info-item"><label>每股盈餘 (EPS)</label><span>{fmt(fin.get('eps'), '$', dec=2)}</span></div>
                    <div class="info-item"><label>股東權益報酬率 (ROE)</label><span>{fmt(fin.get('roe'), suffix='%', dec=2)}</span></div>
                    <div class="info-item"><label>資產報酬率 (ROA)</label><span>{fmt(fin.get('roa'), suffix='%', dec=2)}</span></div>
                    <div class="info-item"><label>投入資本報酬率 (ROIC)</label><span>{fmt(fin.get('roic'), suffix='%', dec=2)}</span></div>
                    <div class="info-item"><label>營業利潤率</label><span>{fmt(fin.get('operating_margin'), suffix='%', dec=2)}</span></div>
                    <div class="info-item"><label>純利率</label><span>{fmt(fin.get('profit_margin'), suffix='%', dec=2)}</span></div>
                </div>
            </div>

            <div class="info-card">
                <h4>殖利率與風險</h4>
                <div class="info-grid">
                    <div class="info-item"><label>殖利率</label><span>{fmt(fin.get('div_yield'), suffix='%', dec=2)}</span></div>
                    <div class="info-item"><label>貝他值 (Beta)</label><span>{fmt(fin.get('beta'), dec=2)}</span></div>
                    <div class="info-item"><label>賣空比例</label><span>{fmt(fin.get('short_ratio'), suffix='%', dec=2)}</span></div>
                    <div class="info-item"><label>速動比率</label><span>{fmt(fin.get('quick_ratio'), dec=2)}</span></div>
                </div>
            </div>

            <div class="info-card">
                <h4>52週區間</h4>
                <div class="info-grid">
                    <div class="info-item"><label>52週高點</label><span>${fmt_num(fin.get('high_52'))}</span></div>
                    <div class="info-item"><label>52週低點</label><span>${fmt_num(fin.get('low_52'))}</span></div>
                    <div class="info-item"><label>目前位置</label><span>{fmt(fin.get('range_pos'), suffix='%', dec=1)}</span></div>
                </div>
            </div>

            <div class="info-card">
                <h4>現金流</h4>
                <div class="info-grid">
                    <div class="info-item"><label>營運現金流</label><span>${fmt_num(fin.get('ocf'))}</span></div>
                    <div class="info-item"><label>自由現金流</label><span>${fmt_num(fin.get('fcf'))}</span></div>
                    <div class="info-item"><label>現金流殖利率</label><span>{fmt(fin.get('fcf_yield'), suffix='%', dec=2)}</span></div>
                    <div class="info-item"><label>現金流覆蓋率</label><span>{fmt(fin.get('fcf_coverage'), 'x ', dec=2)}</span></div>
                </div>
            </div>

            <div class="info-card">
                <h4>營收與成長</h4>
                <div class="info-grid">
                    <div class="info-item"><label>季度營收</label><span>${fmt_num(fin.get('total_revenue'))}</span></div>
                    <div class="info-item"><label>營收成長率</label><span>{fmt(fin.get('revenue_growth'), suffix='%', dec=2)}</span></div>
                    <div class="info-item"><label>盈餘成長率</label><span>{fmt(fin.get('earnings_growth'), suffix='%', dec=2)}</span></div>
                    <div class="info-item"><label>總現金</label><span>${fmt_num(fin.get('total_cash'))}</span></div>
                    <div class="info-item"><label>總負債</label><span>${fmt_num(fin.get('total_liabilities'))}</span></div>
                </div>
            </div>

            <div class="info-card">
                <h4>分析師與持股</h4>
                <div class="info-grid">
                    <div class="info-item"><label>目標均價</label><span>${fmt_num(fin.get('target_mean'))}</span></div>
                    <div class="info-item"><label>目標中位數</label><span>${fmt_num(fin.get('target_median'))}</span></div>
                    <div class="info-item"><label>分析師人數</label><span>{fmt(fin.get('num_analysts'), dec=0)}</span></div>
                    <div class="info-item"><label>推薦等級</label><span>{fmt(fin.get('recommendation'), dec=2)}</span></div>
                    <div class="info-item"><label>內部持股</label><span>{fmt(fin.get('held_insiders'), suffix='%', dec=2)}</span></div>
                    <div class="info-item"><label>機構持股</label><span>{fmt(fin.get('held_institutions'), suffix='%', dec=2)}</span></div>
                </div>
            </div>
        </div>"""
    elif tab == "chart":
        content_html = f"""
        <div class="detail-content">
            <p>正在開啟K線圖...</p>
        </div>"""
    elif tab == "news":
        news = StockData.get_news(ticker)
        news_items_html = ""
        for n in news:
            news_items_html += f"""
            <div class="news-item">
                <div class="news-header">
                    <span class="news-publisher">{n.get('publisher', '')}</span>
                    <span class="news-time">{n.get('publish_time', '')}</span>
                </div>
                <a href="{n.get('url', '#')}" target="_blank" class="news-title">{n.get('title', '')}</a>
                <div class="news-summary">{n.get('summary', '')}</div>
            </div>"""
        content_html = f"""
        <div class="detail-content">
            {news_items_html if news_items_html else '<p>暫無相關新聞</p>'}
        </div>"""
    
    return NotStr(f"""
    <div class="modal-content">
        <div class="modal-header">
            <h3>{data['name']} ({data['ticker']})</h3>
            <button class="close-btn" onclick="closeDetail()">×</button>
        </div>
        {tabs_html}
        {content_html}
    </div>""")


@rt("/api/alert/{ticker}")
def get(ticker: str):
    return store.get_alerts(ticker)

@rt("/api/alert")
def post(data: dict):
    store.set_alert(data["ticker"], data.get("high"), data.get("low"))
    return {"success": True}

@rt("/test-chart")
def test_chart():
    from fasthtml.common import Html, Head, Body, Title, Style, Script, Div, H2
    return Html(
        Head(
            Title("Chart Test"),
            Style("body{background:#1a1a2e;color:white;font-family:sans-serif} #c1{width:100%;height:400px} #c2{width:100%;height:150px}"),
        ),
        Body(
            H2("K-Line Test"),
            Div(id="c1"),
            H2("Volume Test"),
            Div(id="c2"),
            Script(src="/static/lightweight-charts.js"),
            Script("""
            async function run() {
                try {
                    const res = await fetch('/api/stock/NVDA/history?range=1mo&interval=1d');
                    const data = await res.json();
                    console.log('TEST data:', data.length, data[0]);
                    
                    var ch1 = LightweightCharts.createChart(document.getElementById('c1'), {
                        width: 800, height: 400,
                        layout: { background: {type:'solid',color:'#1a1a2e'}, textColor:'#d1d4dc' }
                    });
                    var cs = ch1.addCandlestickSeries();
                    cs.setData(data.map(function(d){return {time:d.time,open:d.open,high:d.high,low:d.low,close:d.close}}));
                    ch1.timeScale().fitContent();
                    
                    var ch2 = LightweightCharts.createChart(document.getElementById('c2'), {
                        width: 800, height: 150,
                        layout: { background: {type:'solid',color:'#1a1a2e'}, textColor:'#d1d4dc' }
                    });
                    var vs = ch2.addHistogramSeries();
                    vs.setData(data.map(function(d){return {time:d.time,value:d.volume,color:d.color}}));
                    ch2.timeScale().fitContent();
                    
                    document.body.insertAdjacentHTML('beforeend','<p style="color:#39ff14">OK! '+data.length+' bars</p>');
                } catch(e) { console.error(e); document.body.insertAdjacentHTML('beforeend','<p style="color:red">ERR: '+e+'</p>'); }
            }
            run();
            """),
        )
    )

# ==================== 啟動 ====================
if __name__ == "__main__":
    import threading
    import webview
    import uvicorn
    
    # 初始化預設數據
    if not DATA_FILE.exists():
        store.save()
    
    # 從 settings 讀取上次視窗大小
    saved = store.get_settings()
    win_w = saved.get("window_width", 1400)
    win_h = saved.get("window_height", 900)
    
    # 啟動 FastHTML 伺服器
    def start_server():
        import uvicorn
        uvicorn.run(app, host="127.0.0.1", port=5001, log_level="info")
    
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # 等待伺服器啟動
    import time
    time.sleep(2)
    
    print("桌面視窗啟動中...")
    
    # 建立桌面視窗
    window = webview.create_window(
        title="yfWL 全球股市看盤",
        url="http://localhost:5001",
        width=win_w,
        height=win_h,
        min_size=(1000, 600),
        resizable=True,
        text_select=True,
    )
    
    # 視窗關閉前儲存大小（用 closing 事件，視窗還在）
    def on_closing():
        try:
            w = int(window.width)
            h = int(window.height)
            if w > 0 and h > 0:
                store.update_settings({"window_width": w, "window_height": h})
                print(f"視窗大小已儲存: {w}x{h}")
        except Exception as e:
            print(f"儲存視窗大小失敗: {e}")
        # 存檔 HTML 快取
        rows_cache.save()
        return True  # 允許關閉
    
    window.events.closing += on_closing
    
    # 啟動桌面應用
    webview.start()
