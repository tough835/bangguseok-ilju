/* 방구석러너 지도 저장 장치 (서비스 워커, 11/17)
   · 한 번 받은 자료를 폰에 저장해 다시 받지 않음 — 저장을 허락한 곳만:
     AWS 높이 자료(공개 자료) · OpenFreeMap(상업 이용·자체 저장 허용) · 우리 lib/·data/ 파일
   · 오픈스트리트맵 지도는 정책상 "다시 볼 때 저장"만 허용 → 30일까지 저장, 미리 받기는 안 함
   · 브이월드·Esri 위성 사진은 저장 허락이 확인되지 않아 저장하지 않음 (평소처럼 받음)
   · 최대 약 200MB(3,000장 남짓) — 넘으면 오래된 것부터 지움
   · index.html 같은 화면 파일은 건드리지 않음 (새 버전 확인이 그대로 되게) */
const TILES = 'bgr-tiles-v1', OWN = 'bgr-own-v1', MAX = 3000;
const KEEP = [/^https:\/\/s3\.amazonaws\.com\/elevation-tiles-prod\//, /^https:\/\/tiles\.openfreemap\.org\//];
const OSM = /^https:\/\/tile\.openstreetmap\.org\//, OSM_DAYS = 30;
const OWNP = /\/(lib|data)\/[^?]+\.(js|css|json)$/;
self.addEventListener('install', () => self.skipWaiting());
self.addEventListener('activate', e => e.waitUntil(self.clients.claim()));
self.addEventListener('fetch', e => {
  const q = e.request, u = q.url;
  if (q.method !== 'GET') return;
  if (KEEP.some(r => r.test(u))) e.respondWith(tile(q, 0));
  else if (OSM.test(u)) e.respondWith(tile(q, OSM_DAYS));
  else if (u.startsWith(self.location.origin) && OWNP.test(new URL(u).pathname)) e.respondWith(own(q, e));
});
async function tile(q, days){
  const c = await caches.open(TILES), hit = await c.match(q);
  if (hit && (!days || Date.now() - Date.parse(hit.headers.get('date') || 0) < days * 864e5)) return hit;
  try {
    const r = await fetch(q);
    if (r.ok && r.type !== 'opaque'){ await c.put(q, r.clone()); trim(c); }   // 크기를 알 수 없는 응답(opaque)은 저장하지 않음
    return r;
  } catch(err){ if (hit) return hit; throw err; }
}
let trimming = false;
async function trim(c){
  if (trimming) return; trimming = true;
  try { const k = await c.keys(); if (k.length > MAX) for (const x of k.slice(0, k.length - MAX + 100)) await c.delete(x); } catch(e){}
  trimming = false;
}
async function own(q, e){   // 저장본을 바로 주고, 뒤에서 새것으로 바꿔 둠 (파일이 바뀌어도 다음 번엔 새것)
  const c = await caches.open(OWN), hit = await c.match(q);
  const net = fetch(q).then(r => { if (r.ok) c.put(q, r.clone()); return r; }).catch(() => hit || Response.error());
  if (hit){ e.waitUntil(net); return hit; }
  return net;
}
