#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build a single-file HAND-DRAWN illustrated travel map (map.html).

No tiles, no Leaflet, no external fonts/JS — everything is inline SVG drawn on a
"Lanna travel journal" cream paper. One little hand-sketched map per day (7 cards);
cross-city / airport days auto-split into a 曼谷 | 清迈 two-frame vignette joined by a
dashed plane arc. Every numbered pin and every stop-list row deep-links to Google Maps
navigation (real coords). Fully offline + China-safe."""
import os, re, json, html, math, datetime, urllib.parse

ROOT = "/home/yuebiao/project/Tailand-travel-plan"

# ---------------- trip data (verbatim, already proof-read) ----------------
trip = {
  "title": "泰国清迈 × 曼谷 · 情侣 7 日",
  "startDate": "2026-07-14",
  "disclaimer": "本页坐标为 AI 依公开资料整理的近似值，仅供手绘示意，点位相对位置经纬度投影、非街道级精确；连线上标注的距离为坐标估算（地面段含道路近似系数、跨城为大圈距离）、时长为按交通方式的参考值，均以实时 Google 导航为准。出行请务必在 Google Maps / 官方渠道核实后再前往。导航按钮一律跳转 Google 地图（泰国首选，高德海外覆盖差）。🚕 Grab 叫车按钮为「尽力唤起」：手机已装 Grab 通常会打开叫车页并预填目的地（视 App 版本也可能只打开 Grab 首页），未安装则回退到 grab.com。",
  "days": [
    {"date": "2026-07-14", "weekday": "周二", "theme": "抵达曼谷 · 朱拉夜市",
     "tips": ["廊曼(DMK)到市区约 26km；A3 巴士便宜、Grab 走高速更快"],
     "slots": [
       {"period": "noon", "name": "抵达 曼谷廊曼机场 DMK", "time": "15:10 落地", "lat": 13.9126, "lng": 100.6068},
       {"period": "noon", "name": "入住 The Quarter Ratchathewi", "time": "16:30", "lat": 13.7538, "lng": 100.5324},
       {"period": "evening", "name": "Banthat Thong 美食街（朱拉隆夜市）", "time": "18:00–18:20", "lat": 13.7365, "lng": 100.5285},
       {"period": "evening", "name": "Banthat Thong 街头晚餐", "time": "18:20–21:00", "lat": 13.7363, "lng": 100.5282},
       {"period": "evening", "name": "Jimjoom99 陶锅火锅（99฿/锅·米其林必比登）", "time": "18:20–20:00", "lat": 13.7368, "lng": 100.5278},
       {"period": "evening", "name": "Pungdet 炭烤吐司（22种馅·有空调）", "time": "18:20–20:00", "lat": 13.7363, "lng": 100.5282},
       {"period": "evening", "name": "Jodd Fairs（Ratchada）备选夜市", "time": "18:00–21:00", "lat": 13.7660, "lng": 100.5720},
     ]},
    {"date": "2026-07-15", "weekday": "周三", "theme": "曼谷半日 → 傍晚飞清迈",
     "tips": ["12:00 前退房、可寄存行李；下午留足时间去廊曼赶 19:30 航班", "Siam 商圈、Pratunam、机场三地，拖行李务必轻装"],
     "slots": [
       {"period": "morning", "name": "The Quarter Ratchathewi（早餐/退房）", "time": "08:00–09:00", "lat": 13.7538, "lng": 100.5324},
       {"period": "morning", "name": "曼谷 Siam 暹罗商圈", "time": "09:15–09:25", "lat": 13.7460, "lng": 100.5340},
       {"period": "morning", "name": "Siam 逛街 + 咖啡", "time": "09:30–12:00", "lat": 13.7465, "lng": 100.5335},
       {"period": "noon", "name": "午餐（Siam 区商场内 food court）", "time": "12:00–13:00", "lat": 13.7455, "lng": 100.5345},
       {"period": "noon", "name": "返回 The Quarter Ratchathewi 取行李", "time": "13:00–13:15", "lat": 13.7538, "lng": 100.5324},
       {"period": "afternoon", "name": "Pratunam 商圈（机动缓冲/扫货/按摩）", "time": "13:15–17:00", "lat": 13.7510, "lng": 100.5400},
       {"period": "afternoon", "name": "曼谷廊曼机场 DMK", "time": "17:00 到机场", "lat": 13.9126, "lng": 100.6068},
       {"period": "evening", "name": "清迈机场 CNX（SL520 抵达）", "time": "20:45", "lat": 18.7680, "lng": 98.9626},
       {"period": "evening", "name": "入住 Travelodge Nimman（清迈）", "time": "21:00", "lat": 18.7985, "lng": 98.9668},
       {"period": "night", "name": "凤飞飞猪脚饭 Khao Kha Moo Chang Phueak（备选宵夜）", "time": "21:30–22:30", "lat": 18.7950, "lng": 98.9850}
     ]},
    {"date": "2026-07-16", "weekday": "周四", "theme": "自然大满贯：粘粘瀑布 · 丛林飞跃 · 便便造纸园",
     "tips": ["城北 Mae Rim 一日，务必包车(约 1,500–3,000฿/天)：瀑布→造纸园→蓬扬全在北线顺路，瀑布 Grab 常拒载返程", "早出发(约 07:30)避午后雷阵雨、穿防滑鞋爬瀑布；蓬扬有体重限制(连衣物鞋约 ≤95–100kg)，建议订 11:00 或 13:00 场(含泰式午餐)", "今晚不做马杀鸡——已挪到 7/17 晚(见 7/17)"],
     "slots": [
       {"period": "morning", "name": "Travelodge Nimman（早餐/出发）", "time": "07:30–07:50", "lat": 18.7985, "lng": 98.9668},
       {"period": "morning", "name": "Bua Tong 粘粘瀑布", "time": "07:50–09:00", "lat": 19.0475, "lng": 99.0286},
       {"period": "morning", "name": "攀爬粘粘瀑布", "time": "09:00–10:45", "lat": 19.0470, "lng": 99.0280},
       {"period": "noon", "name": "POOPOOPAPER Park 大象粪造纸园", "time": "10:45–11:25", "lat": 18.9208, "lng": 98.8875},
       {"period": "noon", "name": "POOPOOPAPER 造纸体验", "time": "11:25–12:30", "lat": 18.9205, "lng": 98.8870},
       {"period": "noon", "name": "无骑乘大象营 / 道德大象营（备选）", "time": "10:45–12:30", "lat": 18.9200, "lng": 98.8800},
       {"period": "afternoon", "name": "蓬扬 Pongyang Jungle Coaster", "time": "12:30–12:55", "lat": 18.916638, "lng": 98.821402},
       {"period": "afternoon", "name": "⭐ 蓬扬丛林飞跃 + 自控丛林过山车", "time": "13:00–15:30", "lat": 18.9163, "lng": 98.8210},
       {"period": "afternoon", "name": "返回 Travelodge Nimman", "time": "15:30–16:20", "lat": 18.7985, "lng": 98.9668},
       {"period": "evening", "name": "宁曼休整 + 晚餐 / 夜市小吃", "time": "16:20 起", "lat": 18.7990, "lng": 98.9670}
     ]},
    {"date": "2026-07-17", "weekday": "周五", "theme": "奶奶厨房 · 宁曼购物 · 古城打铁片 · 马杀鸡",
     "tips": ["先去城西南奶奶厨房 Krua Ya 早午餐(9:00–15:30，早去，下午 3 点半收)，再回宁曼逛街", "午后打车去古城做打铁片；Lanna Artisans 17:00 关门宜早到", "今晚做马杀鸡：Oasis 双人套需预约，市区免费接送"],
     "slots": [
       {"period": "morning", "name": "素贴山双龙寺 Doi Suthep（可选半日）", "time": "06:00–12:00", "lat": 18.8047, "lng": 98.9216},
       {"period": "morning", "name": "⭐ 奶奶厨房 Krua Ya 早午餐", "time": "09:30–11:00", "lat": 18.7625, "lng": 98.9420},
       {"period": "morning", "name": "回宁曼路", "time": "11:00–11:30", "lat": 18.7985, "lng": 98.9668},
       {"period": "morning", "name": "宁曼路购物：One Nimman / Maya / Think Park", "time": "11:30–14:30", "lat": 18.8006, "lng": 98.9673},
       {"period": "afternoon", "name": "宁曼 → 古城南门（Wualai·银庙一带）", "time": "14:30–15:00", "lat": 18.7790, "lng": 98.9836},
       {"period": "afternoon", "name": "打铁片手作 @ Lanna Artisans Art Gallery", "time": "15:00–16:30", "lat": 18.7790, "lng": 98.9836},
       {"period": "afternoon", "name": "银庙 Wat Sri Suphan", "time": "16:30–17:00", "lat": 18.7793, "lng": 98.9838},
       {"period": "evening", "name": "塔佩门 Tha Phae Gate / 古城咖啡", "time": "17:00–18:00", "lat": 18.7877, "lng": 98.9933},
       {"period": "evening", "name": "Ristr8to 尼曼·世界拉花冠军·骷髅杯（备选咖啡）", "time": "17:00–18:00", "lat": 18.7967, "lng": 98.9680},
       {"period": "evening", "name": "Roast8ry Lab 尼曼·冠军新品牌（备选咖啡）", "time": "17:00–18:00", "lat": 18.7985, "lng": 98.9655},
       {"period": "evening", "name": "回宁曼晚餐", "time": "18:00–19:00", "lat": 18.7980, "lng": 98.9660},
       {"period": "evening", "name": "⭐ Oasis Spa Nimman 情侣马杀鸡", "time": "19:00–21:00", "lat": 18.7972, "lng": 98.9662},
       {"period": "evening", "name": "Fah Lanna Spa Romantic 情侣套餐（奢华·备选 SPA）", "time": "19:00–21:00", "lat": 18.7978, "lng": 98.9648},
     ]},
    {"date": "2026-07-18", "weekday": "周六", "theme": "周末市集 · 艺术村 · 周六夜市",
     "tips": ["用满这个唯一的周六：上午 Jing Jai 周末市集（约 14:00 收摊、越早越好）+ 傍晚 Wualai 周六步行街（都仅周末/周六开）", "艺术村 Baan Kang Wat 顺便在村里咖啡馆吃午餐（奶奶厨房已挪到 7/17 早上）"],
     "slots": [
       {"period": "morning", "name": "酒店 → Jing Jai Market（JJ 集市）", "time": "08:00–08:20", "lat": 18.8067, "lng": 98.9762},
       {"period": "morning", "name": "Jing Jai 农夫 + Rustic 手作市集", "time": "08:20–10:30", "lat": 18.8065, "lng": 98.9760},
       {"period": "noon", "name": "JJ → Baan Kang Wat 艺术村", "time": "10:30–10:50", "lat": 18.7758, "lng": 98.9436},
       {"period": "noon", "name": "Baan Kang Wat 艺术村", "time": "10:50–12:15", "lat": 18.7755, "lng": 98.9430},
       {"period": "noon", "name": "Baan Kang Wat 艺术村午餐", "time": "12:15–13:30", "lat": 18.7758, "lng": 98.9436},
       {"period": "noon", "name": "Krua Ya 奶奶厨房（若 7/17 没去·备选午餐）", "time": "12:15–13:30", "lat": 18.7625, "lng": 98.9420},
       {"period": "afternoon", "name": "返回宁曼，酒店午休 / 咖啡", "time": "13:45–15:30", "lat": 18.7985, "lng": 98.9668},
       {"period": "afternoon", "name": "宁曼补咖啡 / 轻按摩 / 收拾行李", "time": "15:30–16:30", "lat": 18.8000, "lng": 98.9670},
       {"period": "evening", "name": "酒店 → Wualai 周六夜市步行街", "time": "17:30–17:50", "lat": 18.7818, "lng": 98.9852},
       {"period": "evening", "name": "Wualai 周六夜市", "time": "18:00–21:00", "lat": 18.7815, "lng": 98.9850},
       {"period": "evening", "name": "夜市 → 酒店", "time": "21:00–21:30", "lat": 18.7985, "lng": 98.9668}
     ]},
    {"date": "2026-07-19", "weekday": "周日", "theme": "飞回曼谷 · ICONSIAM · 昭披耶河夜游船",
     "tips": ["清迈上午约 7:30 离店赶 10:15 航班；曼谷落地素万那普(不是廊曼)", "游船 19:30 从 ICONSIAM 码头发船：先在 ICONSIAM 看 18:30 音乐喷泉再登船；建议提前订顶层/前甲板座", "游船顶掉唐人街正餐；船靠岸后想扫街可 MRT 去吃个宵夜(Yaowarat 开到 00:00+)"],
     "slots": [
       {"period": "morning", "name": "Travelodge Nimman（起床/退房）", "time": "07:00–07:30", "lat": 18.7985, "lng": 98.9668},
       {"period": "morning", "name": "清迈机场 CNX", "time": "07:30–07:50", "lat": 18.7680, "lng": 98.9626},
       {"period": "morning", "name": "清迈机场 CNX 值机安检", "time": "08:15", "lat": 18.7680, "lng": 98.9626},
       {"period": "noon", "name": "VZ2103 CNX → 曼谷素万那普 BKK", "time": "10:15–11:35", "lat": 13.6900, "lng": 100.7501},
       {"period": "afternoon", "name": "BKK 机场 → True Siam Phayathai Hotel", "time": "12:00–13:00", "lat": 13.7565, "lng": 100.5335},
       {"period": "afternoon", "name": "True Siam Phayathai（入住/午餐/休整）", "time": "13:00–14:00", "lat": 13.7565, "lng": 100.5335},
       {"period": "afternoon", "name": "轻松下午：屋顶/河景咖啡", "time": "15:30–17:30", "lat": 13.7300, "lng": 100.5150},
       {"period": "afternoon", "name": "Lumphini 公园散步（备选轻松下午）", "time": "15:30–17:30", "lat": 13.7310, "lng": 100.5415},
       {"period": "evening", "name": "前往 ICONSIAM（河畔商场/游船码头）", "time": "17:30–18:00", "lat": 13.7263, "lng": 100.5100},
       {"period": "evening", "name": "ICONSIAM + 18:30 音乐喷泉", "time": "18:00–19:05", "lat": 13.7263, "lng": 100.5100},
       {"period": "evening", "name": "ICONSIAM 码头 check-in 登船", "time": "19:05–19:25", "lat": 13.7266, "lng": 100.5099},
       {"period": "evening", "name": "⭐ Chao Phraya Princess 夜游船", "time": "19:30–21:30", "lat": 13.7266, "lng": 100.5099},
       {"period": "evening", "name": "唐人街 Yaowarat 宵夜（可选）", "time": "21:45–22:45", "lat": 13.7405, "lng": 100.5090}
     ]},
    {"date": "2026-07-20", "weekday": "周一", "theme": "曼谷早餐 · 回国",
     "tips": ["国际航班 11:05，约 07:00 出发去素万那普(留足早高峰时间)，只够吃个早餐"],
     "slots": [
       {"period": "morning", "name": "True Siam Phayathai Hotel（退房）", "time": "06:15–06:50", "lat": 13.7565, "lng": 100.5335},
       {"period": "morning", "name": "Jok Prince 炭香猪肉粥（早餐）", "time": "06:50–07:15", "lat": 13.7283, "lng": 100.5160},
       {"period": "morning", "name": "K.Panich 芒果糯米饭（周一才开·备选早餐）", "time": "06:50–07:15", "lat": 13.7440, "lng": 100.5060},
       {"period": "morning", "name": "酒店 → 曼谷素万那普 BKK", "time": "07:15", "lat": 13.6900, "lng": 100.7501},
       {"period": "noon", "name": "素万那普 BKK 办理值机 / 退税 / 安检", "time": "08:15", "lat": 13.6900, "lng": 100.7501},
       {"period": "noon", "name": "HU7940 BKK → 海口（回程）", "time": "11:05 起飞", "lat": 13.6900, "lng": 100.7501}
     ]},
  ]
}

# ---------------- geometry helpers ----------------
def esc(s): return html.escape(str(s), quote=True)

def city_of(p): return "cm" if p["lat"] > 16 else "bkk"
CITY_LABEL = {"cm": "清迈 Chiang Mai", "bkk": "曼谷 Bangkok"}

# per-day ink accents (Lanna palette, one per day for variety)
ACCENTS = ["#bd3b73", "#e0a133", "#0f6b53", "#c1522f", "#2f8f6f", "#9a6b14", "#7a5c9e"]

# 每段行程的「时长/方式」（首站为 None；距离由坐标自动算）
LEGS = {
  "2026-07-14": [None, "Grab 40–60min", "Grab 10min", "步行逛吃", "步行", "步行", "Grab 20–30min"],
  "2026-07-15": [None, "BTS 1站", "步行", "步行", "BTS 1站", "步行 14min", "Grab 30–60min", "SL520 航班 1h05", "Grab 15–20min", "Grab 8–10min"],
  "2026-07-16": [None, "包车 1–1.25h", "攀爬", "包车 40min", "造纸体验", "包车 15min", "包车 20–25min", "飞跃", "包车 40–50min", "步行/休息"],
  "2026-07-17": [None, "Grab/包车 30min", "Grab 15–20min", "步行", "Grab 15min", "步行", "步行 2min", "Grab/步行", "Grab/步行", "步行", "步行", "Grab/步行", "步行"],
  "2026-07-18": [None, "Grab 10–15min", "市集", "Grab 15–20min", "逛村", "村内午餐", "Grab 15–20min", "Grab 15–20min", "宁曼", "Grab 15min", "夜市", "Grab 15min"],
  "2026-07-19": [None, "Grab 15–20min", "值机", "VZ2103 航班 1h20", "ARL 28min/Grab", "酒店休整", "二选一", "MRT/Grab", "Grab/BTS 20–30min", "馆内步行", "码头步行", "游船 2h", "MRT/Grab"],
  "2026-07-20": [None, "酒店早餐", "Grab 15min", "Grab/ARL 30–60min", "值机安检", "HU7940 起飞"],
}

def project(points, box):
    """Project lat/lng into an SVG box, preserving relative geography (cos-lat aspect)."""
    if len(points) == 1:
        return [((box[0] + box[2]) / 2, (box[1] + box[3]) / 2)]
    mlat = sum(p["lat"] for p in points) / len(points)
    k = math.cos(math.radians(mlat))
    xs = [p["lng"] * k for p in points]
    ys = [p["lat"] for p in points]
    minx, maxx, miny, maxy = min(xs), max(xs), min(ys), max(ys)
    spanx = (maxx - minx) or 1e-6
    spany = (maxy - miny) or 1e-6
    x0, y0, x1, y1 = box
    pad = 40
    bw, bh = (x1 - x0 - 2 * pad), (y1 - y0 - 2 * pad)
    sc = min(bw / spanx, bh / spany)
    cx, cy = (minx + maxx) / 2, (miny + maxy) / 2
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    return [(mx + (p["lng"] * k - cx) * sc, my - (p["lat"] - cy) * sc) for p in points]

def bloom_duplicates(pos, radius=22):
    """Pre-separate points that project to the exact same pixel so that
    force relaxation does not collapse them against box borders."""
    groups = {}
    for i, p in enumerate(pos):
        key = (round(p[0], 1), round(p[1], 1))
        groups.setdefault(key, []).append(i)
    out = [list(p) for p in pos]
    for key, idxs in groups.items():
        if len(idxs) < 2:
            continue
        cx, cy = key
        n = len(idxs)
        for k, i in enumerate(idxs):
            ang = 2 * math.pi * k / n + ((n % 2) * 0.3)  # slight rotation for variety
            out[i][0] = cx + radius * math.cos(ang)
            out[i][1] = cy + radius * math.sin(ang)
    return out

def relax(pos, box, min_sep=52, iters=120):
    """Push overlapping pins apart, keep inside box."""
    pos = [list(p) for p in pos]
    x0, y0, x1, y1 = box
    for _ in range(iters):
        for i in range(len(pos)):
            for j in range(i + 1, len(pos)):
                dx, dy = pos[j][0] - pos[i][0], pos[j][1] - pos[i][1]
                d = math.hypot(dx, dy)
                if d < 0.5:
                    # deterministic nudge so identical points do not stay stacked
                    ang = math.radians((i * 137.5 + j * 71.3) % 360)
                    dx, dy = math.cos(ang), math.sin(ang)
                    d = 0.5
                if d < min_sep:
                    push = (min_sep - d) / 2
                    ux, uy = dx / d, dy / d
                    pos[i][0] -= ux * push; pos[i][1] -= uy * push
                    pos[j][0] += ux * push; pos[j][1] += uy * push
        for p in pos:
            p[0] = min(max(p[0], x0 + 26), x1 - 26)
            p[1] = min(max(p[1], y0 + 30), y1 - 30)
    return [(round(x, 1), round(y, 1)) for x, y in pos]

def nav(s): return f'https://www.google.com/maps/dir/?api=1&destination={s["lat"]},{s["lng"]}'

def grab(s):
    """Best-effort Grab app deep link with drop-off pre-filled (app URI scheme).
    Not an officially-guaranteed format; page JS falls back to grab.com if the app
    isn't installed. Worst case it just opens Grab, best case pre-fills the drop-off."""
    addr = urllib.parse.quote(s["name"])
    return (f'grab://open?screenType=BOOKING&dropOffLatitude={s["lat"]}'
            f'&dropOffLongitude={s["lng"]}&dropOffAddress={addr}')

