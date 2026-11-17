# 짧은 코스: 손으로 찍은 지점들을 실제 걷는 길(오픈스트리트맵)로 이어 data/route/<id>.json 저장
# 1순위 OSRM(FOSSGIS) → 2순위 Valhalla(FOSSGIS). 결과 거리와 코스 공식 거리 비율도 기록
# 11/17: "mode": "bike" 인 코스는 자전거 길 기준(routed-bike / bicycle) · 이미 받은 파일은 다시 받지 않음("force": true 일 때만) — 폰에 저장된 노선이 바뀌지 않게
import json, urllib.request, urllib.parse, time, os, math
src = json.load(open('data/route_src.json'))
os.makedirs('data/route', exist_ok=True)
UA = {'User-Agent': 'bangguseok-runner/1.0 (github.com/tough835/bangguseok-runner)'}
def get(u):
    with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=60) as r: return json.load(r)
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
log = []
for c in src:
    if os.path.exists('data/route/%s.json' % c['id']) and not c.get('force'): continue
    bike = c.get('mode') == 'bike'
    pts = c['pts'][:]
    if c['loop'] and pts[0] != pts[-1]: pts.append(pts[0])
    res = None
    try:
        u = 'https://routing.openstreetmap.de/' + ('routed-bike' if bike else 'routed-foot') + '/route/v1/driving/' + ';'.join('%.5f,%.5f' % (q[1], q[0]) for q in pts) + '?overview=full&geometries=geojson'
        j = get(u); rt = j['routes'][0]; res = ('OSRM', rt['distance'], [[round(x[1], 6), round(x[0], 6)] for x in rt['geometry']['coordinates']])
    except Exception as e:
        log.append(c['id'] + ' OSRM ' + str(e)[:80])
        try:
            q = {'locations': [{'lat': x[0], 'lon': x[1], 'type': 'break_through'} for x in pts], 'costing': 'bicycle' if bike else 'pedestrian', 'directions_type': 'none'}
            j = get('https://valhalla1.openstreetmap.de/route?json=' + urllib.parse.quote(json.dumps(q)))
            co = []; [co.extend(poly6(l['shape'])) for l in j['trip']['legs']]
            res = ('Valhalla', j['trip']['summary']['length'] * 1000, co)
        except Exception as e2: log.append(c['id'] + ' Valhalla ' + str(e2)[:80])
    if res:
        how, dist, co = res
        json.dump({'p': co, 'km': round(dist / 1000, 2), 'how': how, 'src': '오픈스트리트맵 ' + ('자전거 ' if bike else '') + '길 찾기(' + how + ')'}, open('data/route/%s.json' % c['id'], 'w'), separators=(',', ':'))
        log.append('%s %s %.2fkm / 공식 %.2fkm (x%.2f) %d점' % (c['id'], how, dist / 1000, c['lengthM'] / 1000, dist / c['lengthM'], len(co)))
    time.sleep(1.5)
open('data/route/_log.txt', 'a').write('\n'.join(log) + '\n'); print('\n'.join(log))
