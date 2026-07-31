import yfinance
from datetime import datetime

def get_stock_news(ticker_symbol: str, limit: int = 10):
    """
    抓取個股Yahoo財經新聞（適配新版yfinance嵌套結構，不會出現None）
    :param ticker_symbol: 股票代碼 AAPL/NVDA/2330.TW/0700.HK
    :param limit: 最多抓取幾則新聞
    :return: 新聞清單 list[dict]
    """
    ticker = yfinance.Ticker(ticker_symbol)
    raw_news = ticker.news or []
    news_result = []

    for item in raw_news[:limit]:
        # 新版yfinance所有資訊都包在 content 子字典
        content = item.get("content", {})
        
        # 標題
        title = content.get("title", "無標題")
        # 新聞來源
        provider_info = content.get("provider", {})
        publisher = provider_info.get("displayName", "未知媒體")
        # 發布時間
        pub_date = content.get("pubDate", "")
        if "T" in pub_date:
            pub_date = pub_date.replace("T", " ").replace("Z", " UTC")
        # 新聞連結
        link_info = content.get("clickThroughUrl", {})
        news_url = link_info.get("url", "無連結")
        # 摘要
        summary = content.get("summary", "無摘要")

        news_result.append({
            "ticker": ticker_symbol,
            "publish_time": pub_date,
            "publisher": publisher,
            "title": title,
            "summary": summary,
            "url": news_url
        })
    return news_result

if __name__ == "__main__":
    # 可替換任意標的：AAPL, NVDA, 2330.TW, 0700.HK
    target_ticker = "NVDA"
    news_list = get_stock_news(target_ticker, limit=10)

    if not news_list:
        print(f"【{target_ticker}】無相關新聞")
    else:
        print(f"===== {target_ticker} 共 {len(news_list)} 則新聞 =====\n")
        for idx, news in enumerate(news_list, 1):
            print(f"第{idx}則")
            print(f"時間：{news['publish_time']}")
            print(f"來源：{news['publisher']}")
            print(f"標題：{news['title']}")
            print(f"摘要：{news['summary']}")
            print(f"連結：{news['url']}")
            print("-" * 70)