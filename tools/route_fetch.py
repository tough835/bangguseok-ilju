# 짧은 코스: 지점들을 실제 걷는 길(오픈스트리트맵)로 이어 data/route/<id>.json 저장
# 1순위 OSRM(FOSSGIS) → 2순위 Valhalla(FOSSGIS). 결과 거리와 코스 공식 거리 비율도 기록
# 11/17: "mode": "bike" 인 코스는 자전거 길 기준(routed-bike / bicycle) · 이미 받은 파일은 다시 받지 않음("force": true 일 때만) — 폰에 저장된 노선이 바뀌지 않게
# 11/20: 지점을 손으로 찍는 대신
#   "via":  ["이름", "이름A|이름B", [위도, 경도] …]  → 이름을 지도에서 찾아(Nominatim → Photon) 차례로 이음
#   "ring": "호수 이름A|이름B"                        → 호수 물가 윤곽을 받아 고르게 점을 찍고 한 바퀴 이음
#   "near": [위도, 경도], "box": 0.1                  → 이 근처에서만 찾음(같은 이름 다른 곳 방지)
#   결과 파일에 marks(거점 이름·위치 m) · elev(높이 m, Open-Meteo) 도 함께 저장
import json, urllib.request, urllib.parse, time, os, math, bisect
src = json.load(open('data/route_src.json', encoding='utf-8'))
os.makedirs('data/route', exist_ok=True)
UA = {'User-Agent': 'bangguseok-runner/1.0 (github.com/tough835/bangguseok-runner)'}
def get(u, data=None):
    with urllib.request.urlopen(urllib.request.Request(u, data=data, headers=UA), timeout=90) as r: return json.load(r)
def poly6(s):
    i = la = lo = 0; out = []
    while i < len(s):
        for k in range(2):
            sh = res = 0
            while True:
                b = ord(s[i]) - 63; i += 1; res |= (b & 0x1f) << sh; sh += 5
                if b < 0x20: break
            d = ~(res >> 1) if res & 1 else res >> 1
            if k == 0: la += d
            else: lo += d
        out.append([la / 1e6, lo / 1e6])
    return out
def hav(a, b):
    p = math.pi / 180; x = (b[1] - a[1]) * p * math.cos((a[0] + b[0]) / 2 * p); y = (b[0] - a[0]) * p
    return 6371000 * math.hypot(x, y)
def cumdist(co):
    c = [0.0]
    for i in range(len(co) - 1): c.append(c[-1] + hav(co[i], co[i + 1]))
    return c

log = []; glog = []
GEO_F = 'data/route/_geo.json'
try: GEO = json.load(open(GEO_F, encoding='utf-8'))
except Exception: GEO = {}

def nomi(q, near, box, poly=False):
    p = {'format': 'jsonv2', 'q': q, 'limit': '6', 'accept-language': 'ko'}
    if poly: p['polygon_geojson'] = '1'
    if near: p['viewbox'] = '%.4f,%.4f,%.4f,%.4f' % (near[1] - box, near[0] + box, near[1] + box, near[0] - box); p['bounded'] = '1'
    time.sleep(1.2)
    return get('https://nominatim.openstreetmap.org/search?' + urllib.parse.urlencode(p))
def photon(q, near):
    time.sleep(0.7)
    j = get('https://photon.komoot.io/api/?' + urllib.parse.urlencode({'q': q, 'lat': near[0], 'lon': near[1], 'limit': 6}))
    return [[f['geometry']['coordinates'][1], f['geometry']['coordinates'][0], (f.get('properties') or {}).get('name', '') or ''] for f in j.get('features', [])]
def find(name, near, box):   # 'A|B' → 먼저 찾아지는 이름. [위도, 경도, 찾은 이름, 표시 이름] 또는 None
    for q in name.split('|'):
        q = q.strip(); k = '%s@%.2f,%.2f' % (q, near[0], near[1])
        if k in GEO:
            if GEO[k]: return GEO[k][:2] + [q]
            continue
        hit = None; clean = True
        try:
            r = nomi(q, near, box)
            if r: hit = [round(float(r[0]['lat']), 6), round(float(r[0]['lon']), 6), 'N ' + (r[0].get('display_name') or '')[:70]]
        except Exception as e: clean = False; glog.append('  nominatim 실패 %s: %s' % (q, str(e)[:70]))
        if not hit:
            try:
                for la, lo, nm in photon(q, near):
                    if hav([la, lo], near) < box * 111000 * 1.3 and q.replace(' ', '') in nm.replace(' ', ''): hit = [round(la, 6), round(lo, 6), 'P ' + nm[:70]]; break
            except Exception as e: clean = False; glog.append('  photon 실패 %s: %s' % (q, str(e)[:70]))
        if hit or clean: GEO[k] = hit or 0
        glog.append('  %s → %s' % (q, hit if hit else '못 찾음'))
        if hit: return hit[:2] + [q]
    return None

