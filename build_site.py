#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build a self-contained index.html travel plan site from the TRAVEL/*.md files.
No external fonts/CDNs (China + offline friendly). Uses pandoc for md->html."""
import subprocess, re, os, datetime, urllib.parse
import build_map

_FAV = "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect width='100' height='100' rx='22' fill='#0f6b53'/><text x='50' y='74' font-size='60' text-anchor='middle' fill='#f7edd7' font-family='Georgia,serif'>&#3607;</text></svg>"
FAVICON = '<link rel="icon" href="data:image/svg+xml,' + urllib.parse.quote(_FAV) + '">'

ROOT = "/home/yuebiao/project/Tailand-travel-plan"
SRC  = os.path.join(ROOT, "TRAVEL")

ICON = {"note":"📝","tip":"💡","warning":"⚠️","important":"❗","info":"ℹ️",
        "question":"❓","example":"📋","bug":"🐞","success":"✅","failure":"❌",
        "danger":"🚨","abstract":"📄","todo":"☑️","caution":"⚠️","attention":"❗"}

def callouts_to_divs(md):
    """Convert Obsidian '> [!type] Title' callouts into pandoc fenced divs."""
    # flatten list-nested callouts ('- > [!tip] text') into an icon list item
    md = re.sub(r'(?m)^(\s*[-*]\s+)>\s*\[!(\w+)\][+-]?\s*(.*)$',
                lambda m: m.group(1)+ICON.get(m.group(2).lower(),"•")+" "+m.group(3), md)
    lines = md.split("\n"); out=[]; i=0
    head = re.compile(r'^\s*>\s?\[!(\w+)\]([+-]?)\s*(.*)$')
    while i < len(lines):
        m = head.match(lines[i])
        if m:
            ctype = m.group(1).lower(); title = m.group(3).strip()
            i += 1; body=[]
            while i < len(lines) and re.match(r'^\s*>', lines[i]):
                body.append(re.sub(r'^\s*>\s?','',lines[i])); i += 1
            ic = ICON.get(ctype,"•")
            out.append(f'::: {{.callout .ct-{ctype}}}')
            label = (ic+" "+title).strip() if title else ic
            out.append(f'[{label}]{{.callout-title}}')
            out.append('')
            out.extend(body if body else [""])
            out.append(':::'); out.append('')
            continue
        out.append(lines[i]); i += 1
    return "\n".join(out)

def md_to_html(path):
    with open(path, encoding="utf-8") as f:
        md = f.read()
    md = callouts_to_divs(md)
    fmt = "markdown+pipe_tables+fenced_divs+bracketed_spans+backtick_code_blocks-smart"
    p = subprocess.run(["pandoc","-f",fmt,"-t","html5","--wrap=none"],
                       input=md, capture_output=True, text=True)
    if p.returncode != 0:
        p = subprocess.run(["pandoc","-f","gfm","-t","html5"], input=md,
                            capture_output=True, text=True)
    html = p.stdout
    # first h1 becomes the section's lead; keep as-is
    return html

SECTIONS = [
    ("itinerary", "itinerary.md",      "逐日行程", "🗓️"),
    ("food",      "food_guide.md",     "美食",     "🍜"),
    ("transport", "transportation.md", "交通",     "🚕"),
    ("safety",    "safety_and_tips.md","安全须知", "🛡️"),
    ("budget",    "budget_summary.md", "预算",     "💰"),
]

TABS = [("overview","总览","🧭")] + [(s[0], s[2], s[3]) for s in SECTIONS]

def build_overview():
    flights = [
        ("7/14 二","长沙 CSX","曼谷廊曼 DMK","12:55–15:10","FD481 泰亚航"),
        ("7/15 三","曼谷廊曼 DMK","清迈 CNX","19:30–20:45","SL520 泰狮航"),
        ("7/19 日","清迈 CNX","曼谷素万那普 BKK","10:15–11:35","VZ2103 泰越捷"),
        ("7/20 一","曼谷 BKK → 海口","→ 长沙 CSX","11:05 起飞","HU7940 / HU7517 海航"),
    ]
    fh = "\n".join(
        f'<div class="fl"><div class="fl-d">{d}</div>'
        f'<div class="fl-r"><span>{a}</span><i>✈</i><span>{b}</span></div>'
        f'<div class="fl-t">{t}</div><div class="fl-n">{n}</div></div>'
        for d,a,b,t,n in flights)
    hotels = [
        ("曼谷 · 前段","The Quarter Ratchathewi by UHG","7/14 → 7/15 · 1 晚","已订",""),
        ("清迈 · 主场","Travelodge Nimman","7/15 → 7/19 · 4 晚 · 高级房","已订",""),
        ("曼谷 · 后段","True Siam Phayathai Hotel","7/19 → 7/20 · 1 晚 · ¥291 起 · 步行4分到ARL","查看/预订","hotel.html"),
    ]
    hh = "\n".join(
        (f'<a class="ho ho-link" href="{href}">' if href else '<div class="ho">')
        + f'<div class="ho-tag">{tag}</div><div class="ho-name">{name}</div>'
        + f'<div class="ho-meta">{meta}</div>'
        + f'<span class="ho-badge {"b-ok" if b=="已订" else ("b-link" if href else "b-todo")}">{b}{" →" if href else ""}</span>'
        + ('</a>' if href else '</div>')
        for tag,name,meta,b,href in hotels)
    facts = [
        ("🛂","签证 / 入境","中泰互免 · ≤30 天免签；抵前 72h 填 <b>TDAC</b>（tdac.immigration.go.th·认准 .go.th）"),
        ("☔","七月天气","雨季/绿色季 · 午后阵雨为主 · 清迈 31–32℃ / 曼谷 32–34℃ · 非雾霾季空气好"),
        ("🚨","紧急电话","旅游警察 <b>1155</b>（英语）· 报警 <b>191</b> · 急救 <b>1669</b>"),
        ("💱","货币","泰铢 THB · 1 THB ≈ ¥0.20 · SuperRich 换汇最优 · 街摊/双条只收现金"),
        ("📱","叫车 App","Grab / Bolt / inDrive · 清迈红双条 30–40฿/人 · 曼谷 ARL 进城 45฿"),
        ("🔌","插座","220V · A/B/C 型 · 中国两脚插头可直插"),
    ]
    ff = "\n".join(
        f'<div class="qf"><div class="qf-i">{i}</div><div class="qf-b"><h4>{t}</h4><p>{d}</p></div></div>'
        for i,t,d in facts)
    return f"""
