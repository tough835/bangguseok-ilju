import math
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
