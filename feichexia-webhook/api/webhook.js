const axios = require('axios');

module.exports = async (req, res) => {
  // 允许跨域
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  // 处理预检请求
  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ error: '仅支持POST请求' });
  }

  try {
    const { appSecret, baseId, tableId, fields } = req.body;
    const feishuAppId = "cli_a93f171fd2789bcb";

    // 获取飞书Token
    const tokenRes = await axios.post(
      'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',
      { app_id: feishuAppId, app_secret: appSecret }
    );

    if (tokenRes.data.code !== 0) {
      return res.status(401).json({
        success: false,
        error: '获取Token失败',
        detail: tokenRes.data
      });
    }

    // 写入多维表格
    const tableRes = await axios.post(
      `https://open.feishu.cn/open-apis/bitable/v1/apps/${baseId}/tables/${tableId}/records`,
      { fields },
      { headers: { Authorization: `Bearer ${tokenRes.data.tenant_access_token}` } }
    );

    return res.json({
      success: true,
      msg: '写入成功',
      data: tableRes.data
    });

  } catch (err) {
    console.error('错误:', err);
    return res.status(500).json({
      success: false,
      error: '服务器错误',
      detail: err.response?.data || err.message
    });
  }
};