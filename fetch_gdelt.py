"""GDELT 2.0 Events から世界の主要ニュースイベントを取得"""
import io
import re
import zipfile
import datetime
import requests

CAMEO_ROOT_LABELS = {
    '01': '声明・発表', '02': '要請・訴え', '03': '協力意向',
    '04': '協議',       '05': '外交協力',   '06': '物的協力',
    '07': '支援提供',   '08': '譲歩',       '09': '調査',
    '10': '要求',       '11': '批判・反対', '12': '拒否',
    '13': '脅迫',       '14': '抗議・デモ', '15': '軍事示威',
    '16': '関係縮小',   '17': '強制・圧力', '18': '武力行使',
    '19': '戦闘',       '20': '大量暴力',
}

CAMEO_DETAIL_LABELS = {
    '010': '公式声明',       '011': 'スピーチ',         '013': '報道発表',
    '020': '要請',           '040': '協議',             '041': '外相会談',
    '042': '首脳会談',       '100': '要求',             '101': '制裁要求',
    '110': '批判',           '111': '非難',             '112': '糾弾',
    '120': '拒否',           '130': '脅迫',             '131': '軍事脅迫',
    '132': '制裁脅迫',       '138': '核脅迫',           '140': '抗議デモ',
    '141': 'ストライキ',     '142': 'デモ行進',         '143': '暴力的抗議',
    '145': '暴動',           '150': '軍事力誇示',       '152': '軍事演習',
    '153': '軍事動員',       '155': 'ミサイル発射実験', '160': '外交縮小',
    '161': '大使召還',       '162': '制裁発動',         '163': '禁輸措置',
    '170': '強制',           '171': '封鎖',             '174': '暗殺未遂',
    '180': '武力行使',       '181': '拉致・誘拐',       '182': '暴行',
    '183': '爆撃・砲撃',     '185': '暗殺未遂',         '186': '暗殺',
    '190': '戦闘',           '191': '封鎖',             '192': '占領',
    '193': '小火器戦闘',     '194': '砲兵・戦車戦闘',  '195': '航空攻撃',
    '196': '停戦違反',       '200': '大量暴力',         '201': '大量虐殺',
}

# CAMEOルートコードでイベントをカテゴリに分類
def event_category(root):
    r = int(root) if root.isdigit() else 0
    if r >= 18: return 'conflict'
    if r >= 13: return 'tension'
    if r >= 10: return 'demand'
    return 'diplomatic'


def fetch_top_events(min_articles=5, max_events=150, hours=1):
    """GDELT 2.0 から直近 hours 時間分のイベントを取得、記事数順に返す"""
    print('📰  GDELT: 最新イベント取得中...')
    try:
        resp = requests.get(
            'http://data.gdeltproject.org/gdeltv2/lastupdate.txt', timeout=15
        )
        export_url = None
        for line in resp.text.strip().split('\n'):
            parts = line.strip().split(' ')
            if len(parts) == 3 and 'export' in parts[2]:
                export_url = parts[2]
                break
        if not export_url:
            print('   ⚠ GDELT: URL取得失敗')
            return []

        m = re.search(r'(\d{14})\.export', export_url)
        if not m:
            return []

        latest_dt = datetime.datetime.strptime(m.group(1), '%Y%m%d%H%M%S')
        base_url  = export_url[:export_url.index(m.group(1))]
        urls = [
            f'{base_url}{(latest_dt - datetime.timedelta(minutes=15*i)).strftime("%Y%m%d%H%M%S")}.export.CSV.zip'
            for i in range(hours * 4)
        ]

        events   = []
        seen_ids = set()

        for url in urls:
            try:
                r = requests.get(url, timeout=30)
                if r.status_code != 200:
                    continue
                with zipfile.ZipFile(io.BytesIO(r.content)) as zf:
                    with zf.open(zf.namelist()[0]) as f:
                        content = f.read().decode('utf-8', errors='replace')
                for line in content.split('\n'):
                    if not line.strip():
                        continue
                    row = line.split('\t')
                    if len(row) < 58:
                        continue
                    try:
                        event_id     = row[0]
                        num_articles = int(row[33]) if row[33] else 0
                        if event_id in seen_ids or num_articles < min_articles:
                            continue
                        seen_ids.add(event_id)
                        lat = float(row[56]) if row[56] else None
                        lon = float(row[57]) if row[57] else None
                        if lat is None or lon is None or (lat == 0 and lon == 0):
                            continue
                        code = row[26]
                        root = row[28]
                        events.append({
                            'event_id':     event_id,
                            'lat':          lat,
                            'lon':          lon,
                            'event_code':   code,
                            'event_label':  CAMEO_DETAIL_LABELS.get(code, CAMEO_ROOT_LABELS.get(root, code)),
                            'event_root':   root,
                            'root_label':   CAMEO_ROOT_LABELS.get(root, root),
                            'category':     event_category(root),
                            'goldstein':    float(row[30]) if row[30] else 0.0,
                            'num_articles': num_articles,
                            'avg_tone':     float(row[34]) if row[34] else 0.0,
                            'actor1':       (row[7] or row[6]).strip(),
                            'actor2':       (row[17] or row[16]).strip(),
                            'country':      row[53].strip(),
                            'location':     row[52].strip(),
                            'source_url':   row[60].strip() if len(row) > 60 else '',
                        })
                    except (ValueError, IndexError):
                        continue
            except Exception:
                continue

        events.sort(key=lambda e: e['num_articles'], reverse=True)
        top = events[:max_events]
        print(f'   → {len(top)} 件（記事数 {min_articles}以上）')
        return top

    except Exception as e:
        print(f'   ⚠ GDELT 取得失敗: {e}')
        return []
