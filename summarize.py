"""Claude API を使って GDELT イベントをテーマ別ニュースレポートに変換"""
import os
import anthropic

ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY', '')


def generate_report(events):
    """GDELTイベントから世界情勢レポートを生成してHTMLで返す"""
    if not ANTHROPIC_API_KEY or not events:
        return '<p style="color:#888">データを取得できませんでした。</p>'

    top = sorted(events, key=lambda e: e.get('num_articles', 0), reverse=True)[:60]

    lines = []
    for e in top:
        lines.append(
            f"- {e.get('location','?')} | {e.get('event_label','?')} "
            f"| {e.get('actor1','?')} / {e.get('actor2','?')} "
            f"| 記事数:{e.get('num_articles',0)} トーン:{e.get('avg_tone',0):.1f} "
            f"| URL:{e.get('source_url','')}"
        )

    prompt = f"""あなたは国際情勢の専門アナリストです。
以下のGDELTデータ（直近1時間・記事数順）をもとに、世界の主要ニュースをテーマ別にまとめた日本語レポートを作成してください。

【GDELTデータ】
{chr(10).join(lines)}

【レポートの構成ルール】
1. 地域や話題が重複するイベントはひとつのトピックにまとめる
2. 記事数の多い重要なトピックを3〜6件選ぶ
3. 各トピックは以下の構成で書く：
   - トピック名（絵文字＋15文字以内）
   - 現在起きていること（2〜3文）
   - 背景・文脈（1〜2文）
   - 今後の見通し（1〜2文）
4. 日本語のみ・客観的な論調・合計1500〜2500文字

【出力形式】以下のHTMLを繰り返すだけで出力してください。前置き・タイトルブロック・説明文・余分なdivは一切不要です。

<div class="topic">
<h2>絵文字 トピック名</h2>
<div class="now"><span class="label">現在</span>本文テキスト</div>
<div class="bg"><span class="label">背景</span>本文テキスト</div>
<div class="outlook"><span class="label">見通し</span>本文テキスト</div>
</div>

このブロックをトピック数だけ繰り返してください。それ以外のHTMLは出力しないこと。"""

    try:
        client  = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        message = client.messages.create(
            model='claude-haiku-4-5-20251001',
            max_tokens=4000,
            messages=[{'role': 'user', 'content': prompt}],
        )
        return message.content[0].text.strip()
    except Exception as e:
        print(f'   ⚠ Claude API 失敗: {e}')
        return '<p style="color:#888">レポート生成に失敗しました。</p>'
