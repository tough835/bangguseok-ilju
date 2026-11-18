"""실제 지도 조각으로 방구석 테마 운동 화면을 찍음 (GitHub Actions 'shot.yml'에서만). 위성 3D · 그림 3D 두 장씩"""
import sys, os, time
from playwright.sync_api import sync_playwright

city, course = (sys.argv[1] if len(sys.argv) > 1 else "busan:haeundae-5k").split(":")
URL = "https://tough835.github.io/bangguseok-runner/index.html?notel"
os.makedirs("shots", exist_ok=True)

with sync_playwright() as p:
    b = p.chromium.launch(args=["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"])
    ctx = b.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=1.5, is_mobile=True, has_touch=True)
    ctx.add_init_script("setInterval(()=>{ try { V3D.hot=false; METER.hz.bad=0 } catch(e){} }, 300)")   # 시험 기계는 그래픽이 느려 과열 보호가 3D를 끔 → 시험에서만(새로 받아도 유지)
    page = ctx.new_page()
    logs = []
    page.on("console", lambda m: logs.append(m.type + ": " + m.text[:200]))
    import re
    def vw(route):   # 브이월드는 해외(깃허브 기계)에서 막힘 → 이 시험에서만 같은 칸의 Esri 사진으로 대신
        m = re.search(r"/Satellite/(\d+)/(\d+)/(\d+)", route.request.url)
        if not m: return route.continue_()
        r = ctx.request.get("https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/%s/%s/%s" % m.groups())
        route.fulfill(status=r.status, body=r.body(), headers={"content-type": "image/jpeg", "access-control-allow-origin": "*"})
    ctx.route("**/api.vworld.kr/**", vw)
    page.goto(URL); page.wait_for_timeout(4000)
    page.evaluate(f"()=>{{DB.zone='in'; DB.region=regionOf('{city}'); saveDB(); pickRoad('{city}','{course}')}}"); page.wait_for_timeout(4000)
    page.evaluate("()=>{const z=document.querySelector('[data-zone=in]'); if(z&&z.offsetParent) z.click()}"); page.wait_for_timeout(800)
    page.evaluate("()=>{const r=document.getElementById('resumeBox'); if(r&&!r.classList.contains('hidden')) document.getElementById('rsCancel').click(); setAct('tread')}")
    page.evaluate("()=>document.getElementById('bStart').click()"); page.wait_for_timeout(1500)
    page.evaluate("()=>{const r=document.getElementById('rsRestart'); if(r&&r.offsetParent) r.click()}")
    page.wait_for_timeout(3000)
    for at, sty in ((300, "toon"), (690, "toon"), (1760, "toon"), (4440, "toon")):
        page.evaluate(f"()=>advance({at} - (totalNow() % L))"); page.wait_for_timeout(500)
        if True:
            page.evaluate(f"()=>{{DB.v3d=true; DB.v3dSty='{'toon' if sty == 'toon' else 'sat'}'; saveDB(); v3dBtn(); if(V3D.ready) v3dStyle('{sty}')}}")
            t0 = time.time()
            while time.time() - t0 < 60:
                if page.evaluate("()=>!!(V3D.map && V3D.ready && V3D.map.areTilesLoaded())"): break
                page.wait_for_timeout(1000)
            page.wait_for_timeout(4000)
            page.screenshot(path=f"shots/{course}_{at}m_{sty}.png", timeout=180000, animations="disabled")
            print(at, sty, page.evaluate("()=>(V3D.props||[]).filter(p=>p.vis).map(p=>p.el.className+'@'+Math.round(p.at)).join(' ')"), page.evaluate("()=>[V3D.el, V3D.sty, Math.round(V3D.map.getPitch()), V3D.map.getZoom().toFixed(1), v3dOn(), V3D.ready, V3D.failed, V3D.hot, LOWP, SAT_OK, DB.v3d, S.running]"))
    print("\n".join(l for l in logs if "error" in l.lower())[:3000])
    b.close()
