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


def generate_event_descriptions(events):
    """上位イベントごとに日本語の詳細説明を生成。{event_id: description} を返す"""
    if not ANTHROPIC_API_KEY or not events:
        return {}

    top = sorted(events, key=lambda e: e.get('num_articles', 0), reverse=True)[:20]

    lines = []
    for i, e in enumerate(top):
        lines.append(
            f"{i+1}. [{e['event_id']}] {e.get('location','?')} | "
            f"{e.get('event_label','?')} | "
            f"{e.get('actor1','?')} / {e.get('actor2','?')} | "
            f"記事数:{e.get('num_articles',0)} トーン:{e.get('avg_tone',0):.1f}"
        )

    prompt = f"""以下のGDELTイベントそれぞれについて、国際情勢アナリストとして日本語で説明してください。

{chr(10).join(lines)}

【出力形式】
各イベントを「---N---」で区切って出力してください（Nは番号）。
各説明は3〜4文で：①何が起きたか ②なぜ重要か・背景 ③今後の影響。

例:
---1---
ウクライナ東部でロシア軍の砲撃が激化し、複数の民間人が犠牲になった。この地域は数ヶ月にわたる膠着状態が続いており、今回の攻勢は戦況を大きく変える可能性がある。欧米諸国は追加制裁を検討しており、今後の外交的対応が注目される。
---2---
..."""

    try:
        client  = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        message = client.messages.create(
            model='claude-haiku-4-5-20251001',
            max_tokens=3000,
            messages=[{'role': 'user', 'content': prompt}],
        )
        import re
        raw   = message.content[0].text.strip()
        parts = re.split(r'---\d+---', raw)
        descs = [p.strip() for p in parts if p.strip()]
        return {top[i]['event_id']: descs[i] for i in range(min(len(top), len(descs)))}
    except Exception as e:
        print(f'   ⚠ Claude API (descriptions) 失敗: {e}')
        return {}
