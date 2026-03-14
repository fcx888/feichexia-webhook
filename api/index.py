from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# 飞书配置
APP_ID = "cli_a93f171fd2789bcb"
APP_SECRET = "xxT4XD37PFYDygr8pVNhidgN0CQ4hUgnq"
BITABLE_APP_TOKEN = "XymHbH9edaEAKiszzJOc7BXHn9e"
TABLE_ID = "tblQFMJ3v4SWfgQB"

# 获取飞书 tenant_access_token
def get_tenant_token():
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    data = {
        "app_id": APP_ID,
        "app_secret": APP_SECRET
    }
    resp = requests.post(url, json=data)
    result = resp.json()
    return result.get("tenant_access_token", "")

# 写入飞书多维表格
def write_to_bitable(form_data):
    token = get_tenant_token()
    if not token:
        return {"code": -1, "msg": "获取token失败"}
    
    # 飞书多维表接口地址
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{BITABLE_APP_TOKEN}/tables/{TABLE_ID}/records"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    # 字段映射（和飞书表格中文列名完全一致）
    payload = {
        "fields": {
            "手机号": form_data.get("phone", ""),
            "车辆品牌型号": form_data.get("car_model", ""),
            "上牌年份": form_data.get("year", ""),
            "车辆所在地": form_data.get("location", ""),
            "备注信息": form_data.get("remark", "")
        }
    }
    resp = requests.post(url, json=payload, headers=headers)
    return resp.json()

# webhook 接收接口
@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form
        result = write_to_bitable(data)
        return jsonify({"status": "成功", "feishu_result": result}), 200
    except Exception as e:
        return jsonify({"status": "失败", "错误": str(e)}), 500

# 测试接口是否存活
@app.route("/")
def index():
    return "webhook 服务运行正常，请使用 /webhook 路径接收数据"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)