def rings_of(gj):   # GeoJSON → 바깥 고리 [[위도, 경도] …] 목록
    t = gj.get('type'); c = gj.get('coordinates') or []
    if t == 'Polygon': return [[[y, x] for x, y in c[0]]] if c else []
    if t == 'MultiPolygon': return [[[y, x] for x, y in pg[0]] for pg in c if pg]
    return []
def perim(r): return sum(hav(r[i], r[i + 1]) for i in range(len(r) - 1)) if r and len(r) > 1 else 0
def stitch(ws):   # 조각 길들을 끝점끼리 이어 가장 긴 고리 하나
    ws = [w[:] for w in ws if len(w) > 1]; best = []
    while ws:
        r = ws.pop(0); grew = True
        while grew and r[0] != r[-1]:
            grew = False
            for i, w in enumerate(ws):
                if w[0] == r[-1]: r += w[1:]; ws.pop(i); grew = True; break
                if w[-1] == r[-1]: r += w[::-1][1:]; ws.pop(i); grew = True; break
                if w[-1] == r[0]: r = w[:-1] + r; ws.pop(i); grew = True; break
                if w[0] == r[0]: r = w[::-1][:-1] + r; ws.pop(i); grew = True; break
        if perim(r) > perim(best): best = r
    return best
def lake(names, near, box, want):   # 호수 윤곽 (고리, 둘레 m, 출처)
    best = None; ok = lambda pm: want * 0.4 <= pm <= want * 2.5
    for q in names.split('|'):
        try: res = nomi(q.strip(), near, box, poly=True)
        except Exception as e: glog.append('  nominatim(윤곽) 실패 %s: %s' % (q, str(e)[:70])); res = []
        for it in res:
            for r in rings_of(it.get('geojson') or {}):
                pm = perim(r); glog.append('  윤곽 후보 %s %s %s 둘레 %.0fm' % (q, it.get('category', ''), it.get('type', ''), pm))
                if ok(pm) and (best is None or abs(pm - want) < abs(best[1] - want)): best = (r, pm, 'Nominatim ' + (it.get('display_name') or '')[:50])
        if best: return best
    for q in names.split('|'):
        f = '["name"~"%s"](around:%d,%.5f,%.5f);' % (q.strip(), int(box * 111000), near[0], near[1])
        ql = '[out:json][timeout:50];(' + ''.join(t + k + f for t in ('way', 'relation') for k in ('["natural"="water"]', '["landuse"="reservoir"]', '["natural"="wetland"]')) + ');out geom;'
        j = None
        for host in ('https://overpass-api.de/api/interpreter', 'https://overpass.kumi.systems/api/interpreter'):
            try: time.sleep(2); j = get(host, ('data=' + urllib.parse.quote(ql)).encode()); break
            except Exception as e: glog.append('  overpass 실패 %s: %s' % (q, str(e)[:70]))
        for el in (j or {}).get('elements', []):
            if el.get('type') == 'way': r = [[g['lat'], g['lon']] for g in el.get('geometry') or []]
            else: r = stitch([[[g['lat'], g['lon']] for g in m.get('geometry') or []] for m in el.get('members') or [] if m.get('type') == 'way' and m.get('role') in ('outer', '')])
            pm = perim(r); glog.append('  윤곽 후보(overpass) %s 둘레 %.0fm' % ((el.get('tags') or {}).get('name', ''), pm))
            if ok(pm) and (best is None or abs(pm - want) < abs(best[1] - want)): best = (r, pm, 'Overpass ' + (el.get('tags') or {}).get('name', ''))
        if best: return best
    return None
def sample(r, n, start):   # 고리 위에 n개 점을 고르게 (start에 가장 가까운 곳부터)
    if r[0] != r[-1]: r = r + [r[0]]
    cum = cumdist(r); tot = cum[-1]
    off = cum[min(range(len(r)), key=lambda i: hav(r[i], start))]; out = []
    for k in range(n):
        d = (off + tot * k / n) % tot; j = min(max(bisect.bisect_right(cum, d) - 1, 0), len(r) - 2)
        seg = cum[j + 1] - cum[j]; t = (d - cum[j]) / seg if seg else 0
        out.append([round(r[j][0] + (r[j + 1][0] - r[j][0]) * t, 6), round(r[j][1] + (r[j + 1][1] - r[j][1]) * t, 6)])
    return out

