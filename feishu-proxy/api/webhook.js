const axios = require('axios');

module.exports = async (req, res) => {
  // 允许跨域请求
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  // 处理预检请求
  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ error: '方法不允许' });
  }

  try {
    // 1. 从前端获取参数（包含你的飞书应用凭证和多维表格信息）
    const {
      appSecret,   // 你的飞书 App Secret
      baseId,      // 多维表格 baseId
      tableId,     // 多维表格 tableId
      fields       // 表单字段数据
    } = req.body;

    // 2. 【关键】直接填入你的飞书 App ID (cli_a93f171fd2789bcb)
    const feishuAppId = "cli_a93f171fd2789bcb"; 

    // 3. 获取飞书 tenant_access_token
    const tokenResponse = await axios.post(
      'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',
      {
        app_id: feishuAppId,      // 使用固定的你的 App ID
        app_secret: appSecret    // 使用前端传过来的 Secret
      }
    );

    const { code, tenant_access_token } = tokenResponse.data;
    if (code !== 0) {
      return res.status(401).json({
        success: false,
        error: '获取飞书 Token 失败',
        detail: tokenResponse.data
      });
    }

    // 4. 写入飞书多维表格
    const createResponse = await axios.post(
      `https://open.feishu.cn/open-apis/bitable/v1/apps/${baseId}/tables/${tableId}/records`,
      { fields },
      {
        headers: {
          Authorization: `Bearer ${tenant_access_token}`
        }
      }
    );

    // 5. 返回成功结果
    return res.json({
      success: true,
      msg: '写入飞书成功',
      data: createResponse.data
    });

  } catch (error) {
    console.error('错误:', error);
    return res.status(500).json({
      success: false,
      error: '服务器内部错误',
      detail: error.response?.data || error.message
    });
  }
};