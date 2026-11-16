"""코리아둘레길 GPX를 받아 앱용으로 줄인 좌표 JSON을 만듦 (GitHub Actions에서 실행)
   입력: data/koreatrail_urls.json (두루누비 API 코스 목록에서 뽑은 GPX 주소 — 키 불필요)
   출력: data/koreatrail.json  {route: [{no, name, km, p: [[lat,lon],...]}]}"""
import json, re, math, time, urllib.request
src = json.load(open('data/koreatrail_urls.json'))
def dist(a, b):
    r = math.pi / 180; x = (b[1] - a[1]) * r * math.cos((a[0] + b[0]) / 2 * r); y = (b[0] - a[0]) * r
    return math.hypot(x, y) * 6371000
def seg_d(p, a, b):
    if a == b: return dist(p, a)
    k = math.cos(a[0] * math.pi / 180)
    ax, ay, bx, by, px, py = a[1] * k, a[0], b[1] * k, b[0], p[1] * k, p[0]
    t = max(0, min(1, ((px - ax) * (bx - ax) + (py - ay) * (by - ay)) / ((bx - ax) ** 2 + (by - ay) ** 2)))
    return dist(p, [ay + (by - ay) * t, (ax + (bx - ax) * t) / k])
def simplify(pts, tol):
    if len(pts) < 3: return pts
    keep = [False] * len(pts); keep[0] = keep[-1] = True; st = [(0, len(pts) - 1)]
    while st:
        i, j = st.pop(); best, bi = 0, -1
        for k in range(i + 1, j):
            d = seg_d(pts[k], pts[i], pts[j])
            if d > best: best, bi = d, k
        if best > tol: keep[bi] = True; st += [(i, bi), (bi, j)]
    return [p for p, kk in zip(pts, keep) if kk]
out, bad = {}, []
for c in src:
    try:
        req = urllib.request.Request(c['url'], headers={'User-Agent': 'Mozilla/5.0 bangguseok'})
        x = urllib.request.urlopen(req, timeout=60).read().decode('utf-8', 'ignore')
        pts = [[float(a), float(b)] for a, b in re.findall(r'<trkpt[^>]*lat="([-\d.]+)"[^>]*lon="([-\d.]+)"', x)]
        if not pts: pts = [[float(b), float(a)] for a, b in re.findall(r'<trkpt[^>]*lon="([-\d.]+)"[^>]*lat="([-\d.]+)"', x)]
        if len(pts) < 2: bad.append(c['name'] + ' (점 없음)'); continue
        L = sum(dist(pts[i - 1], pts[i]) for i in range(1, len(pts)))
        s = [[round(p[0], 5), round(p[1], 5)] for p in simplify(pts, 12)]
        out.setdefault(c['route'], []).append({'no': c['no'], 'name': c['name'], 'km': c['km'], 'len': round(L), 'p': s})
        print(c['name'], len(pts), '->', len(s), round(L / 1000, 1), 'km')
    except Exception as e:
        bad.append(c['name'] + ' (' + str(e)[:60] + ')')
    time.sleep(0.3)
for r in out: out[r].sort(key=lambda t: t['no'])
json.dump({'courses': out, 'bad': bad, 'made': time.strftime('%Y-%m-%d %H:%M')}, open('data/koreatrail.json', 'w'), ensure_ascii=False, separators=(',', ':'))
print('BAD', bad)