def haversine_km(a, b):
    R = 6371.0
    p1, p2 = math.radians(a["lat"]), math.radians(b["lat"])
    dphi = math.radians(b["lat"] - a["lat"])
    dlmb = math.radians(b["lng"] - a["lng"])
    h = math.sin(dphi/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dlmb/2)**2
    return 2 * R * math.asin(math.sqrt(h))

def fmt_km(km):
    if km < 0.95: return f"~{int(round(km*20)*50)}m"
    if km < 20:   return f"~{round(km)}km"
    if km < 100:  return f"~{int(round(km/5)*5)}km"
    return f"~{int(round(km/10)*10)}km"

def leg_dist(a, b):
    km = haversine_km(a, b)
    if city_of(a) == city_of(b): km *= 1.3   # 直线→道路近似系数
    return fmt_km(km)

def text_w(s, size):
    u = 0.0
    for c in s:
        u += 1.75 if ord(c) > 0x2E80 else 0.58
    return u * size

def pin_path(cx, cy, r=14.0):
    return (f"M{cx:.1f} {cy-r:.1f} C {cx-r*1.15:.1f} {cy-r:.1f} {cx-r*1.15:.1f} {cy+r*0.72:.1f} "
            f"{cx:.1f} {cy+r*1.8:.1f} C {cx+r*1.15:.1f} {cy+r*0.72:.1f} {cx+r*1.15:.1f} {cy-r:.1f} "
            f"{cx:.1f} {cy-r:.1f} Z")

