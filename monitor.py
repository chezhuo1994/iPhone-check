import os
import requests

# ================= 1. 微信 PushPlus 配置（已填入你的专属 Token） =================
PUSHPLUS_TOKEN = os.environ.get("PUSHPLUS_TOKEN", "2c17415a50b74e80af70bf91cf4c59dc")

# ================= 2. 俄勒冈州门店与 iPhone 18 Pro Max 真实型号代码 =================
ZIP_CODE = "97204"  # 波特兰市中心邮编（一次查询覆盖 OR 全州 3 家 Apple Store）

# 美版 iPhone 18 Pro Max 512GB & 1TB 官方 Part Number 列表
# （如果你只想要特定颜色，可以在不需要的那一行前面加 # 注释掉）
TARGET_MODELS = {
    # --- 512GB 全配色 ---
    "MJW84LL/A": "iPhone 18 Pro Max 512GB Black (黑色)",
    "MJW94LL/A": "iPhone 18 Pro Max 512GB Silver (银色)",
    "MJWA4LL/A": "iPhone 18 Pro Max 512GB Burgundy (酒红色)",
    "MJWC4LL/A": "iPhone 18 Pro Max 512GB Glacier (冰川蓝)",
    
    # --- 1TB 全配色 ---
    "MJWD4LL/A": "iPhone 18 Pro Max 1TB Black (黑色)",
    "MJWE4LL/A": "iPhone 18 Pro Max 1TB Silver (银色)",
    "MJWF4LL/A": "iPhone 18 Pro Max 1TB Burgundy (酒红色)",
    "MJWG4LL/A": "iPhone 18 Pro Max 1TB Glacier (冰川蓝)",
}
# ==============================================================================

def send_wechat_push(title, content):
    """通过 PushPlus 发送微信通知"""
    url = "http://www.pushplus.plus/send"
    data = {
        "token": PUSHPLUS_TOKEN,
        "title": title,
        "content": content.replace("\n", "<br>"),
        "template": "html"
    }
    try:
        res = requests.post(url, json=data, timeout=10)
        print(f"[微信推送结果] {res.text}")
    except Exception as e:
        print(f"[微信推送失败] {e}")

def check_oregon_stock():
    url = "https://www.apple.com/shop/fulfillment-messages"
    params = {
        "pl": "true",
        "mts.0": "regular",
        "location": ZIP_CODE
    }
    for idx, part in enumerate(TARGET_MODELS.keys()):
        params[f"parts.{idx}"] = part

    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1"
    }
    
    try:
        res = requests.get(url, params=params, headers=headers, timeout=12)
        if res.status_code != 200:
            print(f"请求受限，HTTP 状态码: {res.status_code}")
            return

        stores = res.json().get("body", {}).get("content", {}).get("pickupMessage", {}).get("stores", [])
        available_list = []

        for store in stores:
            # 严格只看俄勒冈州 (OR) 免税门店，过滤掉华盛顿州门店
            if store.get("address", {}).get("state") != "OR":
                continue
            
            store_name = store.get("storeName")
            store_num = store.get("storeNumber")
            parts_avail = store.get("partsAvailability", {})

            for part_num, model_name in TARGET_MODELS.items():
                info = parts_avail.get(part_num, {})
                if info.get("pickupDisplay") == "available":
                    quote = info.get("pickupSearchQuote", "今日可取")
                    available_list.append(f"📍 <b>{store_name} ({store_num})</b><br>📱 {model_name}<br>🛒 状态: {quote}<br>")

        # 如果发现任意一款有货，合并为一条微信消息立刻推送（避免一次刷屏多条触发 PushPlus 频率限制）
        if available_list:
            title = f"🎉 俄勒冈 Apple 发现 {len(available_list)} 款现货！"
            msg = "<br>".join(available_list) + "<br>👉 <b>快打开 Apple Store App 锁单！</b>"
            send_wechat_push(title, msg)
        else:
            print("俄勒冈 3 家门店当前暂无 512GB / 1TB 现货。")

    except Exception as e:
        print(f"查询异常: {e}")

if __name__ == "__main__":
    # 首次运行时如果想要测试微信能否收到，可以把下面这行前面的 # 删掉跑一次：
    send_wechat_push("🔔 俄勒冈监控已启动", "你的微信推送配置成功！一旦发现 iPhone 18 Pro Max 512G/1TB 现货会第一时间通知你。")
    check_oregon_stock()
