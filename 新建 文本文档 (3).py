from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# ========== 全部已填好，直接复制使用 ==========
APP_ID = "cli_a931f171fd2789bcb"
APP_SECRET = "xxT4XD37PFYDygr8pVNhihbgN0Q4fhUgnq"
BITABLE_APP_TOKEN = "XymHbH9edaEAKiszzJOc7BXHn9e"
TABLE_ID = "tblQFMJ3v4SWfgQB"
# ==========================================

# 获取飞书 tenant_access_token
def get_tenant_token():
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    data = {"app_id": APP_ID, "app_secret": APP_SECRET}
    resp = requests.post(url, json=data)
    return resp.json().get("tenant_access_token", "")

# 写入飞书多维表格
def write_to_bitable(form_data):
    token = get_tenant_token()
    if not token:
        return {"code": -1, "msg": "获取token失败"}

    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{BITABLE_APP_TOKEN}/tables/{TABLE_ID}/records"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "fields": {
            "手机号码": form_data.get("phone", ""),
            "车辆品牌型号": form_data.get("car_model", ""),
            "上牌年份": form_data.get("year", ""),
            "车辆所在地": form_data.get("location", ""),
            "备注信息": form_data.get("remark", "")
        }
    }

    resp = requests.post(url, json=payload, headers=headers)
    return resp.json()

# Webhook 接收接口
@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form
        result = write_to_bitable(data)
        return jsonify({"status": "success", "feishu_result": result}), 200
    except Exception as e:
        return jsonify({"status": "fail", "error": str(e)}), 500

# 测试接口是否存活
@app.route("/")
def index():
    return "Webhook 服务运行正常，请使用 /webhook 路径接收数据"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)