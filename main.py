"""World Monitor — GDELT で世界の主要ニュースを監視"""
import os
import datetime

from fetch_gdelt import fetch_top_events
from summarize import generate_summary
from report import generate


def main():
    timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')
    print(f'🌍 World Monitor  {timestamp}\n')

    events = fetch_top_events(min_articles=5, max_events=150, hours=1)
    if not events:
        print('⚠ イベントが取得できませんでした')

    print('\n📝 サマリー生成中...')
    summary = generate_summary(events)
    if summary:
        print(summary[:200] + '...')

    html = generate(events, summary, timestamp)
    os.makedirs('public', exist_ok=True)
    with open('public/index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print('\n✅ 完了: public/index.html')


if __name__ == '__main__':
    main()
