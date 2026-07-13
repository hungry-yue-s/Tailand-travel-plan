# 泰国清迈 + 曼谷 旅行计划（2026.7.15 – 7.20）

情侣 2 人 · 清迈为主（约 3.5 天）+ 曼谷（约 1 天）· 均衡节奏。

## ✈️ 航班

| 日期 | 航段 | 航班 | 起飞 | 到达 |
|---|---|---|---|---|
| 7/14 周二 | 长沙 → 曼谷廊曼 (DMK) | FD481 泰亚航 | 12:55 | 15:10 |
| 7/15 周三 | 曼谷廊曼 (DMK) → 清迈 (CNX) | SL520 泰狮航 | 19:30 | 20:45 |
| 7/19 周日 | 清迈 (CNX) → 曼谷素万那普 (BKK) | VZ2103 泰越捷 | 10:15 | 11:35 |
| 7/20 周一 | 曼谷素万那普 (BKK) → 海口 | HU7940 海航 | 11:05 | 14:40 |
| 7/20 周一 | 海口 → 长沙 | HU7517 海航 | 16:30 | 18:35 |

> 注意：7/14 抵达**廊曼 (DMK)** 后在曼谷住 1 晚；7/15 傍晚从廊曼飞清迈。7/19 飞曼谷落地的是**素万那普 (BKK)**，与廊曼不是同一机场。

## 🏨 住宿

- **曼谷（前段）**：The Quarter Ratchathewi by UHG（Ratchathewi 区，388 Phetchaburi Rd），7/14 入住、7/15 离店
- **清迈**：Travelodge Nimman（宁曼路核心区），7/15 入住 4 晚、7/19 离店，高级房 ×1
- **曼谷（后段）**：True Siam Phayathai Hotel（Phaya Thai/Ratchathewi，步行 4 分到 ARL 机场快线），7/19 入住、7/20 离店 · **已订**

## 🧭 行程重心

- 自然户外 / 动物 / 探险（粘粘瀑布、便便造纸园、**丛林飞跃**）
- 美食 / 夜市 / 街头小吃 / **昭披耶河夜游船**
- 按摩 SPA / 咖啡馆 / 慢生活

## 📂 计划文档结构

```
TRAVEL/
├── itinerary.md          逐日行程
├── food_guide.md         美食 / 夜市
├── transportation.md     交通
├── safety_and_tips.md    天气 / 签证 TDAC / 安全 / 文化
└── budget_summary.md     预算
```

## 🛠️ 构建 & 部署

站点由 Python 从 `TRAVEL/*.md` 生成，产物无运行时依赖、无 CDN（离线 / 国内友好）。

- **依赖**：Python 3 + [pandoc](https://pandoc.org/installing.html)（Markdown → HTML）
- **构建**：`python build_site.py` → 生成 `index.html`（含内嵌逐日手绘地图 + 导航/Grab 按钮）
- `build_map.py` 是 `build_site.py` 调用的库（手绘 SVG 地图），无需单独运行
- `hotel.html` 为手写页面，不经构建
- **部署**：推送到 GitHub Pages（`.nojekyll` 已就位，直接服务静态文件）