# canvas + frame boxes
W, H = 780, 470
ONE = (44, 44, 736, 440)
LEFT = (36, 44, 374, 440)
RIGHT = (406, 44, 744, 440)

# ---------------- decorative doodles ----------------
def doodle(sym, x, y, w, h, color, op=0.5, rot=0):
    t = f' transform="rotate({rot} {x+w/2:.0f} {y+h/2:.0f})"' if rot else ""
    return (f'<use href="#{sym}" x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="{h:.0f}"'
            f' style="color:{color};opacity:{op}"{t}/>')

def decorations(city, box, accent):
    x0, y0, x1, y1 = box
    w = x1 - x0
    ink = "#2a2320"
    d = []
    if city == "cm":
        d.append(doodle("d-mtn", x0 + 10, y0 + 6, min(150, w * 0.42), 76, ink, 0.30))
        d.append(doodle("d-temple", x1 - 66, y1 - 96, 56, 84, accent, 0.32))
        d.append(doodle("d-eleph", x0 + 14, y1 - 74, 82, 60, ink, 0.26))
        d.append(doodle("d-palm", x1 - 118, y0 + 18, 40, 56, "#2f8f6f", 0.30))
    else:
        d.append(doodle("d-river", x0 + 8, y1 - 52, w - 16, 40, "#2f7fae", 0.38))
        d.append(doodle("d-temple", x1 - 70, y0 + 12, 54, 80, accent, 0.30))
        d.append(doodle("d-sun", x0 + 16, y0 + 12, 44, 44, "#e0a133", 0.45))
        d.append(doodle("d-cloud", x1 - 150, y0 + 8, 78, 46, ink, 0.22))
    return "".join(d)

