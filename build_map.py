#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build a single-file travel-map HTML (map.html) from the finished Thailand plan,
following the travel-plan-viz skill's page-contract. Inlines its map.js/reminders.js
engines (map.js patched to use Google Maps nav links). No external fonts."""
import os, re, json, html, datetime

ROOT = "/home/yuebiao/project/Tailand-travel-plan"
SKILL = "/home/yuebiao/.claude/skills/travel-plan-viz/assets"

# ---------------- trip data (per page-contract) ----------------
trip = {
  "title": "泰国清迈 × 曼谷 · 情侣 7 日",
  "startDate": "2026-07-14",
  "colorScheme": "lanna-jade",
  "preTrip": {
    "weather": {
      "summary": "7 月雨季/绿色季：清迈 31–32℃、曼谷 32–34℃，午后/傍晚多短时强阵雨（约 30–90 分钟），上午多晴。",
      "typhoon": "非雾霾季（雾霾在 2–4 月），7 月空气清新；曼谷暴雨偶有短时内涝，走排水好的主干道。"
    },
    "packing": "一次性雨衣+折叠伞、速干衣、防滑凉鞋/两栖鞋、驱蚊液(含 DEET)、珊瑚友好防晒、万能转换插头(泰国 220V·A/B/C 型，中国插头多可直插)、寺庙用过肩过膝衣物+披肩。",
    "payment": "现金为主(街摊/双条/夜市只收现金)，备足 20/50/100 泰铢小钞；SuperRich 换汇最优、机场最差；ATM 外卡约 220฿/笔一次取足；大商场可刷卡。",
    "apps": ["Grab / Bolt（叫车）", "Google Maps（泰国导航首选）", "TDAC 官网 tdac.immigration.go.th（数字入境卡）"],
    "ticketTip": "中泰互免签证、≤30 天免签；抵达前 72 小时内（最早 7/11）在官方 tdac.immigration.go.th 填 TDAC 并保存 QR 码，认准 .go.th 免费，防收费假站。"
  },
  "flights": {
    "booked": [
      {"label": "7/14 长沙 → 曼谷廊曼(DMK)", "code": "FD481 泰亚航", "time": "12:55–15:10"},
      {"label": "7/15 曼谷廊曼(DMK) → 清迈(CNX)", "code": "SL520 泰狮航", "time": "19:30–20:45"},
      {"label": "7/19 清迈(CNX) → 曼谷素万那普(BKK)", "code": "VZ2103 泰越捷", "time": "10:15–11:35"},
      {"label": "7/20 曼谷素万那普(BKK) → 海口", "code": "HU7940 海航", "time": "11:05–14:40"},
      {"label": "7/20 海口 → 长沙", "code": "HU7517 海航", "time": "16:30–18:35"},
    ],
    "candidates": []
  },
  "hotelAreas": [
    {"area": "曼谷 · Ratchathewi（前段 7/14）", "reason": "近 Pratunam/Siam 与朱拉美食街，Ratchathewi/Phaya Thai 站步行圈",
     "options": [{"tier": "已订", "name": "The Quarter Ratchathewi by UHG", "priceRange": "已预订 · 1 晚", "note": "388 Phetchaburi Rd，高级双人间"}]},
    {"area": "清迈 · 宁曼 Nimman（主场 7/15–7/19）", "reason": "步行逛 One Nimman/Maya、多家美食咖啡，打车古城 15 分钟",
     "options": [{"tier": "已订", "name": "Travelodge Nimman Chiang Mai", "priceRange": "已预订 · 4 晚", "note": "宁曼核心区，高级房"}]},
    {"area": "曼谷 · Phayathai/Ratchathewi（后段 7/19–7/20）", "reason": "步行 4 分钟到帕亚泰(Phaya Thai) ARL 机场快线，7/20 早直达素万那普赶国际航班",
     "options": [
       {"tier": "已订", "name": "True Siam Phayathai Hotel 真暹罗帕亚泰", "priceRange": "已预订 · ¥291 起/晚", "note": "8.8 分，近 Phaya Thai BTS/ARL；站内 hotel.html 有实拍与介绍"},
     ]},
  ],
  "disclaimer": "本页全部信息（天气、航班、酒店、餐厅、景点、门票、价格、营业时间、坐标、评分等）均为 AI 基于公开资料整理的参考建议，可能不准确或已过时，不保证与实时情况一致；坐标为近似值仅供地图示意，请务必在 Google Maps / 官方渠道 / 订票订房 App 核实后再前往。",
  "tips": [
    "叫车优先 Grab（上车前显示固定价），装 Bolt/inDrive 比价；清迈红双条古城内短途约 30–40฿/人，下车付现，别主动问价。",
    "泰国用 Google Maps 导航（本页 marker 一键跳 Google 地图）；高德海外覆盖差，不建议。",
    "传统 khao soi/烤鸡多只做午市、卖完即收，想吃中午前去；凤飞飞猪脚饭、打抛牛肉店是傍晚才开。",
    "雨季把户外(瀑布/寺庙/市集)排上午，午后阵雨转室内(商场/咖啡/按摩)；随身带雨衣。",
    "现金为主，街摊/双条/夜市/寺庙只收现金；PromptPay 短期游客用不了。",
    "寺庙过肩过膝、进殿脱鞋；银庙 Wat Sri Suphan 银殿仅限男性入内。尊重王室是法律红线。",
  ],
  "reminders": [
    {"item": "填写 TDAC 泰国数字入境卡（tdac.immigration.go.th，认准 .go.th）", "leadDays": 3},
    {"item": "购买含医疗+紧急送返的旅行保险（若租摩托确认含两轮条款）", "leadDays": 7},
    {"item": "备泰铢现金 + 确认手机可用 Grab / Google Maps", "leadDays": 2},
  ],
  "days": [
    {"date": "2026-07-14", "weekday": "周二", "theme": "抵达曼谷 · 朱拉夜市",
     "tips": ["廊曼(DMK)到市区约 26km；A3 巴士便宜、Grab 走高速更快"],
     "slots": [
       {"period": "noon", "name": "抵达 曼谷廊曼机场 DMK", "time": "15:10 落地", "lat": 13.9126, "lng": 100.6068,
        "review": "国际航班到达，填好 TDAC、取托运、出关；打车/A3 巴士进城", "transport": {"mode": "Grab/出租(高速)", "fare": "约 350–500฿", "duration": "约 40–60 分钟"}},
       {"period": "noon", "name": "入住 The Quarter Ratchathewi", "time": "16:30", "lat": 13.7538, "lng": 100.5324,
        "review": "放行李、休整；近 Pratunam/Siam", "openingHours": "14:00 后入住"},
       {"period": "evening", "name": "朱拉/Banthat Thong 美食街夜市", "time": "18:30–22:00", "lat": 13.7365, "lng": 100.5285,
        "review": "曼谷年轻人气美食街：泰式炒粉、烤串、Elvis Suki、芒果糯米饭，走走吃吃", "seasonal": "露天，遇雨躲进商场"}
     ],
     "dining": [{"meal": "晚餐", "place": "Banthat Thong 美食街", "hours": "傍晚–深夜",
        "dishes": [{"name": "Elvis Suki 干泰式寿喜", "price": "60฿起/道"}, {"name": "芒果糯米饭", "price": "80–150฿"}]}]},

    {"date": "2026-07-15", "weekday": "周三", "theme": "曼谷半日 → 傍晚飞清迈",
     "tips": ["12:00 前退房、可寄存行李；下午留足时间去廊曼赶 19:30 航班"],
     "slots": [
       {"period": "morning", "name": "曼谷 Siam 暹罗商圈", "time": "10:00–13:00", "lat": 13.7460, "lng": 100.5340,
        "review": "Siam Paragon/CentralWorld 逛街吹空调，或就近一座寺庙；午餐后取行李", "transport": {"mode": "BTS 天铁", "fare": "约 25–40฿", "duration": "10–20 分钟"}},
       {"period": "afternoon", "name": "曼谷廊曼机场 DMK 飞清迈", "time": "17:00 到机场", "lat": 13.9126, "lng": 100.6068,
        "review": "国内航班提前约 2 小时到；SL520 19:30 起飞", "needsBooking": False},
       {"period": "evening", "name": "入住 Travelodge Nimman（清迈）", "time": "21:00", "lat": 18.7985, "lng": 98.9668,
        "review": "20:45 落地清迈，打车约 15 分钟到宁曼；放行李后吃夜宵", "transport": {"mode": "机场出租/Grab", "fare": "约 150–200฿", "duration": "约 15 分钟"}}
     ],
     "dining": [{"meal": "夜宵", "place": "凤飞飞猪脚饭（象门 Chang Phueak）", "hours": "约 17:00–午夜",
        "dishes": [{"name": "五香猪脚饭 khao kha moo", "price": "50–80฿"}]}]},

    {"date": "2026-07-16", "weekday": "周四", "theme": "粘粘瀑布 · 便便造纸园 · 马杀鸡",
     "tips": ["城北一日，建议包车(约 1,500–3,000฿/天)；瀑布 Grab 常拒载返程", "早出发避午后雷阵雨；穿防滑鞋爬瀑布"],
     "slots": [
       {"period": "morning", "name": "Bua Tong 粘粘瀑布", "time": "09:45–12:00", "lat": 19.0475, "lng": 99.0286,
        "review": "石灰岩不打滑、可赤脚往上爬，雨季水量最壮观", "ticketPrice": "免费（入口登记）", "openingHours": "约 08:00–17:00",
        "transport": {"mode": "包车", "fare": "约 60km/1–1.25h", "duration": "往北"}},
       {"period": "noon", "name": "POOPOOPAPER Park 大象粪造纸园", "time": "13:00–14:30", "lat": 18.9208, "lng": 98.8875,
        "review": "Mae Rim，字面就是“大象粑粑”：手工造纸体验、有中英导览，可动手", "ticketPrice": "约 120–150฿/人", "openingHours": "约 09:00–17:00"},
       {"period": "evening", "name": "Oasis Spa Nimman 情侣马杀鸡", "time": "18:00–20:30", "lat": 18.7972, "lng": 98.9662,
        "review": "King & Queen 双人套，市区免费接送；纪念感可选 Fah Lanna Romantic", "ticketPrice": "双人套约 3,045฿ 起", "needsBooking": True, "leadDays": 1}
     ],
     "dining": [
       {"meal": "午餐", "place": "Mae Rim 花园餐厅", "hours": "沿途", "dishes": [{"name": "泰北家常菜", "price": "150–300฿/人"}]},
       {"meal": "晚餐", "place": "Tong Tem Toh（宁曼 Soi 13）", "hours": "08:00–23:00",
        "dishes": [{"name": "北部拼盘 Or-dern Muang", "price": "约 187฿"}, {"name": "炭烤猪颈肉配 jaew", "price": "—"}]}]},

    {"date": "2026-07-17", "weekday": "周五", "theme": "宁曼购物 · 古城打铁片手作",
     "tips": ["上午宁曼，午后打车去古城做打铁片；Lanna Artisans 17:00 关门宜早到"],
     "slots": [
       {"period": "morning", "name": "One Nimman / 宁曼路购物", "time": "10:00–13:00", "lat": 18.8006, "lng": 98.9673,
        "review": "One Nimman 意式拱廊+文创、Maya 商场、Think Park；家门口步行圈", "openingHours": "约 11:00–21:00"},
       {"period": "noon", "name": "打铁片手作 @ Lanna Artisans Art Gallery", "time": "14:15–16:00", "lat": 18.7790, "lng": 98.9836,
        "review": "南门银庙旁、认门口有三角梅那家：小铁锤敲打铁牌做钥匙扣/戒指，独一无二伴手礼", "ticketPrice": "50฿/件（仅现金）", "openingHours": "约 09:00–17:00",
        "transport": {"mode": "Grab 宁曼→古城", "fare": "约 80–120฿", "duration": "约 15 分钟"}},
       {"period": "afternoon", "name": "银庙 Wat Sri Suphan", "time": "16:00–16:40", "lat": 18.7793, "lng": 98.9838,
        "review": "全球唯一纯银装饰佛殿，兰纳银匠工艺", "ticketPrice": "约 50฿", "openingHours": "银殿仅限男性入内"},
       {"period": "evening", "name": "塔佩门 Tha Phae Gate / 古城咖啡", "time": "17:00 起", "lat": 18.7877, "lng": 98.9933,
        "review": "古城地标散步、顺路咖啡馆歇脚，晚餐宁曼或古城"}
     ],
     "dining": [
       {"meal": "早午餐", "place": "宁曼 brunch / 咖啡", "hours": "上午", "dishes": [{"name": "Ristr8to 冠军拉花", "price": "100–150฿"}, {"name": "Joost 山竹果昔", "price": "50฿起"}]},
       {"meal": "晚餐", "place": "Kao Soy Nimman / 古城餐厅", "hours": "晚市", "dishes": [{"name": "khao soi 咖喱面", "price": "90–100฿"}]}]},

    {"date": "2026-07-18", "weekday": "周六", "theme": "周末市集 · 艺术村 · 周六夜市",
     "tips": ["用满这个唯一的周六：上午 Jing Jai 周末市集 + 傍晚 Wualai 周六步行街（都仅周末/周六开）"],
     "slots": [
       {"period": "morning", "name": "Jing Jai 周末市集（JJ Market）", "time": "07:30–11:00", "lat": 18.8067, "lng": 98.9762,
        "review": "仅周末上午：有机农产+手作+咖啡+北部小吃，树荫下很出片", "openingHours": "约 06:30–14:00（仅周六日）"},
       {"period": "noon", "name": "Baan Kang Wat 艺术村（白色集市）", "time": "12:30–15:00", "lat": 18.7758, "lng": 98.9436,
        "review": "手作艺术家社区、文艺小店咖啡；周一休", "openingHours": "约 10:00–18:00（周一休）"},
       {"period": "evening", "name": "Wualai 周六步行街", "time": "17:30–22:00", "lat": 18.7818, "lng": 98.9852,
        "review": "仅周六：银器手工艺 + 北部街头小吃（khao soi、香蕉叶烤蛋），比周日街更本地", "seasonal": "全露天，雨季看天（可转 Kalare 有顶食阁）"}
     ],
     "dining": [
       {"meal": "早餐", "place": "Jing Jai 市集", "hours": "上午", "dishes": [{"name": "sai ua 北部香肠 + 咖啡", "price": "市集价"}]},
       {"meal": "晚餐", "place": "Wualai 周六夜市小吃", "hours": "傍晚", "dishes": [{"name": "香蕉叶烤“野蛋” + 烤串", "price": "夜市价"}]}]},

    {"date": "2026-07-19", "weekday": "周日", "theme": "飞回曼谷 · 唐人街扫街",
     "tips": ["清迈上午约 7:30 离店赶 10:15 航班；曼谷落地素万那普(不是廊曼)", "唐人街周日晚正是巅峰、正好避开周一弱夜"],
     "slots": [
       {"period": "morning", "name": "清迈机场 CNX 飞曼谷", "time": "08:15 到机场 / 10:15 起飞", "lat": 18.7680, "lng": 98.9626,
        "review": "退房→CNX 约 15 分钟；VZ2103 飞素万那普"},
       {"period": "afternoon", "name": "入住 True Siam Phayathai Hotel", "time": "12:30", "lat": 13.7565, "lng": 100.5335,
        "review": "帕亚泰/Ratchathewi，步行 4 分到 ARL 机场快线，放行李后玩曼谷；次日直达素万那普", "openingHours": "近 Phaya Thai BTS/ARL"},
       {"period": "afternoon", "name": "ICONSIAM（昭披耶河畔）", "time": "13:30–17:00", "lat": 13.7263, "lng": 100.5100,
        "review": "11:35 落地素万那普→市区；ICONSIAM 室内 SookSiam 水上市场+河景，雨天友好", "transport": {"mode": "ARL 机场快线→市区", "fare": "约 45฿/人", "duration": "约 30 分钟"}},
       {"period": "evening", "name": "Yaowarat 唐人街扫街", "time": "18:00–22:00", "lat": 13.7405, "lng": 100.5090,
        "review": "泰国最强街头美食带：烤海鲜、燕窝糖水、卷粉汤，19 点后最旺；MRT Wat Mangkon 1 号口直达"}
     ],
     "dining": [{"meal": "晚餐", "place": "唐人街 Yaowarat", "hours": "傍晚–02:00",
        "dishes": [{"name": "T&K/Lek&Rut 烤大虾·蟹", "price": "50–200฿/道"}, {"name": "Guay Jub 胡椒卷粉汤", "price": "50–100฿"}]}]},

    {"date": "2026-07-20", "weekday": "周一", "theme": "曼谷早餐 · 回国",
     "tips": ["国际航班 11:05，约 07:00 出发去素万那普(留足早高峰时间)，只够吃个早餐"],
     "slots": [
       {"period": "morning", "name": "Jok Prince 炭香猪肉粥（早餐）", "time": "06:30", "lat": 13.7283, "lng": 100.5160,
        "review": "必比登，周一也开、6 点开门；或 K.Panich 芒果糯米饭打包", "ticketPrice": "40–60฿", "openingHours": "06:00 起"},
       {"period": "noon", "name": "曼谷素万那普机场 BKK 回国", "time": "08:15 到机场 / 11:05 起飞", "lat": 13.6900, "lng": 100.7501,
        "review": "HU7940 经海口转 HU7517 回长沙", "transport": {"mode": "ARL/Grab", "fare": "约 45–650฿", "duration": "早高峰留足时间"}}
     ],
     "dining": [{"meal": "早餐", "place": "Jok Prince / K.Panich", "hours": "上午",
        "dishes": [{"name": "炭香猪肉粥", "price": "40–60฿"}, {"name": "K.Panich 芒果糯米饭(打包)", "price": "100–150฿"}]}]},
  ]
}

# ---------------- engines (inline; patch map.js nav → Google Maps) ----------------
reminders_js = open(os.path.join(SKILL, "reminders.js"), encoding="utf-8").read()
map_js = open(os.path.join(SKILL, "map.js"), encoding="utf-8").read()
map_js = re.sub(
    r"// 生成跳转手机地图导航的链接。.*?function buildNavLink\(lat, lng, label, ua\) \{.*?\n\}",
    "// 生成导航链接（泰国用 Google Maps，跨平台唤起 Google 地图）\n"
    "function buildNavLink(lat, lng, label, ua) {\n"
    "  return 'https://www.google.com/maps/dir/?api=1&destination=' + lat + ',' + lng;\n"
    "}",
    map_js, flags=re.S)

# ---------------- helpers ----------------
def esc(s): return html.escape(str(s), quote=True)

def deadline(start, lead):
    d = datetime.date.fromisoformat(start) - datetime.timedelta(days=lead)
    return d.isoformat()

PERIOD = {"morning": "上午", "noon": "午间", "afternoon": "午后", "evening": "傍晚/晚"}

def render_checklist():
    items = sorted(trip["reminders"], key=lambda r: deadline(trip["startDate"], r["leadDays"]))
    lis = "".join(
        f'<li><input type="checkbox"><span class="dl">{deadline(trip["startDate"], r["leadDays"])} 前</span>'
        f'<span>{esc(r["item"])}（提前 {r["leadDays"]} 天）</span></li>' for r in items)
    return f'<ul class="checklist" id="checklist">{lis}</ul>'

def render_pretrip():
    p = trip["preTrip"]
    apps = " · ".join(esc(a) for a in p["apps"])
    return f"""<div class="grid2">
      <div class="info-card"><h4>☔ 天气</h4><p>{esc(p['weather']['summary'])}</p><p class="sub">{esc(p['weather']['typhoon'])}</p></div>
      <div class="info-card"><h4>🎒 打包</h4><p>{esc(p['packing'])}</p></div>
      <div class="info-card"><h4>💳 支付</h4><p>{esc(p['payment'])}</p></div>
      <div class="info-card"><h4>📱 必备 App</h4><p>{apps}</p></div>
      <div class="info-card wide"><h4>🛂 签证 / TDAC</h4><p>{esc(p['ticketTip'])}</p></div>
    </div>"""

def render_flights():
    rows = "".join(
        f'<div class="fl"><span class="fl-badge">已订</span><div class="fl-main">{esc(f["label"])}<span class="fl-code">{esc(f["code"])}</span></div><div class="fl-time">{esc(f["time"])}</div></div>'
        for f in trip["flights"]["booked"])
    return f'<div class="flights">{rows}</div>'

def render_hotels():
    blocks = []
    for a in trip["hotelAreas"]:
        opts = "".join(
            f'<div class="ho-opt"><span class="ho-tier">{esc(o["tier"])}</span><b>{esc(o["name"])}</b>'
            f'<span class="ho-price">{esc(o["priceRange"])}</span><span class="ho-note">{esc(o["note"])}</span></div>'
            for o in a["options"])
        blocks.append(f'<div class="ho-area"><h4>{esc(a["area"])}</h4><p class="sub">{esc(a["reason"])}</p>{opts}</div>')
    return f'<div class="grid2">{"".join(blocks)}</div>'

def render_timeline():
    out = []
    for d in trip["days"]:
        slots = ""
        for s in d["slots"]:
            bits = []
            if s.get("openingHours"): bits.append(f'🕒 {esc(s["openingHours"])}')
            if s.get("closedDays"): bits.append(f'🚫 {esc(s["closedDays"])}')
            if s.get("ticketPrice"): bits.append(f'🎫 {esc(s["ticketPrice"])}')
            if s.get("seasonal"): bits.append(f'✨ {esc(s["seasonal"])}')
            if s.get("transport"):
                t = s["transport"]; bits.append("🚕 " + esc(" · ".join(x for x in [t.get("mode"), t.get("fare"), t.get("duration")] if x)))
            meta = "".join(f'<span class="chip">{b}</span>' for b in bits)
            badge = f'<span class="rbadge">⚠️ 提前 {s.get("leadDays",0)} 天订</span>' if s.get("needsBooking") else ""
            nav = f'https://www.google.com/maps/dir/?api=1&destination={s["lat"]},{s["lng"]}'
            slots += f"""<div class="slot">
              <div class="slot-h"><span class="slot-p">{PERIOD.get(s['period'],'')}</span><span class="slot-t">{esc(s.get('time',''))}</span></div>
              <div class="slot-name">{esc(s['name'])}{badge}</div>
              <p class="slot-r">{esc(s.get('review',''))}</p>
              <div class="chips">{meta}</div>
              <a class="navlink" href="{nav}" target="_blank" rel="noopener">🧭 Google 地图导航</a>
            </div>"""
        dining = ""
        for m in d.get("dining", []):
            dishes = "、".join(f'{esc(x["name"])} <i>{esc(x["price"])}</i>' for x in m.get("dishes", []))
            dining += f'<div class="dine"><span class="dine-meal">{esc(m["meal"])}</span><b>{esc(m["place"])}</b><span class="sub">{esc(m.get("hours",""))}</span><div class="dishes">{dishes}</div></div>'
        tips = "".join(f'<li>{esc(t)}</li>' for t in d.get("tips", []))
        tips_html = f'<ul class="daytips">{tips}</ul>' if tips else ""
        out.append(f"""<section class="day">
          <div class="day-head"><span class="day-date">{esc(d['date'][5:])} <em>{esc(d['weekday'])}</em></span><span class="day-theme">{esc(d.get('theme',''))}</span></div>
          {tips_html}
          <div class="slots">{slots}</div>
          <div class="dining"><h5>🍜 当日餐饮</h5>{dining}</div>
        </section>""")
    return "".join(out)

def render_tips():
    return '<ul class="tips">' + "".join(f'<li>{esc(t)}</li>' for t in trip["tips"]) + '</ul>'

trip_json = json.dumps(trip, ensure_ascii=False)

# ---------------- assemble ----------------
HTML = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#0f6b53">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Crect width='100' height='100' rx='22' fill='%230f6b53'/%3E%3Ctext x='50' y='74' font-size='60' text-anchor='middle' fill='%23f7edd7' font-family='Georgia,serif'%3E%E0%B8%97%3C/text%3E%3C/svg%3E">
<title>{esc(trip['title'])} · 交互地图</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<style>
:root{{--paper:#f6efe1;--ink:#2a2320;--ink2:#5c5044;--jade:#0f6b53;--jade-d:#0a4f3d;--jade-l:#3f9b7f;--gold:#e0a133;--terra:#c1522f;--magenta:#bd3b73;--card:#fbf6ec;--line:rgba(42,35,32,.13);--shadow:0 1px 2px rgba(42,35,32,.06),0 10px 30px -12px rgba(42,35,32,.22);--serif:"Songti SC","Noto Serif SC",STSong,serif;--sans:"PingFang SC","Hiragino Sans GB","Microsoft YaHei","Noto Sans SC",system-ui,sans-serif;--lat:"Georgia",serif}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--paper);color:var(--ink);font-family:var(--sans);line-height:1.7;
 background-image:radial-gradient(60vw 60vw at 88% -8%,rgba(224,161,51,.18),transparent 60%),radial-gradient(55vw 55vw at -12% 6%,rgba(15,107,83,.15),transparent 60%);background-attachment:fixed}}
.wrap{{max-width:940px;margin:0 auto;padding:0 clamp(14px,4vw,32px) 60px}}
header.top{{text-align:center;padding:min(10vw,60px) 0 22px}}
.kick{{font-family:var(--lat);letter-spacing:.3em;text-transform:uppercase;font-size:11px;color:var(--terra)}}
h1{{font-family:var(--serif);font-weight:600;font-size:clamp(30px,7vw,52px);margin:10px 0 6px;letter-spacing:.02em;
 background:linear-gradient(160deg,var(--jade-d),var(--jade) 55%,var(--terra));-webkit-background-clip:text;background-clip:text;color:transparent}}
.dates{{font-family:var(--lat);letter-spacing:.18em;color:var(--ink2);font-size:15px}}
h2{{font-family:var(--serif);font-weight:600;font-size:21px;margin:38px 0 14px;padding-left:13px;border-left:5px solid var(--jade);letter-spacing:.02em}}
.sub{{color:var(--ink2);font-size:13px}}
.card{{background:var(--card);border:1px solid var(--line);border-radius:14px;box-shadow:var(--shadow)}}
.grid2{{display:grid;grid-template-columns:1fr;gap:12px}}
.info-card{{background:var(--card);border:1px solid var(--line);border-left:4px solid var(--jade-l);border-radius:12px;padding:13px 15px;box-shadow:var(--shadow)}}
.info-card h4{{margin:0 0 5px;font-family:var(--serif);font-size:15px}}
.info-card p{{margin:3px 0;font-size:13.5px}}.info-card .sub{{font-size:12.5px}}
/* checklist */
.checklist{{list-style:none;margin:0;padding:0;display:grid;gap:8px}}
.checklist li{{display:flex;align-items:flex-start;gap:9px;background:var(--card);border:1px solid var(--line);border-radius:11px;padding:11px 13px;box-shadow:var(--shadow);font-size:14px}}
.checklist .dl{{color:var(--terra);font-weight:700;font-family:var(--lat);white-space:nowrap}}
.checklist input{{margin-top:4px;accent-color:var(--jade);width:16px;height:16px;flex:0 0 auto}}
/* flights */
.flights{{display:grid;gap:9px}}
.fl{{display:flex;align-items:center;gap:11px;background:var(--card);border:1px solid var(--line);border-left:4px solid var(--jade);border-radius:12px;padding:11px 14px;box-shadow:var(--shadow);flex-wrap:wrap}}
.fl-badge{{font-size:11px;background:rgba(15,107,83,.14);color:var(--jade-d);padding:2px 8px;border-radius:999px;font-weight:700;flex:0 0 auto}}
.fl-main{{flex:1;min-width:180px;font-size:14px}}.fl-code{{display:block;color:var(--ink2);font-size:12.5px}}
.fl-time{{font-family:var(--lat);letter-spacing:.04em;color:var(--jade-d);font-weight:600}}
/* hotels */
.ho-area{{background:var(--card);border:1px solid var(--line);border-radius:13px;padding:14px 15px;box-shadow:var(--shadow)}}
.ho-area h4{{margin:0 0 3px;font-family:var(--serif);font-size:16px}}
.ho-opt{{display:flex;flex-wrap:wrap;align-items:baseline;gap:6px 9px;padding:8px 0;border-top:1px solid var(--line)}}
.ho-tier{{font-size:11px;background:rgba(224,161,51,.18);color:#9a6b14;padding:1px 8px;border-radius:999px}}
.ho-price{{color:var(--terra);font-size:13px}}.ho-note{{color:var(--ink2);font-size:12.5px;width:100%}}
/* map */
#map{{height:min(66vh,520px);border-radius:16px;border:1px solid var(--line);box-shadow:var(--shadow);z-index:0}}
.route-pin__num{{display:grid;place-items:center;width:28px;height:28px;border-radius:50%;background:var(--jade);color:#fff;font-weight:700;font-size:14px;border:2px solid #fff;box-shadow:0 2px 6px rgba(0,0,0,.3);font-family:var(--lat)}}
.leaflet-container{{font-family:var(--sans)}}
/* timeline */
.day{{margin:16px 0;background:var(--card);border:1px solid var(--line);border-radius:16px;padding:15px 16px;box-shadow:var(--shadow)}}
.day-head{{display:flex;align-items:baseline;gap:12px;flex-wrap:wrap;border-bottom:2px solid var(--ink);padding-bottom:9px;margin-bottom:11px}}
.day-date{{font-family:var(--serif);font-weight:600;font-size:19px}}.day-date em{{font-style:normal;color:var(--jade-d);font-size:15px}}
.day-theme{{color:var(--terra);font-size:14px}}
.daytips{{margin:0 0 11px;padding-left:18px;color:var(--ink2);font-size:13px}}
.slots{{display:grid;gap:11px}}
.slot{{border-left:3px solid var(--jade-l);padding:2px 0 2px 13px}}
.slot-h{{display:flex;gap:10px;align-items:baseline}}
.slot-p{{font-size:11px;background:var(--jade);color:#f7edd7;padding:1px 8px;border-radius:999px}}
.slot-t{{font-family:var(--lat);color:var(--ink2);font-size:13px}}
.slot-name{{font-family:var(--serif);font-weight:600;font-size:16px;margin:3px 0}}
.slot-r{{margin:2px 0;font-size:13.5px;color:var(--ink2)}}
.chips{{display:flex;flex-wrap:wrap;gap:5px;margin:5px 0}}
.chip{{font-size:12px;background:rgba(42,35,32,.05);border:1px solid var(--line);border-radius:8px;padding:1px 8px;color:var(--ink2)}}
.rbadge{{font-size:11px;background:rgba(193,82,47,.14);color:var(--terra);padding:1px 8px;border-radius:999px;margin-left:8px;white-space:nowrap}}
.navlink{{display:inline-block;margin-top:4px;font-size:13px;color:#fff;background:linear-gradient(150deg,var(--jade),var(--jade-d));padding:5px 12px;border-radius:999px;text-decoration:none;box-shadow:var(--shadow)}}
.dining{{margin-top:12px;background:rgba(224,161,51,.07);border-radius:11px;padding:10px 13px}}
.dining h5{{margin:0 0 6px;font-size:13px;color:#9a6b14;letter-spacing:.04em}}
.dine{{padding:5px 0;font-size:13.5px;border-top:1px dashed var(--line)}}.dine:first-of-type{{border-top:0}}
.dine-meal{{display:inline-block;font-size:11px;background:var(--gold);color:#3a2a06;padding:1px 8px;border-radius:999px;margin-right:7px}}
.dine .sub{{margin-left:7px}}.dishes{{color:var(--ink2);font-size:12.5px;margin-top:2px}}.dishes i{{color:var(--terra);font-style:normal}}
.tips{{margin:0;padding-left:20px}}.tips li{{margin:6px 0;font-size:14px}}
.disclaimer{{margin:16px 0;font-size:12px;color:var(--ink2);background:rgba(193,82,47,.06);border:1px dashed var(--terra);border-radius:12px;padding:12px 15px;line-height:1.65}}
footer{{text-align:center;color:var(--ink2);font-size:12.5px;padding:30px 10px;border-top:1px solid var(--line);margin-top:24px}}
footer a{{color:var(--jade-d)}}
@media(min-width:768px){{
  .grid2{{grid-template-columns:1fr 1fr}}
  .info-card.wide{{grid-column:1/3}}
  .slots{{grid-template-columns:1fr 1fr}}
  .day-head{{grid-column:1/3}}
}}
</style>
</head>
<body>
<div class="wrap">
  <header class="top">
    <div class="kick">A COUPLE&#39;S JOURNEY · 交互地图</div>
    <h1>{esc(trip['title'])}</h1>
    <div class="dates">2026 · 07 · 14 — 07 · 20</div>
    <p class="sub" style="margin-top:10px">👇 点击地图编号或行程卡片的「导航」按钮，一键跳转 <b>Google 地图</b></p>
  </header>

  <h2>🗺️ 全程路线地图</h2>
  <div id="map"></div>

  <h2>✅ 出发前待办</h2>
  {render_checklist()}

  <h2>📋 行前须知</h2>
  {render_pretrip()}

  <h2>✈️ 航班（已预订）</h2>
  {render_flights()}

  <h2>🏨 住宿（片区 + 价位）</h2>
  {render_hotels()}

  <div class="disclaimer">{esc(trip['disclaimer'])}</div>

  <h2>🗓️ 每日行程</h2>
  {render_timeline()}

  <h2>💡 全程实用贴士</h2>
  {render_tips()}

  <footer>
    🐘 {esc(trip['title'])} · 2026/7/14–7/20 ·
    <a href="./index.html">← 返回完整攻略</a><br>
    由 Claude + travel-plan-viz 生成 · 坐标为近似示意，导航以 Google 地图为准
  </footer>
</div>

<script id="trip-data" type="application/json">{trip_json}</script>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script>{reminders_js}</script>
<script>{map_js}</script>
<script>
(function(){{
  var trip = JSON.parse(document.getElementById('trip-data').textContent);
  // 用引擎重渲染出发前清单（离线可读，JS 增强）
  try {{
    var rem = computeReminders(trip.startDate, trip.reminders);
    var el = document.getElementById('checklist');
    if (el) el.outerHTML = renderChecklistHTML(rem).replace('pretrip-todo','checklist');
  }} catch(e) {{}}
  // 汇总所有 slot 为地图点位，按行程顺序
  var points = [];
  trip.days.forEach(function(d){{ (d.slots||[]).forEach(function(s){{
    if (typeof s.lat==='number' && typeof s.lng==='number')
      points.push({{lat:s.lat, lng:s.lng, name:s.name, time:(d.date.slice(5)+' '+(s.time||''))}});
  }});}});
  if (window.initTravelMap && points.length) initTravelMap('map', points);
}})();
</script>
</body>
</html>"""

out = os.path.join(ROOT, "map.html")
with open(out, "w", encoding="utf-8") as f:
    f.write(HTML)
n_points = sum(len(d["slots"]) for d in trip["days"])
print(f"wrote {out} — {len(HTML)} chars, {n_points} map points, {len(trip['days'])} days")
