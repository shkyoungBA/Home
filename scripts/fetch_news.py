import json, urllib.request, urllib.parse, xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from datetime import datetime, timezone, timedelta

QUERIES = ["양재 ICT 특정개발진흥지구", "양재 ICT 진흥지구", "양재 AI특구"]
KST = timezone(timedelta(hours=9))
MAX_ITEMS = 60

def fetch(q):
    url = "https://news.google.com/rss/search?" + urllib.parse.urlencode(
        {"q": q + " when:30d", "hl": "ko", "gl": "KR", "ceid": "KR:ko"})
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        root = ET.fromstring(r.read())
    out = []
    for it in root.iter("item"):
        title = (it.findtext("title") or "").strip()
        link = (it.findtext("link") or "").strip()
        src = (it.findtext("source") or "").strip()
        if src and title.endswith(" - " + src):
            title = title[: -len(src) - 3]
        try:
            d = parsedate_to_datetime(it.findtext("pubDate")).astimezone(KST).strftime("%Y-%m-%d")
        except Exception:
            continue
        if title and link:
            out.append({"d": d, "t": title, "s": src, "u": link})
    return out

try:
    data = json.load(open("news.json", encoding="utf-8"))
except Exception:
    data = {"items": []}

items = data.get("items", [])
seen = {i["u"] for i in items} | {i["t"] for i in items}
for q in QUERIES:
    try:
        for n in fetch(q):
            if n["u"] in seen or n["t"] in seen:
                continue
            seen.add(n["u"]); seen.add(n["t"])
            items.append(n)
    except Exception as e:
        print("실패:", q, e)

items.sort(key=lambda x: x["d"], reverse=True)
data = {"updated": datetime.now(KST).strftime("%Y-%m-%d"), "items": items[:MAX_ITEMS]}
json.dump(data, open("news.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("총", len(data["items"]), "건")