def city_tag(city, box):
    x0, y0, x1, y1 = box
    return (f'<text x="{x0+16:.0f}" y="{y0+28:.0f}" font-family="Georgia,serif" font-size="15" '
            f'fill="#5c5044" opacity="0.75" letter-spacing="0.04em">{CITY_LABEL[city]}</text>'
            f'<path d="M{x0+16:.0f} {y0+34:.0f} q40 5 96 0" fill="none" stroke="#5c5044" '
            f'stroke-width="1.4" opacity="0.4" filter="url(#rough)"/>')

def frame_border(box):
    x0, y0, x1, y1 = box
    return (f'<rect x="{x0}" y="{y0}" width="{x1-x0}" height="{y1-y0}" rx="18" fill="none" '
            f'stroke="#2a2320" stroke-width="1.5" stroke-dasharray="2 7" opacity="0.22" '
            f'filter="url(#rough)"/>')

def route_seg(a, b, pa, pb, accent):
    x1, y1 = pa; x2, y2 = pb
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy) or 1
    nx, ny = -dy / L, dx / L
    if city_of(a) != city_of(b):   # inter-city flight → dashed plane arc
        off = 60
        cx, cy = mx + nx * off, my + ny * off
        ang = math.degrees(math.atan2(y2 - y1, x2 - x1)) + 90
        return (f'<path d="M{x1:.1f} {y1:.1f} Q{cx:.1f} {cy:.1f} {x2:.1f} {y2:.1f}" fill="none" '
                f'stroke="{accent}" stroke-width="2" stroke-dasharray="7 8" stroke-linecap="round" '
                f'opacity="0.7" filter="url(#rough)"/>'
                + doodle("d-plane", cx - 17, cy - 17, 34, 34, accent, 0.9, rot=ang))
    off = 14
    cx, cy = mx + nx * off, my + ny * off
    return (f'<path d="M{x1:.1f} {y1:.1f} Q{cx:.1f} {cy:.1f} {x2:.1f} {y2:.1f}" fill="none" '
            f'stroke="{accent}" stroke-width="2.6" stroke-dasharray="1 8" stroke-linecap="round" '
            f'opacity="0.85" filter="url(#rough)"/>')

