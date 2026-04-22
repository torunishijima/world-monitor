"""HTML レポート生成（テキスト記事形式）"""


def generate(events, report_html, timestamp):
    event_count  = len(events)
    top_articles = max((e.get('num_articles', 0) for e in events), default=0)

    return f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>World Monitor</title>
<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{
  font-family: -apple-system, BlinkMacSystemFont, 'Helvetica Neue', sans-serif;
  background: #f5f5f7;
  color: #1a1a1a;
  max-width: 680px;
  margin: 0 auto;
  padding: 0 16px 48px;
}}
header {{
  padding: 20px 0 14px;
  border-bottom: 2px solid #ddd;
  margin-bottom: 4px;
}}
header h1 {{ font-size: 20px; font-weight: 700; color: #111; }}
.meta {{ font-size: 12px; color: #888; margin-top: 5px; }}

/* Claudeが生成するHTML要素を強制的にスタイリング */
.topic, div[class="topic"] {{
  background: #fff;
  border-radius: 10px;
  padding: 18px;
  margin: 16px 0;
  border-left: 4px solid #0066cc;
  box-shadow: 0 1px 4px rgba(0,0,0,0.08);
}}
.topic h2, div[class="topic"] h2 {{
  font-size: 17px;
  font-weight: 700;
  color: #111;
  margin-bottom: 14px;
}}
.now, .bg, .outlook {{
  margin-bottom: 11px;
  font-size: 14px;
  line-height: 1.85;
  color: #222;
}}
.label {{
  display: inline-block;
  font-size: 10px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 4px;
  margin-right: 8px;
  vertical-align: middle;
  letter-spacing: 0.5px;
  color: #fff;
}}
.now .label     {{ background: #c0392b; }}
.bg .label      {{ background: #d68910; }}
.outlook .label {{ background: #1e8449; }}

footer {{
  padding: 24px 0;
  font-size: 11px;
  color: #aaa;
  text-align: center;
}}
</style>
</head>
<body>

<header>
  <h1>🌍 World Monitor</h1>
  <div class="meta">更新: {timestamp} · {event_count}件のイベントを分析（記事数最大: {top_articles}）</div>
</header>

{report_html}

<footer>データ: GDELT 2.0（約1時間遅延） · 分析: Claude AI · 毎時更新</footer>

</body>
</html>'''