def route(cid, pts, bike):   # (방법, 거리 m, [[위도, 경도] …]) 또는 None
    try:
        u = 'https://routing.openstreetmap.de/' + ('routed-bike' if bike else 'routed-foot') + '/route/v1/driving/' + ';'.join('%.5f,%.5f' % (q[1], q[0]) for q in pts) + '?overview=full&geometries=geojson'
        j = get(u); rt = j['routes'][0]; return ('OSRM', rt['distance'], [[round(x[1], 6), round(x[0], 6)] for x in rt['geometry']['coordinates']])
    except Exception as e:
        log.append(cid + ' OSRM ' + str(e)[:80])
        try:
            q = {'locations': [{'lat': x[0], 'lon': x[1], 'type': 'break_through'} for x in pts], 'costing': 'bicycle' if bike else 'pedestrian', 'directions_type': 'none'}
            j = get('https://valhalla1.openstreetmap.de/route?json=' + urllib.parse.quote(json.dumps(q)))
            co = []; [co.extend(poly6(l['shape'])) for l in j['trip']['legs']]
            return ('Valhalla', j['trip']['summary']['length'] * 1000, co)
        except Exception as e2: log.append(cid + ' Valhalla ' + str(e2)[:80])
    return None
def heights(co, cum):   # 길 따라 높이 [[m 지점, 해발 m] …] (Open-Meteo, 열쇠 없음)
    n = max(6, min(60, int(cum[-1] / 300) + 2))
    idx = sorted(set(min(bisect.bisect_left(cum, cum[-1] * k / (n - 1)), len(co) - 1) for k in range(n)))
    try:
        time.sleep(0.6)
        j = get('https://api.open-meteo.com/v1/elevation?latitude=' + ','.join('%.5f' % co[i][0] for i in idx) + '&longitude=' + ','.join('%.5f' % co[i][1] for i in idx))
        return [[round(cum[i]), round(h)] for i, h in zip(idx, j['elevation'])]
    except Exception as e: glog.append('  높이 실패: ' + str(e)[:70]); return None

for c in src:
    if os.path.exists('data/route/%s.json' % c['id']) and not c.get('force'): continue
    bike = c.get('mode') == 'bike'; extra = {}; named = []; res = None
    near = c.get('near'); box = c.get('box', 0.1)
    if c.get('ring') or c.get('via'): glog.append('[%s]' % c['id'])
    if c.get('ring'):
        lk = lake(c['ring'], near, box, c['lengthM'])
        if not lk: log.append(c['id'] + ' 호수 윤곽을 못 찾음'); continue
        ring, pm, how_ring = lk; n1 = max(8, min(36, round(pm / 250)))
        for n in (n1, max(6, n1 // 2)):
            r2 = route(c['id'], sample(ring, n, c.get('start') or near) + sample(ring, n, c.get('start') or near)[:1], bike); time.sleep(1.5)
            if r2 and (res is None or r2[1] < res[1]): res = r2; extra['ring'] = {'from': how_ring, 'perim': round(pm), 'n': n}
        named = [m for m in ((find(nm, near, box) or [None, None, nm]) for nm in c.get('marks', [])) if m[0] is not None]
    elif c.get('via'):
        pts = []
        for v in c['via']:
            if isinstance(v, str):
                f = find(v, near, box)
                if f: pts.append(f[:2]); named.append(f)
            else: pts.append(v)
        if len(pts) < 2: log.append(c['id'] + ' 지점을 2곳 이상 못 찾음'); continue
        if c['loop'] and pts[0] != pts[-1]: pts.append(pts[0])
        res = route(c['id'], pts, bike)
    else:
        pts = c['pts'][:]
        if c['loop'] and pts[0] != pts[-1]: pts.append(pts[0])
        res = route(c['id'], pts, bike)
    if res:
        how, dist, co = res
        out = {'p': co, 'km': round(dist / 1000, 2), 'how': how, 'src': '오픈스트리트맵 ' + ('자전거 ' if bike else '') + '길 찾기(' + how + ')'}
        if c.get('ring') or c.get('via'):
            cum = cumdist(co); marks = []; i0 = 0; seen = set()
            for la, lo, nm in named:
                rng = range(i0, len(co)) if c.get('via') else range(len(co))
                i = min(rng, key=lambda i: hav(co[i], [la, lo])); off = hav(co[i], [la, lo])
                if nm in seen or off > 400: continue
                seen.add(nm); marks.append([nm, round(cum[i]), la, lo, round(off)])
                if c.get('via'): i0 = i
            out['marks'] = marks; out.update(extra)
            el = heights(co, cum)
            if el: out['elev'] = el
        json.dump(out, open('data/route/%s.json' % c['id'], 'w', encoding='utf-8'), separators=(',', ':'), ensure_ascii=False)
        log.append('%s %s %.2fkm / 공식 %.2fkm (x%.2f) %d점%s' % (c['id'], how, dist / 1000, c['lengthM'] / 1000, dist / c['lengthM'], len(co), ' 거점 %d' % len(out.get('marks', [])) if 'marks' in out else ''))
    time.sleep(1.5)
json.dump(GEO, open(GEO_F, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
if glog: open('data/route/_geo.txt', 'a', encoding='utf-8').write('\n'.join(glog) + '\n')
open('data/route/_log.txt', 'a', encoding='utf-8').write('\n'.join(log) + '\n'); print('\n'.join(glog)); print('\n'.join(log))