def pin(cx, cy, n, accent, navurl, alt=False):
    p = pin_path(cx, cy)
    if alt:
        return (f'<a href="{navurl}" target="_blank" rel="noopener">'
                f'<ellipse cx="{cx:.1f}" cy="{cy+27:.1f}" rx="7" ry="2.6" fill="#2a2320" opacity="0.10"/>'
                f'<path d="{p}" fill="none" stroke="{accent}" stroke-width="2" stroke-dasharray="4 3" filter="url(#rough)" opacity="0.7"/>'
                f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="8.6" fill="#ffffff" opacity="0.10"/>'
                f'<text x="{cx:.1f}" y="{cy:.1f}" text-anchor="middle" dominant-baseline="central" dy="0.5" '
                f'font-family="Georgia,serif" font-weight="400" font-size="13" fill="{accent}" opacity="0.85">{n}</text>'
                f'</a>')
    return (f'<a href="{navurl}" target="_blank" rel="noopener">'
            f'<ellipse cx="{cx:.1f}" cy="{cy+27:.1f}" rx="7" ry="2.6" fill="#2a2320" opacity="0.16"/>'
            f'<path d="{p}" fill="{accent}" stroke="#2a2320" stroke-width="1.6" filter="url(#rough)"/>'
            f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="8.6" fill="#ffffff" opacity="0.15"/>'
            f'<text x="{cx:.1f}" y="{cy:.1f}" text-anchor="middle" dominant-baseline="central" dy="0.5" '
            f'font-family="Georgia,serif" font-weight="700" font-size="15" fill="#fbf6ec">{n}</text>'
            f'</a>')

def leg_label(a, b, pa, pb, leg_text, accent):
    """一段连线上的「≈距离 · 时长」小标签，贴在曲线外侧。"""
    if not leg_text:
        return ""
    x1, y1 = pa; x2, y2 = pb
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy) or 1
    nx, ny = -dy / L, dx / L
    off = (60 if city_of(a) != city_of(b) else 16) + 14
    cx, cy = mx + nx * off, my + ny * off
    d = leg_dist(a, b)
    short_walk = d.endswith("m") and ("步行" in leg_text or "馆内" in leg_text)
    txt = leg_text if short_walk else f"{d} · {leg_text}"
    w = text_w(txt, 13) + 14
    return (f'<g><rect x="{cx-w/2:.1f}" y="{cy-10:.1f}" width="{w:.1f}" height="20" rx="10" '
            f'fill="#ffffff" stroke="{accent}" stroke-width="1.3" opacity="0.97"/>'
            f'<text x="{cx:.1f}" y="{cy:.1f}" text-anchor="middle" dominant-baseline="central" dy="0.5" '
            f'font-family="sans-serif" font-size="13" fill="#2a2320">{esc(txt)}</text></g>')

# ---------------- per-day map + stop list ----------------
def render_day(day, accent, include_stops=True, compact=False):
    pts = day["slots"]
    # collect all points including alts for layout
    all_pts = []
    for p in pts:
        all_pts.append(p)
        for a in p.get("alts", []):
            all_pts.append(a)

    order = []
    for p in all_pts:
        c = city_of(p)
        if c not in order:
            order.append(c)
    boxes = {order[0]: ONE} if len(order) == 1 else {order[0]: LEFT, order[1]: RIGHT}

    coord = {}
    svg = []
    svg.append(f'<rect x="0" y="0" width="{W}" height="{H}" rx="20" fill="#faf4e6"/>')
    svg.append(f'<rect x="0" y="0" width="{W}" height="{H}" rx="20" fill="url(#page)" opacity="0.55"/>')
    svg.append(f'<rect x="0" y="0" width="{W}" height="{H}" rx="20" filter="url(#grain)" opacity="0.05"/>')

    for c in order:
        box = boxes[c]
        cpts = [p for p in all_pts if city_of(p) == c]
        pos = relax(bloom_duplicates(project(cpts, box), radius=22), box)
        for p, xy in zip(cpts, pos):
            coord[id(p)] = xy
        svg.append(frame_border(box))
        svg.append(decorations(c, box, accent))
        svg.append(city_tag(c, box))

    # routes first (under labels & pins) — only between main slots
    for i in range(len(pts) - 1):
        svg.append(route_seg(pts[i], pts[i + 1], coord[id(pts[i])], coord[id(pts[i + 1])], accent))
    # leg labels (≈距离 · 时长) — above routes, below pins
    legs = LEGS.get(day["date"], [])
    for i in range(len(pts) - 1):
        lt = legs[i + 1] if i + 1 < len(legs) else None
        svg.append(leg_label(pts[i], pts[i + 1], coord[id(pts[i])], coord[id(pts[i + 1])], lt, accent))
    # alt pins first (behind main pins)
    for i, p in enumerate(pts, 1):
        alts = p.get("alts", [])
        for j, a in enumerate(alts):
            x, y = coord[id(a)]
            label = f"{i}{chr(97+j)}"  # 1a, 1b, ...
            svg.append(pin(x, y, label, accent, nav(a), alt=True))
            # dashed line from main to alt
            mx, my = coord[id(p)]
            svg.append(f'<line x1="{mx:.1f}" y1="{my:.1f}" x2="{x:.1f}" y2="{y:.1f}" '
                       f'stroke="{accent}" stroke-width="1.2" stroke-dasharray="3 4" opacity="0.45"/>')
    # main pins on top
    for i, p in enumerate(pts, 1):
        x, y = coord[id(p)]
        svg.append(pin(x, y, i, accent, nav(p)))

    svg_html = (f'<svg class="map" viewBox="0 0 {W} {H}" role="img" '
                f'aria-label="{esc(day["date"])} 手绘地图" xmlns="http://www.w3.org/2000/svg">'
                + "".join(svg) + "</svg>")

    # stops list with collapsible alts
    stops_parts = []
    for i, s in enumerate(pts, 1):
        alts = s.get("alts", [])
        # compact mode: hide time from the stop row because the itinerary table below has full timing
        main_time = esc(s.get("time", ""))
        time_html = f'<i>{main_time}</i>' if main_time and not compact else ""
        alt_html = ""
        if alts:
            alt_items_list = []
            for j, a in enumerate(alts):
                alt_time = esc(a.get("time", ""))
                alt_time_html = f'<i>{alt_time}</i>' if alt_time and not compact else ""
                alt_items_list.append(
                    f'<li class="alt-item"><span class="sn sn-alt">{i}{chr(97+j)}</span>'
                    f'<span class="st"><b>{esc(a["name"])}</b>{alt_time_html}</span>'
                    f'<span class="acts">'
                    f'<a class="btn go" href="{nav(a)}" target="_blank" rel="noopener">🧭</a>'
                    f'<a class="btn grab" href="{grab(a)}" data-fb="https://www.grab.com/th/" target="_blank" rel="noopener">🚕</a>'
                    f'</span></li>')
            alt_html = (f'<details class="alt-group"><summary>🔀 还有 {len(alts)} 个备选</summary>'
                        f'<ol class="alt-list">{"".join(alt_items_list)}</ol></details>')
        stops_parts.append(
            f'<li><span class="sn">{i}</span>'
            f'<span class="st"><b>{esc(s["name"])}</b>{time_html}</span>'
            f'<span class="acts">'
            f'<a class="btn go" href="{nav(s)}" target="_blank" rel="noopener">🧭 导航</a>'
            f'<a class="btn grab" href="{grab(s)}" data-fb="https://www.grab.com/th/" target="_blank" rel="noopener">🚕 Grab</a>'
            f'</span></li>'
            + alt_html)
    stops = "".join(stops_parts)

    tips = "".join(f"<li>{esc(t)}</li>" for t in day.get("tips", []))
    tips_html = f'<ul class="tips">{tips}</ul>' if tips else ""
    stops_html = f'<ol class="stops">{stops}</ol>' if include_stops else ""
    n = int(day["date"][8:10])
    return (f'<section class="daycard" id="d{n}" style="--accent:{accent}">'
            f'<div class="dh"><span class="dd">{esc(day["date"][5:])} <em>{esc(day["weekday"])}</em></span>'
            f'<span class="dt">{esc(day["theme"])}</span></div>'
            f'{tips_html}{svg_html}'
            f'{stops_html}</section>')

