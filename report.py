"""HTML レポート生成"""
import json


CATEGORY_COLOR = {
    'conflict':   '#e74c3c',
    'tension':    '#e67e22',
    'demand':     '#f1c40f',
    'diplomatic': '#3498db',
}

CATEGORY_LABEL = {
    'conflict':   '衝突・暴力',
    'tension':    '緊張・圧力',
    'demand':     '要求・批判',
    'diplomatic': '外交・協議',
}


def generate(events, summary, timestamp, descriptions=None):
    descriptions = descriptions or {}
    events_json  = json.dumps(events, ensure_ascii=False)
    summary_html = _summary_html(summary)
    cards_html   = _cards_html(events[:30], descriptions)

    return f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>World Monitor</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, sans-serif; background: #0f0f1a; color: #eee; }}
header {{ padding: 14px 16px; background: #16213e; border-bottom: 1px solid #2a2a4a;
          display: flex; align-items: center; gap: 10px; }}
header h1 {{ font-size: 17px; font-weight: 700; }}
.updated {{ font-size: 11px; color: #888; margin-left: auto; }}
.summary {{ padding: 14px 16px; background: #16213e; border-bottom: 1px solid #2a2a4a; }}
.summary-label {{ font-size: 11px; color: #888; margin-bottom: 8px; }}
.summary-body {{ font-size: 13px; color: #ccc; line-height: 1.75; white-space: pre-wrap; }}
#map {{ height: 45vh; }}
.legend {{ padding: 7px 14px; background: #16213e; border-bottom: 1px solid #2a2a4a;
           display: flex; flex-wrap: wrap; gap: 12px; font-size: 11px; color: #aaa; align-items: center; }}
.dot {{ width: 9px; height: 9px; border-radius: 50%; display: inline-block; margin-right: 3px; }}
.section-title {{ padding: 10px 16px 4px; font-size: 12px; color: #888; letter-spacing: 0.5px; }}
.cards {{ padding: 0 10px 16px; display: flex; flex-direction: column; gap: 8px; }}
.card {{ background: #16213e; border-radius: 10px; padding: 12px 14px;
         border-left: 3px solid #2a2a4a; }}
.card-top {{ display: flex; align-items: center; gap: 8px; margin-bottom: 6px; }}
.cat-badge {{ font-size: 10px; padding: 2px 7px; border-radius: 10px; color: #fff; white-space: nowrap; }}
.location {{ font-size: 13px; font-weight: 600; flex: 1; }}
.articles {{ font-size: 11px; color: #888; white-space: nowrap; }}
.event-label {{ font-size: 12px; color: #aaa; margin-bottom: 4px; }}
.desc {{ font-size: 13px; color: #ddd; margin-bottom: 4px; line-height: 1.5; }}
.actors {{ font-size: 11px; color: #666; }}
.source-link {{ display: inline-block; margin-top: 5px; font-size: 11px; color: #4fc3f7;
                text-decoration: none; overflow: hidden; text-overflow: ellipsis;
                white-space: nowrap; max-width: 100%; }}
footer {{ padding: 12px; font-size: 11px; color: #444; text-align: center; }}
</style>
</head>
<body>

<header>
  <span style="font-size:22px">🌍</span>
  <h1>World Monitor</h1>
  <span class="updated">更新: {timestamp}</span>
</header>

{summary_html}

<div id="map"></div>

<div class="legend">
  <span><span class="dot" style="background:#e74c3c"></span>衝突・暴力</span>
  <span><span class="dot" style="background:#e67e22"></span>緊張・圧力</span>
  <span><span class="dot" style="background:#f1c40f"></span>要求・批判</span>
  <span><span class="dot" style="background:#3498db"></span>外交・協議</span>
  <span style="color:#555;">｜ 円の大きさ = 記事数</span>
</div>

<div class="section-title">📋 記事数の多いイベント（上位30件）</div>
<div class="cards">{cards_html}</div>

<footer>データ: GDELT 2.0（約1時間遅延） · AI要約: Claude</footer>

<script>
const events = {events_json};

const renderer = L.canvas({{ padding: 0.5 }});
const map = L.map('map').setView([20, 10], 2);
L.tileLayer('https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}{{r}}.png', {{
  attribution: '&copy; OpenStreetMap &copy; CARTO'
}}).addTo(map);

const colors = {{ conflict:'#e74c3c', tension:'#e67e22', demand:'#f1c40f', diplomatic:'#3498db' }};

events.forEach(e => {{
  const color  = colors[e.category] || '#888';
  const radius = Math.min(4 + Math.log2(Math.max(e.num_articles, 1)) * 2, 16);
  L.circleMarker([e.lat, e.lon], {{
    radius, color, fillColor: color, fillOpacity: 0.6, weight: 1, renderer
  }}).bindPopup(
    `<b>${{e.event_label}}</b><br>${{e.location}}<br>` +
    `${{e.actor1}}${{e.actor2 ? ' / ' + e.actor2 : ''}}<br>` +
    `記事数: ${{e.num_articles}}　トーン: ${{e.avg_tone.toFixed(1)}}<br>` +
    (e.source_url ? `<a href="${{e.source_url}}" target="_blank" style="color:#88ccff">記事を開く</a>` : '')
  ).addTo(map);
}});
</script>
</body>
</html>'''


def _summary_html(summary):
    if not summary:
        return ''
    return f'''<div class="summary">
  <div class="summary-label">📝 AI生成ブリーフィング</div>
  <div class="summary-body">{summary}</div>
</div>'''


def _cards_html(events, descriptions):
    html = []
    for e in events:
        cat   = e.get('category', 'diplomatic')
        color = CATEGORY_COLOR.get(cat, '#888')
        label = CATEGORY_LABEL.get(cat, cat)
        loc   = e.get('location') or e.get('country') or '不明'
        a1    = e.get('actor1', '')
        a2    = e.get('actor2', '')
        actors_str = f'{a1} / {a2}' if a1 and a2 else (a1 or a2)
        src   = e.get('source_url', '')
        link  = f'<a class="source-link" href="{src}" target="_blank">🔗 記事を開く</a>' if src else ''
        desc  = descriptions.get(e['event_id'], '')
        desc_html = f'<div class="desc">{desc}</div>' if desc else ''

        html.append(f'''<div class="card" style="border-left-color:{color}">
  <div class="card-top">
    <span class="cat-badge" style="background:{color}">{label}</span>
    <span class="location">{loc}</span>
    <span class="articles">📄 {e["num_articles"]}</span>
  </div>
  {desc_html}
  <div class="actors">{actors_str}</div>
  {link}
</div>''')
    return '\n'.join(html)
