"""API 목록에 빠진 코리아둘레길 코스 찾기: 코스 번호(crsIdx) 범위를 차례로 받아 보고, GPX 안의 이름으로 어떤 코스인지 확인
   출력: data/koreatrail_probe.json {idx: {name, len, p}}"""
import json, re, time, urllib.request, sys
sys.path.insert(0, 'tools')
from gpx_fetch_lib import simplify, dist
known = {c['idx'] for c in json.load(open('data/koreatrail_urls.json'))}
out = {}
for n in list(range(4170, 4420)) + list(range(5110, 5420)):
    idx = 'T_CRS_MNG%010d' % n
    if idx in known: continue
    url = 'https://www.durunubi.kr/editImgUp.do?filePath=/data/koreamobility/course/summap/' + idx + '.gpx'
    try:
        x = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 bangguseok'}), timeout=30).read().decode('utf-8', 'ignore')
    except Exception as e:
        continue
    pts = [[float(a), float(b)] for a, b in re.findall(r'<trkpt[^>]*lat="([-\d.]+)"[^>]*lon="([-\d.]+)"', x)]
    if len(pts) < 2: continue
    names = re.findall(r'<name>(.*?)</name>', x)[:3]
    L = sum(dist(pts[i - 1], pts[i]) for i in range(1, len(pts)))
    out[idx] = {'names': names, 'head': x[:200], 'len': round(L), 'p': [[round(p[0], 5), round(p[1], 5)] for p in simplify(pts, 12)]}
    print(idx, names, round(L / 1000, 1))
    time.sleep(0.2)
json.dump(out, open('data/koreatrail_probe.json', 'w'), ensure_ascii=False, separators=(',', ':'))
print('FOUND', len(out))
