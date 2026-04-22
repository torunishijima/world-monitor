"""HTML レポート生成（テキスト記事形式）"""


def generate(events, report_html, timestamp):
    event_count = len(events)
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
  background: #0f0f1a;
  color: #e0e0e0;
  max-width: 680px;
  margin: 0 auto;
  padding: 0 16px 48px;
}}
header {{
  padding: 20px 0 14px;
  border-bottom: 1px solid #2a2a4a;
  margin-bottom: 8px;
}}
header h1 {{ font-size: 20px; font-weight: 700; color: #fff; }}
.meta {{
  font-size: 12px;
  color: #666;
  margin-top: 6px;
  display: flex;
  gap: 16px;
}}
.topic {{
  margin: 28px 0;
  padding-bottom: 28px;
  border-bottom: 1px solid #1e1e35;
}}
.topic:last-child {{ border-bottom: none; }}
.topic h2 {{
  font-size: 17px;
  font-weight: 700;
  color: #fff;
  margin-bottom: 14px;
  line-height: 1.4;
}}
.now, .bg, .outlook {{
  margin-bottom: 10px;
  font-size: 14px;
  line-height: 1.8;
  color: #ccc;
}}
.label {{
  display: inline-block;
  font-size: 10px;
  font-weight: 700;
  padding: 2px 7px;
  border-radius: 4px;
  margin-right: 8px;
  vertical-align: middle;
  letter-spacing: 0.5px;
}}
.now .label   {{ background: #1a3a5c; color: #5ab4ff; }}
.bg .label    {{ background: #2a2a1a; color: #c8a84b; }}
.outlook .label {{ background: #1a3a1a; color: #5aaf5a; }}
footer {{
  padding: 24px 0;
  font-size: 11px;
  color: #444;
  text-align: center;
}}
</style>
</head>
<body>

<header>
  <h1>🌍 World Monitor</h1>
  <div class="meta">
    <span>更新: {timestamp}</span>
    <span>イベント数: {event_count}件（記事数最大: {top_articles}）</span>
  </div>
</header>

{report_html}

<footer>データ: GDELT 2.0（約1時間遅延） · 分析: Claude AI · 毎時更新</footer>

</body>
</html>'''