# ---------------- shared SVG defs (filters + doodle symbols) ----------------
DEFS = """<svg class="defs" width="0" height="0" aria-hidden="true" xmlns="http://www.w3.org/2000/svg"><defs>
<filter id="rough"><feTurbulence type="turbulence" baseFrequency="0.018" numOctaves="2" seed="7" result="n"/>
<feDisplacementMap in="SourceGraphic" in2="n" scale="2.2" xChannelSelector="R" yChannelSelector="G"/></filter>
<filter id="grain"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" stitchTiles="stitch"/><feColorMatrix type="saturate" values="0"/></filter>
<radialGradient id="page" cx="50%" cy="18%" r="90%"><stop offset="0%" stop-color="#fbf6ea"/><stop offset="100%" stop-color="#f0e6cf"/></radialGradient>
<symbol id="d-mtn" viewBox="0 0 150 80"><path d="M2 76 L40 22 L60 48 L86 16 L148 76" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linejoin="round" stroke-linecap="round"/><path d="M80 24 l7 11 l-14 0 z" fill="currentColor"/><path d="M18 60 q10 -8 20 0" fill="none" stroke="currentColor" stroke-width="1.6"/></symbol>
<symbol id="d-temple" viewBox="0 0 60 90"><path d="M30 4 L34 18 L26 18 Z" fill="currentColor"/><path d="M30 16 L42 40 L18 40 Z" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linejoin="round"/><path d="M30 32 L48 66 L12 66 Z" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linejoin="round"/><path d="M14 66 L46 66 L50 86 L10 86 Z" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linejoin="round"/></symbol>
<symbol id="d-eleph" viewBox="0 0 120 90"><path d="M24 74 Q16 40 46 34 Q82 26 96 46 Q108 44 108 56 Q108 63 99 62 L99 76 L88 76 L88 63 Q70 68 52 63 L52 76 L41 76 L41 60 Q28 56 28 74 Z" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linejoin="round"/><path d="M46 60 Q40 76 47 84" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"/><circle cx="60" cy="46" r="2.4" fill="currentColor"/></symbol>
<symbol id="d-palm" viewBox="0 0 80 100"><path d="M40 96 Q43 62 40 46" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round"/><path d="M40 46 Q20 36 8 42 M40 46 Q24 26 18 14 M40 46 Q58 34 72 40 M40 46 Q56 26 66 14 M40 46 Q40 30 40 18" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/></symbol>
<symbol id="d-sun" viewBox="0 0 60 60"><circle cx="30" cy="30" r="11" fill="none" stroke="currentColor" stroke-width="2.4"/><path d="M30 5 V13 M30 47 V55 M5 30 H13 M47 30 H55 M12 12 L18 18 M42 42 L48 48 M48 12 L42 18 M18 42 L12 48" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/></symbol>
<symbol id="d-cloud" viewBox="0 0 100 60"><path d="M24 48 Q6 48 9 32 Q12 19 26 24 Q30 8 48 13 Q62 6 68 23 Q88 21 85 40 Q84 48 72 48 Z" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linejoin="round"/></symbol>
<symbol id="d-river" viewBox="0 0 160 40"><path d="M0 12 Q20 4 40 12 T80 12 T120 12 T160 12" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/><path d="M0 26 Q20 18 40 26 T80 26 T120 26 T160 26" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/></symbol>
<symbol id="d-plane" viewBox="0 0 100 100"><path d="M50 8 L58 44 L90 62 L58 55 L56 82 L66 92 L50 87 L34 92 L44 82 L42 55 L10 62 L42 44 Z" fill="currentColor"/></symbol>
</defs></svg>"""