<div class="hero">
  <div class="hero-kicker">A COUPLE&#39;S JOURNEY · 情侣 7 日</div>
  <h1 class="hero-title">泰国<span class="ht-sub">清迈 <em>×</em> 曼谷</span></h1>
  <div class="hero-dates">2026 · 07 · 14 &nbsp;—&nbsp; 07 · 20</div>
  <div class="hero-tags"><span>自然户外 · 大象</span><span>美食 · 夜市</span><span>按摩 SPA · 咖啡慢生活</span></div>
  <div class="hero-scroll">曼谷 1.5 天 → 清迈 3.5 天（主场） → 曼谷 1 天</div>
</div>

<a href="./map.html" style="display:block;text-align:center;margin:8px 0 2px;padding:12px 16px;border-radius:14px;text-decoration:none;font-family:var(--cjk-serif);font-size:14px;letter-spacing:.02em;color:var(--ink2);background:var(--card);border:1px solid var(--line)">🗺️ 手绘地图也有独立版 →</a>

<h2 class="sec-h"><span class="sec-no">01</span>航班</h2>
<div class="flights">{fh}</div>

<h2 class="sec-h"><span class="sec-no">02</span>住宿</h2>
<div class="hotels">{hh}</div>

<h2 class="sec-h"><span class="sec-no">03</span>出行速查</h2>
<div class="qfacts">{ff}</div>

<div class="ov-note">📌 下面每个标签页是一份完整攻略：<b>逐日行程 / 美食 / 交通 / 安全须知 / 预算</b>。手机上可左右滑动查看表格。出行前请对 ⚠️ 项（签证 TDAC、汇率、营业时间、打车费）再做复核。</div>
"""

def _inject_day_maps(itinerary_html):
    """Inject hand-drawn map cards after each day's <h2> heading in itinerary."""
    fragments = build_map.render_day_fragments()
    # Match <h2> headings like: 🗓️ 7/14 周二 · ...
    pattern = re.compile(r'(<h2[^>]*>.*?7/(\d{2})\s*周.*?</h2>)', re.DOTALL)
    def replacer(m):
        h2 = m.group(1)
        day_num = int(m.group(2))
        frag = fragments.get(day_num, "")
        return h2 + "\n" + frag if frag else h2
    return pattern.sub(replacer, itinerary_html)

