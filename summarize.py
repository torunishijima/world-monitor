"""Claude API を使って GDELT イベントを日本語でサマリー生成"""
import os
import anthropic

ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY', '')


def generate_summary(events):
    if not ANTHROPIC_API_KEY or not events:
        return ''

    top = sorted(events, key=lambda e: e.get('num_articles', 0), reverse=True)[:25]

    lines = []
    for e in top:
        lines.append(
            f"- {e.get('location', '?')} | {e.get('event_label', '?')} "
            f"| {e.get('actor1', '?')} / {e.get('actor2', '?')} "
            f"| 記事数:{e.get('num_articles', 0)} トーン:{e.get('avg_tone', 0):.1f} "
            f"| {e.get('source_url', '')}"
        )

    prompt = f"""あなたは国際情勢の専門アナリストです。
以下のGDELTデータをもとに、今この瞬間世界で何が起きているかを日本語で簡潔にまとめてください。

【直近1時間の主要イベント（記事数順）】
{chr(10).join(lines)}

【形式】
- 見出し（15文字以内）
- 重要ニュース3〜5件をそれぞれ2〜3文で
- 合計400〜600文字
- 日本語のみ・客観的な論調
- 見出しに絵文字を使う"""

    try:
        client  = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        message = client.messages.create(
            model='claude-haiku-4-5-20251001',
            max_tokens=1500,
            messages=[{'role': 'user', 'content': prompt}],
        )
        return message.content[0].text.strip()
    except Exception as e:
        print(f'   ⚠ Claude API 失敗: {e}')
        return ''