# ---------------- CSS (plain string; journal aesthetic) ----------------
CSS = """
:root{--paper:#f4ecda;--ink:#2a2320;--ink2:#5c5044;--jade:#0f6b53;--jade-d:#0a4f3d;--terra:#c1522f;--gold:#e0a133;--card:#faf4e6;--line:rgba(42,35,32,.14);--shadow:0 1px 2px rgba(42,35,32,.06),0 14px 34px -16px rgba(42,35,32,.28);--serif:"Songti SC","Noto Serif SC",STSong,serif;--sans:"PingFang SC","Hiragino Sans GB","Microsoft YaHei","Noto Sans SC",system-ui,sans-serif;--lat:"Georgia",serif}
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);font-family:var(--sans);line-height:1.7;
 background-image:radial-gradient(60vw 60vw at 88% -8%,rgba(224,161,51,.18),transparent 60%),radial-gradient(55vw 55vw at -12% 4%,rgba(15,107,83,.15),transparent 60%);background-attachment:fixed}
.wrap{max-width:860px;margin:0 auto;padding:0 clamp(12px,4vw,28px) 60px}
header.top{text-align:center;padding:min(9vw,54px) 0 14px}
.kick{font-family:var(--lat);letter-spacing:.32em;text-transform:uppercase;font-size:11px;color:var(--terra)}
h1{font-family:var(--serif);font-weight:600;font-size:clamp(28px,7vw,48px);margin:10px 0 6px;letter-spacing:.02em;
 background:linear-gradient(160deg,var(--jade-d),var(--jade) 55%,var(--terra));-webkit-background-clip:text;background-clip:text;color:transparent}
.dates{font-family:var(--lat);letter-spacing:.18em;color:var(--ink2);font-size:15px}
.intro{color:var(--ink2);font-size:13.5px;margin:12px auto 0;max-width:640px}
.intro b{color:var(--jade-d)}
/* day quick-nav */
.daynav{display:flex;flex-wrap:wrap;gap:7px;justify-content:center;margin:20px 0 6px}
.daynav a{font-family:var(--lat);font-size:12.5px;text-decoration:none;color:var(--ink2);background:var(--card);
 border:1px solid var(--line);border-radius:999px;padding:5px 11px;box-shadow:var(--shadow)}
.daynav a b{color:var(--ink);font-family:var(--serif)}
/* day card */
.daycard{margin:20px 0;background:var(--card);border:1px solid var(--line);border-radius:18px;padding:15px clamp(12px,3vw,20px) 17px;box-shadow:var(--shadow);scroll-margin-top:16px;position:relative}
.daycard::before{content:"";position:absolute;left:0;top:20px;bottom:20px;width:5px;border-radius:0 5px 5px 0;background:var(--accent);opacity:.9}
.dh{display:flex;align-items:baseline;gap:12px;flex-wrap:wrap;border-bottom:2px solid var(--ink);padding-bottom:9px;margin-bottom:8px}
.dd{font-family:var(--serif);font-weight:600;font-size:20px}.dd em{font-style:normal;color:var(--jade-d);font-size:15px;margin-left:2px}
.dt{color:var(--terra);font-size:14.5px;font-family:var(--serif)}
.tips{margin:6px 0 10px;padding-left:18px;color:var(--ink2);font-size:13px}
.tips li{margin:3px 0}
svg.map{display:block;width:100%;height:auto;border-radius:16px;filter:drop-shadow(0 8px 22px rgba(42,35,32,.14))}
svg.map a{cursor:pointer}
svg.map a:hover path[stroke]{stroke-width:2}
/* stop list */
.stops{list-style:none;margin:13px 0 0;padding:0;display:grid;gap:7px}
.stops li{display:grid;grid-template-columns:auto 1fr;column-gap:10px;row-gap:6px;align-items:center;color:var(--ink);
 background:rgba(255,255,255,.5);border:1px solid var(--line);border-radius:12px;padding:9px 12px}
.sn{grid-column:1;grid-row:1;width:25px;height:25px;border-radius:50%;background:var(--accent);color:#fbf6ec;
 display:grid;place-items:center;font-family:var(--lat);font-weight:700;font-size:13.5px;box-shadow:0 2px 5px rgba(42,35,32,.25)}
.st{grid-column:2;grid-row:1;min-width:0;display:flex;flex-direction:column}
.st b{font-family:var(--serif);font-weight:600;font-size:14px;line-height:1.34}
.st i{font-style:normal;color:var(--ink2);font-size:11.5px;font-family:var(--lat)}
.acts{grid-column:1/-1;grid-row:2;display:flex;flex-wrap:wrap;gap:6px;justify-content:flex-end}
.btn{font-size:12px;text-decoration:none;white-space:nowrap;padding:5px 11px;border-radius:999px;transition:transform .12s}
.btn:active{transform:scale(.94)}
.go{color:#fff;background:linear-gradient(150deg,var(--jade),var(--jade-d));box-shadow:0 2px 6px rgba(10,79,61,.28)}
.grab{color:#fff;background:#00b14f;font-weight:600;box-shadow:0 2px 6px rgba(0,177,79,.32)}
@media(min-width:560px){.stops li{grid-template-columns:auto 1fr auto}.acts{grid-column:3;grid-row:1;flex-wrap:nowrap}}
/* alt groups */
.alt-group{margin:4px 0 4px 35px;border:1px dashed var(--line);border-radius:10px;padding:0;overflow:hidden}
.alt-group summary{font-size:12px;color:var(--ink2);cursor:pointer;padding:6px 10px;user-select:none}
.alt-group summary:hover{color:var(--accent);background:rgba(0,0,0,.02)}
.alt-list{list-style:none;margin:0;padding:0 8px 8px;display:grid;gap:5px}
.alt-item{background:rgba(255,255,255,.4);border:1px dashed var(--line);border-radius:10px;padding:7px 10px}
.sn-alt{width:22px;height:22px;font-size:11.5px;background:transparent;color:var(--accent);border:2px dashed var(--accent);box-shadow:none}
/* legend / disclaimer / footer */
.legend{display:flex;flex-wrap:wrap;gap:12px 18px;justify-content:center;margin:14px 0 0;font-size:12.5px;color:var(--ink2)}
.legend span{display:inline-flex;align-items:center;gap:6px}
.legend .k{width:22px;height:0;border-top:2.6px dotted var(--jade);display:inline-block}
.legend .kf{width:22px;height:0;border-top:2.6px dashed var(--terra);display:inline-block}
.legend .kp{font-size:14px}
.disclaimer{margin:22px 0 0;font-size:12px;color:var(--ink2);background:rgba(193,82,47,.06);border:1px dashed var(--terra);border-radius:12px;padding:12px 15px;line-height:1.65}
footer{text-align:center;color:var(--ink2);font-size:12.5px;padding:28px 10px 6px;border-top:1px solid var(--line);margin-top:26px}
footer a{color:var(--jade-d)}
.booking{margin:20px 0 4px;background:linear-gradient(160deg,rgba(224,161,51,.12),rgba(15,107,83,.07));border:1px solid var(--line);border-left:5px solid var(--gold);border-radius:16px;padding:15px 18px;box-shadow:var(--shadow)}
.booking h3{margin:0 0 3px;font-family:var(--serif);font-size:18px}
.booking .bk-sub{color:var(--ink2);font-size:12.5px;margin:0 0 10px}
.booking ol{list-style:none;margin:0;padding:0;display:grid;gap:8px}
.booking li{display:flex;flex-wrap:wrap;align-items:baseline;gap:5px 8px;padding:9px 11px;background:rgba(255,255,255,.55);border:1px solid var(--line);border-radius:12px}
.booking li b{font-family:var(--serif);font-size:14px}
.booking .bk-when{font-size:11.5px;color:var(--terra);font-family:var(--lat)}
.booking .bk-links{display:flex;flex-wrap:wrap;gap:6px;margin-top:3px;flex:1 1 100%}
.booking .bk-links a{font-size:12px;text-decoration:none;color:#fff;background:linear-gradient(150deg,var(--jade),var(--jade-d));padding:4px 10px;border-radius:999px}
.booking .bk-warn{flex:1 1 100%;font-size:11.5px;color:var(--ink2)}
@media(min-width:760px){.daycard{padding:18px 22px 20px}}
"""