def main():
    today = datetime.date.today().isoformat()
    # nav
    nav = "".join(
        f'<button class="tab{" on" if k=="overview" else ""}" data-tab="{k}">'
        f'<i>{ic}</i><span>{label}</span></button>'
        for k,label,ic in TABS)
    # sections
    secs = [f'<section id="sec-overview" class="panel on">{build_overview()}</section>']
    for key, fn, label, ic in SECTIONS:
        body = md_to_html(os.path.join(SRC, fn))
        if key == "itinerary":
            body = _inject_day_maps(body)
        secs.append(f'<section id="sec-{key}" class="panel"><div class="md">{body}</div></section>')
    sections_html = "\n".join(secs)

    html = HEAD.replace("<!--FAVICON-->", FAVICON) + f"""
{build_map.DEFS}
<div class="grain"></div>
<header class="site">
  <div class="brand"><span class="brand-mark">ท</span><div><b>泰国行程手账</b><small>Chiang Mai × Bangkok</small></div></div>
  <nav class="tabs">{nav}</nav>
</header>
<main class="wrap">
{sections_html}
</main>
<footer class="foot">
  <div>🐘 泰国清迈 × 曼谷 · 情侣 7 日 · 2026/7/14–7/20</div>
  <div class="foot-sub">由 Claude 多智能体研究生成 · 更新于 {today} · 价格/营业时间/签证规则为 2026/7 参考，出行前请复核 ⚠️</div>
</footer>
{SCRIPT}
<script>
/* Grab 深链：点按先尝试唤起 App，未安装/桌面端则回退 grab.com */
document.addEventListener('click',function(e){{
  var a=e.target.closest('a.grab');if(!a)return;
  var app=a.getAttribute('href'),fb=a.getAttribute('data-fb');
  if(!app||app.indexOf('grab://')!==0){{return;}}
  e.preventDefault();var t=Date.now();
  setTimeout(function(){{if(!document.hidden&&Date.now()-t<1700){{window.location=fb;}}}},1200);
  window.location=app;
}});
</script>
</body></html>"""
    out = os.path.join(ROOT, "index.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    print("wrote", out, len(html), "bytes")

HEAD = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#0f6b53">
<!--FAVICON-->
<title>泰国清迈 × 曼谷 · 情侣 7 日行程手账</title>
<meta name="description" content="2026/7/14–7/20 泰国清迈+曼谷情侣自由行：逐日行程、美食、交通、安全、预算全攻略。">
<style>
:root{
  --paper:#f6efe1; --paper2:#efe4cf; --ink:#2a2320; --ink2:#5c5044;
  --jade:#0f6b53; --jade-d:#0a4f3d; --jade-l:#3f9b7f;
  --gold:#e0a133; --terra:#c1522f; --magenta:#bd3b73;
  --card:#fbf6ec; --line:rgba(42,35,32,.13); --line2:rgba(42,35,32,.08);
  --shadow:0 1px 2px rgba(42,35,32,.06),0 10px 30px -12px rgba(42,35,32,.22);
  --cjk-serif:"Songti SC","Noto Serif SC","Source Han Serif SC",STSong,"SimSun",serif;
  --cjk-sans:"PingFang SC","Hiragino Sans GB","Microsoft YaHei","Noto Sans SC",system-ui,sans-serif;
  --lat:"Georgia","Times New Roman",serif;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth;-webkit-text-size-adjust:100%}
body{
  margin:0;background:var(--paper);color:var(--ink);
  font-family:var(--cjk-sans);font-size:16px;line-height:1.75;letter-spacing:.01em;
  background-image:
    radial-gradient(60vw 60vw at 88% -8%, rgba(224,161,51,.20), transparent 60%),
    radial-gradient(55vw 55vw at -12% 6%, rgba(15,107,83,.16), transparent 60%),
    radial-gradient(50vw 50vw at 50% 118%, rgba(189,59,115,.13), transparent 60%);
  background-attachment:fixed;
}
.grain{position:fixed;inset:0;z-index:0;pointer-events:none;opacity:.5;mix-blend-mode:multiply;
  background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='140' height='140'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.85' numOctaves='2' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='.55'/%3E%3C/svg%3E");}
/* header */
.site{position:sticky;top:0;z-index:20;display:flex;align-items:center;gap:14px;
  padding:10px clamp(14px,4vw,40px);background:rgba(246,239,225,.86);
  backdrop-filter:saturate(1.4) blur(12px);-webkit-backdrop-filter:saturate(1.4) blur(12px);
  border-bottom:1px solid var(--line);}
.brand{display:flex;align-items:center;gap:11px;flex:0 0 auto}
.brand-mark{display:grid;place-items:center;width:40px;height:40px;border-radius:12px;
  background:linear-gradient(150deg,var(--jade),var(--jade-d));color:#f7edd7;
  font-size:22px;font-family:var(--cjk-serif);box-shadow:var(--shadow);transform:rotate(-4deg)}
.brand b{font-family:var(--cjk-serif);font-size:16px;letter-spacing:.04em;display:block;line-height:1.15}
.brand small{color:var(--ink2);font-size:11px;letter-spacing:.14em;text-transform:uppercase;font-family:var(--lat)}
.tabs{display:flex;gap:4px;overflow-x:auto;scrollbar-width:none;margin-left:auto;padding:2px}
.tabs::-webkit-scrollbar{display:none}
.tab{flex:0 0 auto;display:flex;align-items:center;gap:6px;border:1px solid transparent;
  background:transparent;color:var(--ink2);font-family:var(--cjk-sans);font-size:14px;
  padding:8px 13px;border-radius:999px;cursor:pointer;transition:.22s;white-space:nowrap}
.tab i{font-style:normal;font-size:15px}
.tab:hover{background:var(--paper2);color:var(--ink)}
.tab.on{background:linear-gradient(150deg,var(--jade),var(--jade-d));color:#f7edd7;
  box-shadow:var(--shadow);border-color:transparent}
.tab.on span{font-weight:600}
/* layout */
.wrap{position:relative;z-index:1;max-width:900px;margin:0 auto;padding:clamp(18px,4vw,42px) clamp(14px,4vw,40px) 60px}
.panel{display:none;animation:rise .5s cubic-bezier(.2,.7,.2,1) both}
.panel.on{display:block}
@keyframes rise{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}
/* hero */
.hero{position:relative;padding:min(11vw,74px) 0 30px;text-align:center}
.hero-kicker{font-family:var(--lat);letter-spacing:.32em;text-transform:uppercase;font-size:12px;
  color:var(--terra);margin-bottom:16px;animation:rise .6s .02s both}
.hero-title{font-family:var(--cjk-serif);font-weight:600;line-height:.98;margin:0;
  font-size:clamp(58px,17vw,132px);letter-spacing:.02em;
  background:linear-gradient(160deg,var(--jade-d),var(--jade) 55%,var(--terra));
  -webkit-background-clip:text;background-clip:text;color:transparent;animation:rise .6s .08s both}
.ht-sub{display:block;font-size:clamp(19px,5.4vw,34px);letter-spacing:.12em;margin-top:12px;
  -webkit-text-fill-color:var(--ink);color:var(--ink);font-weight:500}
.ht-sub em{font-family:var(--lat);font-style:italic;color:var(--gold);padding:0 4px}
.hero-dates{font-family:var(--lat);letter-spacing:.24em;font-size:clamp(15px,3.6vw,20px);
  color:var(--ink2);margin-top:20px;animation:rise .6s .16s both}
.hero-tags{display:flex;flex-wrap:wrap;gap:9px;justify-content:center;margin-top:24px;animation:rise .6s .24s both}
.hero-tags span{font-size:13px;padding:6px 14px;border:1px solid var(--line);border-radius:999px;
  background:var(--card);color:var(--ink2);box-shadow:var(--shadow)}
.hero-scroll{margin-top:26px;font-size:13.5px;color:var(--jade-d);font-weight:600;letter-spacing:.02em;animation:rise .6s .32s both}
/* section headings in overview */
.sec-h{display:flex;align-items:baseline;gap:12px;font-family:var(--cjk-serif);font-weight:600;
  font-size:23px;margin:44px 0 16px;padding-bottom:11px;border-bottom:2px solid var(--ink);letter-spacing:.03em}
.sec-no{font-family:var(--lat);font-style:italic;font-size:16px;color:var(--terra);letter-spacing:.05em}
/* flights */
.flights{display:grid;gap:10px}
.fl{display:grid;grid-template-columns:64px 1fr auto;gap:8px 14px;align-items:center;
  background:var(--card);border:1px solid var(--line);border-left:4px solid var(--jade);
  border-radius:13px;padding:13px 16px;box-shadow:var(--shadow)}
.fl-d{font-family:var(--cjk-serif);font-size:15px;font-weight:600;color:var(--jade-d)}
.fl-r{display:flex;align-items:center;gap:9px;flex-wrap:wrap;font-size:14.5px}
.fl-r i{color:var(--gold);font-style:normal}
.fl-t{grid-column:2;font-family:var(--lat);letter-spacing:.06em;color:var(--ink2);font-size:13.5px}
.fl-n{grid-column:3;grid-row:1/3;align-self:center;font-size:12.5px;color:var(--ink2);text-align:right;max-width:110px}
/* hotels */
.hotels{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:12px}
.ho{position:relative;background:var(--card);border:1px solid var(--line);border-radius:14px;
  padding:16px 16px 15px;box-shadow:var(--shadow);overflow:hidden}
.ho::before{content:"";position:absolute;inset:0 auto 0 0;width:4px;background:linear-gradient(var(--gold),var(--terra))}
.ho-tag{font-size:11.5px;letter-spacing:.14em;text-transform:uppercase;color:var(--terra);font-family:var(--lat)}
.ho-name{font-family:var(--cjk-serif);font-size:16.5px;font-weight:600;margin:5px 0 3px;line-height:1.35}
.ho-meta{font-size:13px;color:var(--ink2)}
.ho-badge{position:absolute;top:13px;right:13px;font-size:11px;padding:3px 9px;border-radius:999px;font-weight:600}
.b-ok{background:rgba(15,107,83,.14);color:var(--jade-d)}
.b-todo{background:rgba(193,82,47,.15);color:var(--terra)}
.ho-link{text-decoration:none;color:inherit;display:block;transition:.2s}
.ho-link:hover{transform:translateY(-2px);box-shadow:0 8px 24px -8px rgba(42,35,32,.34);border-color:var(--jade-l)}
.b-link{background:linear-gradient(150deg,var(--jade),var(--jade-d));color:#f7edd7}
/* quick facts */
.qfacts{display:grid;grid-template-columns:repeat(auto-fit,minmax(255px,1fr));gap:12px}
.qf{display:flex;gap:13px;background:var(--card);border:1px solid var(--line);border-radius:14px;padding:15px;box-shadow:var(--shadow)}
.qf-i{font-size:23px;flex:0 0 auto;filter:saturate(1.1)}
.qf-b h4{margin:0 0 4px;font-family:var(--cjk-serif);font-size:15.5px;letter-spacing:.02em}
.qf-b p{margin:0;font-size:13.5px;color:var(--ink2);line-height:1.6}
.qf-b b{color:var(--jade-d)}
.ov-note{margin:34px 0 6px;padding:16px 18px;border-radius:14px;font-size:14px;line-height:1.7;
  background:linear-gradient(150deg,rgba(15,107,83,.09),rgba(224,161,51,.09));
  border:1px dashed var(--jade-l);color:var(--ink)}
.ov-note b{color:var(--jade-d)}
/* ---- markdown content ---- */
.md{font-size:15.5px}
.md>h1{font-family:var(--cjk-serif);font-weight:600;font-size:clamp(27px,6vw,38px);
  line-height:1.2;margin:6px 0 20px;letter-spacing:.02em;
  background:linear-gradient(160deg,var(--jade-d),var(--terra));-webkit-background-clip:text;background-clip:text;color:transparent}
.md h2{font-family:var(--cjk-serif);font-weight:600;font-size:22px;letter-spacing:.02em;
  margin:40px 0 14px;padding:9px 0 9px 15px;border-left:5px solid var(--jade);
  background:linear-gradient(90deg,rgba(15,107,83,.09),transparent);border-radius:0 10px 10px 0}
.md h3{font-family:var(--cjk-serif);font-weight:600;font-size:18px;margin:26px 0 10px;color:var(--jade-d);letter-spacing:.02em}
.md h4{font-size:15.5px;margin:20px 0 8px;color:var(--terra);font-weight:700}
.md p{margin:11px 0}
.md a{color:var(--jade-d);text-decoration:none;border-bottom:1.5px solid rgba(15,107,83,.32);transition:.18s;word-break:break-word}
.md a:hover{border-bottom-color:var(--jade);background:rgba(15,107,83,.07)}
.md strong{color:var(--ink);font-weight:700}
.md em{color:var(--terra)}
.md ul,.md ol{margin:11px 0;padding-left:22px}
.md li{margin:5px 0}
.md ul li::marker{color:var(--gold)}
.md hr{border:0;height:1px;background:var(--line);margin:30px 0;position:relative}
.md hr::after{content:"❋";position:absolute;left:50%;top:-12px;transform:translateX(-50%);
  background:var(--paper);padding:0 12px;color:var(--gold);font-size:14px}
.md code{font-family:ui-monospace,"SFMono-Regular",Menlo,Consolas,monospace;font-size:.9em;
  background:var(--paper2);padding:1.5px 6px;border-radius:6px;color:var(--terra)}
.md blockquote{margin:14px 0;padding:2px 16px;border-left:3px solid var(--line);color:var(--ink2)}
/* tables */
.md table{width:100%;border-collapse:collapse;margin:16px 0;font-size:13.8px;
  display:block;overflow-x:auto;white-space:nowrap;-webkit-overflow-scrolling:touch;
  border:1px solid var(--line);border-radius:12px}
.md thead th{background:linear-gradient(150deg,var(--jade),var(--jade-d));color:#f7edd7;
  font-family:var(--cjk-serif);font-weight:600;text-align:left;padding:11px 13px;position:sticky;top:0}
.md tbody td{padding:10px 13px;border-top:1px solid var(--line2);vertical-align:top}
.md tbody tr:nth-child(even){background:rgba(42,35,32,.028)}
.md tbody tr:hover{background:rgba(224,161,51,.10)}
/* callouts */
.callout{margin:16px 0;padding:14px 16px 12px;border-radius:13px;border:1px solid var(--line);
  border-left:4px solid var(--jade);background:var(--card);box-shadow:var(--shadow)}
.callout .callout-title{display:block;font-family:var(--cjk-serif);font-weight:700;font-size:15px;
  margin-bottom:6px;color:var(--jade-d);letter-spacing:.01em}
.callout>p{margin:7px 0}
.callout>p:last-child{margin-bottom:0}
.ct-warning,.ct-caution{border-left-color:var(--gold);background:linear-gradient(150deg,rgba(224,161,51,.13),var(--card) 60%)}
.ct-warning .callout-title,.ct-caution .callout-title{color:#a9781a}
.ct-important,.ct-danger,.ct-failure,.ct-bug,.ct-attention{border-left-color:var(--terra);background:linear-gradient(150deg,rgba(193,82,47,.12),var(--card) 60%)}
.ct-important .callout-title,.ct-danger .callout-title,.ct-failure .callout-title,.ct-bug .callout-title{color:var(--terra)}
.ct-tip,.ct-success{border-left-color:var(--jade-l);background:linear-gradient(150deg,rgba(63,155,127,.13),var(--card) 60%)}
.ct-note,.ct-info,.ct-abstract{border-left-color:var(--jade);background:linear-gradient(150deg,rgba(15,107,83,.09),var(--card) 60%)}
.ct-example,.ct-question,.ct-todo{border-left-color:var(--magenta);background:linear-gradient(150deg,rgba(189,59,115,.10),var(--card) 60%)}
.ct-example .callout-title,.ct-question .callout-title{color:var(--magenta)}
/* footer */
.foot{position:relative;z-index:1;text-align:center;padding:34px 20px 46px;color:var(--ink2);
  font-size:13px;border-top:1px solid var(--line);margin-top:20px}
.foot-sub{font-size:12px;margin-top:7px;opacity:.85}
/* backtotop */
.top{position:fixed;right:16px;bottom:16px;z-index:30;width:46px;height:46px;border-radius:50%;
  border:1px solid var(--line);background:var(--card);color:var(--jade-d);font-size:19px;cursor:pointer;
  box-shadow:var(--shadow);opacity:0;transform:translateY(12px);transition:.28s;display:grid;place-items:center}
.top.show{opacity:1;transform:none}
@media(max-width:560px){
  body{font-size:15.5px}
  .brand small{display:none}
  .fl{grid-template-columns:56px 1fr;}
  .fl-n{grid-column:1/3;grid-row:auto;text-align:left;max-width:none}
  .fl-t{grid-column:2}
}
/* ---- hand-drawn map cards (from build_map) ---- */
.daycard{margin:20px 0;background:var(--card);border:1px solid var(--line);border-radius:18px;padding:15px clamp(12px,3vw,20px) 17px;box-shadow:var(--shadow);scroll-margin-top:16px;position:relative}
.daycard::before{content:"";position:absolute;left:0;top:20px;bottom:20px;width:5px;border-radius:0 5px 5px 0;background:var(--accent);opacity:.9}
.dh{display:flex;flex-wrap:wrap;align-items:baseline;gap:6px 12px;margin:0 0 8px}
.dd{font-family:var(--lat);font-size:14px;color:var(--terra);font-weight:600;letter-spacing:.04em}
.dd em{font-style:normal;color:var(--ink2);font-weight:400}
.dt{font-family:var(--cjk-serif);font-size:17px;font-weight:600}
.tips{list-style:none;margin:8px 0 12px;padding:0;font-size:13px;color:var(--ink2);line-height:1.6}
.tips li::before{content:"💡 "}
svg.map{display:block;width:100%;height:auto;border-radius:16px;filter:drop-shadow(0 8px 22px rgba(42,35,32,.14))}
svg.map a{cursor:pointer}
svg.map a:hover path[stroke]{stroke-width:2}
.stops{list-style:none;margin:13px 0 0;padding:0;display:grid;gap:7px}
.stops li{display:grid;grid-template-columns:auto 1fr;column-gap:10px;row-gap:6px;align-items:center;color:var(--ink);background:rgba(255,255,255,.5);border:1px solid var(--line);border-radius:12px;padding:9px 12px}
.sn{grid-column:1;grid-row:1;width:25px;height:25px;border-radius:50%;background:var(--accent);color:#fbf6ec;display:grid;place-items:center;font-family:var(--lat);font-weight:700;font-size:13.5px;box-shadow:0 2px 5px rgba(42,35,32,.25)}
.st{grid-column:2;grid-row:1;min-width:0;display:flex;flex-direction:column}
.st b{font-family:var(--cjk-serif);font-weight:600;font-size:14px;line-height:1.34}
.st i{font-style:normal;color:var(--ink2);font-size:11.5px;font-family:var(--lat)}
.acts{grid-column:1/-1;grid-row:2;display:flex;flex-wrap:wrap;gap:6px;justify-content:flex-end}
.btn{font-size:12px;text-decoration:none;white-space:nowrap;padding:5px 11px;border-radius:999px;transition:transform .12s}
.btn:active{transform:scale(.94)}
.go{color:#fff;background:linear-gradient(150deg,var(--jade),var(--jade-d));box-shadow:0 2px 6px rgba(10,79,61,.28)}
.grab{color:#fff;background:#00b14f;font-weight:600;box-shadow:0 2px 6px rgba(0,177,79,.32)}
@media(min-width:560px){.stops li{grid-template-columns:auto 1fr auto}.acts{grid-column:3;grid-row:1;flex-wrap:nowrap}}
</style>
</head>
<body>
"""

SCRIPT = """
<button class="top" id="toTop" aria-label="回到顶部">↑</button>
<script>
(function(){
  var tabs=[].slice.call(document.querySelectorAll('.tab'));
  var panels=[].slice.call(document.querySelectorAll('.panel'));
  function show(key,push){
    tabs.forEach(function(t){t.classList.toggle('on',t.dataset.tab===key)});
    panels.forEach(function(p){p.classList.toggle('on',p.id==='sec-'+key)});
    var act=document.querySelector('.tab[data-tab="'+key+'"]');
    if(act)act.scrollIntoView({inline:'center',block:'nearest'});
    if(push)history.replaceState(null,'','#'+key);
    window.scrollTo({top:0,behavior:'smooth'});
  }
  tabs.forEach(function(t){t.addEventListener('click',function(){show(t.dataset.tab,true)})});
  var h=(location.hash||'').replace('#','');
  if(h&&document.getElementById('sec-'+h))show(h,false);
  var top=document.getElementById('toTop');
  addEventListener('scroll',function(){top.classList.toggle('show',scrollY>640)},{passive:true});
  top.addEventListener('click',function(){window.scrollTo({top:0,behavior:'smooth'})});
})();
</script>
"""

if __name__ == "__main__":
    main()
