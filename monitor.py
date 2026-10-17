import requests

# ================= 1. ntfy 推送配置（已精确匹配你截图中的订阅名） =================
NTFY_TOPIC = "oregon_iphone_chezhuo"

# ================= 2. 俄勒冈州门店与 iPhone 18 Pro Max 型号代码 =================
ZIP_CODE = "97204"  # 波特兰市中心邮编（覆盖 OR 全州 3 家免税店）

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

def send_push(title, content):
    """通过 ntfy 发送手机弹窗通知"""
    url = f"https://ntfy.sh/{NTFY_TOPIC}"
    headers = {
        "Priority": "high",
        "Tags": "iphone,tada"
    }
    full_message = f"【{title}】\n{content}"
    try:
        res = requests.post(url, data=full_message.encode("utf-8"), headers=headers, timeout=10)
        print(f"[ntfy 推送状态] HTTP {res.status_code}")
    except Exception as e:
        print(f"[推送失败] {e}")

def check_oregon_stock():
    url = "https://www.apple.com/shop/fulfillment-messages"
    params = {"pl": "true", "mts.0": "regular", "location": ZIP_CODE}
    for idx, part in enumerate(TARGET_MODELS.keys()):
        params[f"parts.{idx}"] = part

    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1"
    }
    
    try:
        res = requests.get(url, params=params, headers=headers, timeout=12)
        if res.status_code != 200:
            print(f"请求受限，状态码: {res.status_code}")
            return

        stores = res.json().get("body", {}).get("content", {}).get("pickupMessage", {}).get("stores", [])
        available_list = []

        for store in stores:
            if store.get("address", {}).get("state") != "OR":
                continue
            store_name = store.get("storeName")
            store_num = store.get("storeNumber")
            parts_avail = store.get("partsAvailability", {})

            for part_num, model_name in TARGET_MODELS.items():
                info = parts_avail.get(part_num, {})
                if info.get("pickupDisplay") == "available":
                    quote = info.get("pickupSearchQuote", "今日可取")
                    available_list.append(f"📍 {store_name} ({store_num})\n📱 {model_name} ({quote})")

        if available_list:
            title = f"🎉 俄勒冈发现 {len(available_list)} 款 iPhone 现货！"
            msg = "\n\n".join(available_list) + "\n\n👉 快打开 Apple Store App 锁单！"
            send_push(title, msg)
        else:
            print("俄勒冈 3 家门店当前暂无 512GB / 1TB 现货。")

    except Exception as e:
        print(f"查询异常: {e}")

if __name__ == "__main__":
    # 测试开关（收到手机弹窗后，记得把下面这行最前面加上 # 注释掉并保存）：
    send_push("🔔 俄勒冈监控已启动", "ntfy 推送配置成功！一旦刷出 512G/1TB 现货会第一时间弹窗提醒你。")
    check_oregon_stock()