# ---------------- assemble ----------------
def build():
    cards = "".join(render_day(d, ACCENTS[i % len(ACCENTS)]) for i, d in enumerate(trip["days"]))
    daynav = "".join(
        f'<a href="#d{int(d["date"][8:10])}"><b>{d["date"][5:]}</b> {d["weekday"][1:]}</a>'
        for d in trip["days"])
    booking = (
      '<section class="booking">'
      '<h3>🎟️ 出发前必订清单</h3>'
      '<p class="bk-sub">这几样先订好：价格更好、不怕满场（链接为官方/主流平台，实时价格与档期以页面为准）</p>'
      '<ol>'
      '<li><b>① 蓬扬 Pongyang 丛林飞跃</b> <span class="bk-when">7/16 · 建议 13:00 场</span>'
      '<span class="bk-links"><a href="https://www.klook.com/en-US/activity/88017-1-day-join-pongyang-jungle-coaster-zipline-chiang-mai/" target="_blank" rel="noopener">Klook</a>'
      '<a href="https://www.kkday.com/en-us/product/21263" target="_blank" rel="noopener">KKday</a></span>'
      '<span class="bk-warn">⚠️ 体重连衣物鞋 ≤ ~95–100kg、穿运动鞋不能拖鞋</span></li>'
      '<li><b>② 情侣马杀鸡</b> <span class="bk-when">7/17 晚</span>'
      '<span class="bk-links"><a href="https://www.gowabi.com/en/provider/oasis-spa-at-nimman-chiang-mai" target="_blank" rel="noopener">Oasis·GoWabi</a>'
      '<a href="https://fahlanna.com/spa-nimman/" target="_blank" rel="noopener">Fah Lanna 官网</a></span>'
      '<span class="bk-warn">⚠️ 务必预约；Fah Lanna 末场 20:00、Oasis 市区免费接送</span></li>'
      '<li><b>③ Chao Phraya Princess 夜游船</b> <span class="bk-when">7/19 · 19:30 ICONSIAM 码头</span>'
      '<span class="bk-links"><a href="https://www.klook.com/en-US/activity/88680-upper-deck-seat-chao-phraya-princess-cruise-bangkok/" target="_blank" rel="noopener">Klook 顶层</a>'
      '<a href="https://www.klook.com/en-US/activity/375-chao-phraya-princess-cruise-bangkok/" target="_blank" rel="noopener">Klook 标准</a>'
      '<a href="https://www.kkday.com/en-us/product/2567-chao-phraya-princess-river-cruise-with-dinner-buffet-thailand" target="_blank" rel="noopener">KKday</a>'
      '<a href="https://chaophrayaprincess.com/reservations.php" target="_blank" rel="noopener">官网</a></span>'
      '<span class="bk-warn">⚠️ 选顶层/前甲板；提前 30 分到 ICONSIAM Pier 2 · SookSiam G 层 Naraya 旁 check-in</span></li>'
      '<li><b>④ TDAC 电子入境卡</b> <span class="bk-when">免费 · 抵达前 72h（最早 7/11）</span>'
      '<span class="bk-links"><a href="https://tdac.immigration.go.th/" target="_blank" rel="noopener">tdac.immigration.go.th</a></span>'
      '<span class="bk-warn">⚠️ 认准 .go.th 免费官网，填完存 QR 截图</span></li>'
      '</ol></section>')
    page = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#0f6b53">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Crect width='100' height='100' rx='22' fill='%230f6b53'/%3E%3Ctext x='50' y='74' font-size='60' text-anchor='middle' fill='%23f7edd7' font-family='Georgia,serif'%3E%E0%B8%97%3C/text%3E%3C/svg%3E">
<title>{esc(trip['title'])} · 手绘地图</title>
<style>{CSS}</style>
</head>
<body>
{DEFS}
<div class="wrap">
  <header class="top">
    <div class="kick">Hand-drawn Route Journal · 手绘路线</div>
    <h1>{esc(trip['title'])}</h1>
    <div class="dates">2026 · 07 · 14 — 07 · 20</div>
    <p class="intro">一天一张手绘小地图，牛皮纸上用墨线把当天的脚印连起来。每一站都能<b>一键跳 Google 地图导航</b>，或 <b>🚕 唤起 Grab 叫车</b>（尽力预填目的地）。跨城/机场那天会拆成「曼谷｜清迈」两格、用虚线飞机弧相连。全部离线绘制，无需联网。</p>
    <div class="legend">
      <span><i class="k"></i> 当天步行/车行路线</span>
      <span><i class="kf"></i> 飞机跨城</span>
      <span><i class="kp">📏</i> 连线上 ≈距离 · 时长（估算）</span>
      <span><i class="kp">🧭</i> 图钉/导航 = Google 地图</span>
      <span><i class="kp">🚕</i> Grab = 叫车（预填目的地）</span>
    </div>
  </header>

  <nav class="daynav">{daynav}</nav>

  {booking}

  {cards}

  <div class="disclaimer">{esc(trip["disclaimer"])}</div>

  <footer>
    🐘 {esc(trip['title'])} · 2026/7/14–7/20 ·
    <a href="./index.html">← 返回完整攻略</a> ·
    <a href="./hotel.html">曼谷酒店实拍 →</a><br>
    手绘 SVG · 无外部依赖 · 坐标近似示意，导航以 Google 地图为准
  </footer>
</div>
<script>
/* Grab 深链：点按先尝试唤起 App，未安装/桌面端则回退 grab.com；不影响离线阅读 */
document.addEventListener('click',function(e){{
  var a=e.target.closest('a.grab');if(!a)return;
  var app=a.getAttribute('href'),fb=a.getAttribute('data-fb');
  if(!app||app.indexOf('grab://')!==0){{return;}}
  e.preventDefault();var t=Date.now();
  setTimeout(function(){{if(!document.hidden&&Date.now()-t<1700){{window.location=fb;}}}},1200);
  window.location=app;
}});
</script>
</body>
</html>"""
    out = os.path.join(ROOT, "map.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(page)
    n_points = sum(len(d["slots"]) for d in trip["days"])
    print(f"wrote {out} — {len(page)} chars, {len(trip['days'])} hand-drawn day maps, {n_points} pins")

def render_day_fragments():
    """Return {day_num: html_fragment} for embedding into index.html.
    The map provides the visual + numbered pins (pins link to Google Maps).
    Detailed timing, transport and action buttons live in the itinerary
    markdown table below, so we drop the stops list entirely."""
    fragments = {}
    for i, d in enumerate(trip["days"]):
        accent = ACCENTS[i % len(ACCENTS)]
        n = int(d["date"][8:10])
        fragments[n] = render_day(d, accent, include_stops=False)
    return fragments

if __name__ == "__main__":
    build()
