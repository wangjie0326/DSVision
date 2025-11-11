# LLM 配置指南

## 📋 配置文件位置

**主配置文件**: `/home/user/DSVision/.env`

## 🔧 配置步骤

### 1. 创建配置文件

```bash
# 复制示例配置文件
cp .env.example .env

# 或者手动创建
touch .env
```

### 2. 编辑 `.env` 文件

根据你使用的服务商配置以下参数:

```bash
# LLM提供商 (openai, claude等)
LLM_PROVIDER=openai

# API基础URL (可选,用于第三方API)
LLM_BASE_URL=https://api.kanzakiyui.xyz

# API密钥 (必填)
LLM_API_KEY=sk-nr6DkU5QITHkxmhYYAk4DBrj81S3SMDJH6r1zL4xaKubrct
```

## 🌍 常见场景配置

### A) 使用 OpenAI 官方 API

```bash
LLM_PROVIDER=openai
LLM_API_KEY=sk-proj-xxxxxx
# LLM_BASE_URL 留空或删除此行
```

### B) 使用第三方 OpenAI 兼容 API

```bash
LLM_PROVIDER=openai
LLM_BASE_URL=https://api.kanzakiyui.xyz
LLM_API_KEY=sk-nr6DkU5QITHkxmhYYAk4DBrj81S3SMDJH6r1zL4xaKubrct
```

### C) 使用 Claude API (开发中)

```bash
LLM_PROVIDER=claude
LLM_API_KEY=sk-ant-xxxxxx
# LLM_BASE_URL 留空
```

### D) 使用其他第三方代理

```bash
LLM_PROVIDER=openai
LLM_BASE_URL=https://your-proxy.com/v1
LLM_API_KEY=your-custom-api-key
```

## 🔄 更换平台/密钥时需要更新的地方

### ⚠️ 重要: 只需修改 `.env` 文件!

**你只需要修改项目根目录下的 `.env` 文件**, 无需修改任何代码文件。

修改后重启Flask服务器即可生效:

```bash
# 停止当前服务器 (Ctrl+C)
# 重新启动
python -m controller.app
```

### 配置参数说明

| 参数 | 说明 | 是否必填 | 示例 |
|------|------|---------|------|
| `LLM_PROVIDER` | LLM提供商类型 | 是 | `openai`, `claude` |
| `LLM_API_KEY` | API密钥 | 是 | `sk-proj-xxx` |
| `LLM_BASE_URL` | API基础URL | 否 | `https://api.example.com` |

## 🧪 测试配置

### 方式1: 使用测试脚本 (推荐)

```bash
# 在项目根目录运行
python test_llm_service.py
```

测试脚本会:
- ✅ 检查配置是否正确
- ✅ 测试API连接
- ✅ 执行5个预设测试用例
- ✅ 显示详细的调试信息

### 方式2: 直接测试 llm_service.py

```bash
# 运行 llm_service.py 内置测试
python -m dsvision.extend2_llm.llm_service
```

### 方式3: 通过 Flask 服务测试

```bash
# 1. 启动 Flask 服务器
python -m controller.app

# 2. 在另一个终端发送测试请求
curl -X POST http://localhost:5000/llm/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "创建一个包含5,3,7的二叉搜索树"}'
```

## 🛠️ 故障排查

### 问题1: "未设置 LLM_API_KEY"

**解决方案**: 检查 `.env` 文件是否存在且包含 `LLM_API_KEY=xxx`

```bash
# 检查文件是否存在
ls -la .env

# 查看文件内容
cat .env
```

### 问题2: "LLM服务未启用"

**可能原因**:
- `.env` 文件不在项目根目录
- API_KEY 格式错误
- 网络连接问题

**解决方案**:
```bash
# 确保 .env 在正确位置
pwd  # 应显示 /home/user/DSVision
ls .env

# 测试网络连接
curl https://api.openai.com/v1/models -H "Authorization: Bearer YOUR_KEY"
```

### 问题3: 第三方API连接失败

**解决方案**: 检查 `LLM_BASE_URL` 是否正确

```bash
# 测试URL是否可访问
curl https://api.kanzakiyui.xyz/v1/models \
  -H "Authorization: Bearer YOUR_KEY"
```

## 📁 相关文件

| 文件路径 | 说明 |
|---------|------|
| `/home/user/DSVision/.env` | **主配置文件** (需手动创建) |
| `/home/user/DSVision/.env.example` | 配置示例模板 |
| `/home/user/DSVision/dsvision/extend2_llm/llm_service.py` | LLM服务实现 |
| `/home/user/DSVision/controller/app.py` | Flask服务器(读取配置) |
| `/home/user/DSVision/test_llm_service.py` | 测试启动脚本 |

## 🔒 安全提示

- ⚠️ **切勿将 `.env` 文件提交到 Git**
- ⚠️ 确保 `.gitignore` 包含 `.env`
- ⚠️ 不要在代码中硬编码 API Key
- ✅ 使用环境变量管理敏感信息

检查 `.gitignore`:
```bash
grep ".env" .gitignore || echo ".env" >> .gitignore
```

## 📞 需要帮助?

如果配置遇到问题,请运行测试脚本获取详细错误信息:

```bash
python test_llm_service.py
```

或查看Flask服务器启动日志中的LLM配置部分。
