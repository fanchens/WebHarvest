## 采集模块说明（`webharvest.collectors`）

本目录用于承载 **“按网站拆分的采集逻辑”**，配合项目的 **内置浏览器（WebView2/pywebview）** 完成登录、自动化与数据落地。

### 目录结构约定

- **`collectors/common/`**：采集公共能力（封控/限流/重试/保存/配置/日志等），所有站点可复用
- **`collectors/<site>/`**：单站点采集包（一个网站一个目录）
- **`collectors/<site>/tasks/`**：站点内的任务模块（主页、单作品、搜索、评论等按文件拆分）
- **`collectors/<site>/run.py`**：站点入口（可直接 `python -m ...` 运行）

建议形态：

```
webharvest/collectors/
  README.md
  __init__.py
  common/
    __init__.py
    anti_detection.py
    rate_limit.py
    retry.py
    storage.py
    config.py
    logger.py
    utils.py
  xiaohongshu/
    __init__.py
    config.py
    run.py
    tasks/
      __init__.py
      snapshot.py
      note.py
      profile.py
      search.py
```

### 站点命名规范（`<site>`）

- 使用 **小写英文**：`xiaohongshu`、`douyin`、`kuaishou`…
- 站点配置放在 `collectors/<site>/config.py`，至少包含：
  - **base_url**：站点首页
  - **login_url**：建议用户登录的入口页（便于首次扫码/登录）

### Cookie / 登录信息约定

- Cookie 统一由 `webharvest.browser.CookieManager` 管理与持久化
- 默认存储目录：
  - **源码运行**：`WebHarvest/data/cookies/`
  - **打包运行**：`%LOCALAPPDATA%\\WebHarvest\\data\\cookies\\`（用户可写，避免安装目录权限问题）
- 建议按 **域名** 分文件：`<domain>.json`（如 `www.xiaohongshu.com.json`）
- 采集入口一般遵循：
  - 打开页面后 **先 apply cookies（如有）**
  - 采集过程中周期性 **save cookies（仅变化时才写盘）**

### 数据输出约定

- 建议统一输出到：
  - **源码运行**：`WebHarvest/data/outputs/<site>/`
  - **打包运行**：`%LOCALAPPDATA%\\WebHarvest\\data\\outputs\\<site>\\`
- 文件命名建议携带时间戳，便于追溯
- 后续会把保存策略抽到 `collectors/common/storage.py`：
  - JSON（单文件/追加/JSONL）
  - CSV
  - SQLite（可选）
  - 去重策略（按 id/url）

### 封控 / 反检测（后续统一在 `collectors/common/`）

常见需要抽象成公共能力的点：
- **UA/Headers 策略**：统一管理、可按站点覆盖
- **行为节奏**：随机延迟、滚动策略、点击节奏
- **代理**：可选（对接你现有的代理池目录）
- **限流**：全局限流 + 站点限流
- **重试**：指数退避、错误分级（可重试/不可重试）

### 如何新增一个网站采集（推荐步骤）

1. 新建站点包：`collectors/<site>/`
2. 写 `config.py`：放站点 URL、必要选择器/规则
3. 写 `tasks/`：按任务拆文件（如 `note.py`、`search.py`）
4. 写 `run.py`：站点入口，先实现“能打开页面 + Cookie 正常保存”，再逐步补采集逻辑
5. 输出统一落到 `data/outputs/<site>/`

### 运行示例（以小红书为例）

在 `WebHarvest` 目录下：

```bash
python -m webharvest.collectors.xiaohongshu.run --login
```

说明：
- `--login`：打开建议登录页面，首次扫码/登录后 Cookie 会自动保存
- 后续可扩展更多参数：任务类型、目标 URL、保存格式等


