## WebHarvest 采集工具说明文档（设计阶段）

> 当前阶段仅做设计与说明，不落地具体代码。  
> 代码计划放在：`E:\PyCharm\PythonProject\WebHarvest`

---
 
## 一、项目目标

- **项目名称**：WebHarvest Windows 桌面采集工具  
- **形态**：Windows 桌面应用，最终以 **可安装 EXE 安装包** 形式分发（非单文件 EXE）。  
- **核心能力**：
  - 静态网页高并发采集（Requests 引擎）
  - 动态网页 / 登录站点采集（QWebEngineView 引擎）
  - 自动重试与代理切换
  - 采集结果本地化存储（SQLite + 文件夹）
  - 可视化配置与进度监控界面

---

## 二、技术栈规划

- **语言 & 框架**
  - Python 3.x
  - PySide6（含 `QWebEngineView`，用于 UI + 浏览器模拟）

- **采集与解析**
  - `requests` + `requests` 代理配置（HTTP/HTTPS 代理）
  - `tenacity`（网络请求 / 解析的失败重试策略）
  - `newspaper4k`（主力文本提取）
  - `trafilatura`（高精度文本提取补充，作为降级或兜底）

- **存储与导出**
  - `sqlite3` 或 `SQLAlchemy`（统一管理 SQLite）
  - Excel 导出（后续可选 `openpyxl` / `xlsxwriter` 等）

- **打包与安装**
  - PyInstaller：将主程序打包为可分发目录（含 PySide6 + QWebEngine 依赖）
  - Inno Setup：制作 Windows 安装向导（桌面图标 / 开始菜单 / 卸载）

---

## 三、初步目录结构规划（草案）

后续在 `WebHarvest` 目录下按类似结构进行实现（现阶段只是规划，不必完全一致）：

```text
WebHarvest/
  README.md                 # 本说明文档
  requirements.txt          # 依赖列表（后续补充）
  webharvest/
    __init__.py
    main.py                 # 应用入口（PySide6 主窗口启动）

    ui/                     # 界面相关（PySide6）
      main_window.py        # 主窗口、菜单栏、状态栏
      task_panel.py         # 任务配置界面（URL、规则、引擎选择）
      proxy_panel.py        # 代理配置界面
      schedule_panel.py     # 定时任务配置
      progress_view.py      # 进度、成功率、日志展示
      export_dialog.py      # 数据导出对话框

    core/                   # 核心业务逻辑
      task_manager.py       # 任务创建、启动、暂停、删除
      scheduler.py          # 定时任务调度
      engine_router.py      # 根据 URL / 配置选择 Requests / WebEngine 引擎

    engines/                # 采集引擎
      requests_engine.py    # 使用 requests 的静态页面采集
      qwebengine_engine.py  # 基于 QWebEngineView 的动态页面采集
      parser.py             # 封装 newspaper4k + trafilatura 的统一解析接口

    storage/                # 本地存储
      db_manager.py         # SQLite 读写（任务表 / 结果表 / 日志表）
      file_manager.py       # 图片、附件存储到本地文件夹
      exporter.py           # 结果导出为 Excel

    config/                 # 配置相关
      settings.py           # 路径、数据库位置、日志等级、代理池设置等

    utils/                  # 工具模块
      logging_utils.py      # 日志封装（文件 + UI）
      proxy_pool.py         # 代理池与自动切换策略
      retry_policies.py     # tenacity 重试策略封装
      path_manager.py       # 安装目录 / 用户数据目录 / 日志目录等路径统一管理
```

---

## 四、核心功能设计说明（概要）

### 1. 可视化操作界面

- 配置内容：
  - 采集 URL 列表
  - 采集引擎选择：Requests / QWebEngine / 自动模式
  - 代理设置：单代理 / 代理池
  - 定时任务（简单周期或 cron 类配置）
  - 提取规则（优先使用 `newspaper4k`、是否启用 `trafilatura` 兜底、是否提取图片等）
- 监控内容：
  - 每个任务的进度条
  - 成功 / 失败数量与成功率
  - 详细日志（错误原因、代理信息等）
- 数据导出：
  - 选择任务 / 时间范围
  - 导出为 Excel，支持自定义导出路径

### 2. 双引擎采集模式

- **Requests 引擎（静态页、高并发）**
  - 使用 `requests` 发起 HTTP 请求
  - 支持代理、超时配置、重试逻辑
  - 适合不需 JS 渲染的静态页面

- **QWebEngineView 引擎（动态页 / 登录站点）**
  - 使用 `QWebEngineView` 模拟浏览器加载页面，处理 JS 渲染
  - 支持人工登录后复用 Cookie / Session（适合需要登录的网站）
  - 可注入 JavaScript 提取需要的 DOM 内容
  - 页面加载成功后，再将 HTML 内容交给解析模块

### 3. 文本解析策略（newspaper4k + trafilatura）

- 默认流程：
  1. 使用 `newspaper4k` 提取标题、正文、作者、时间等信息
  2. 如提取结果失败或文本质量不足：
     - 再尝试 `trafilatura` 进行补充解析或兜底
  3. 最终返回统一结构的数据对象（标题、正文、摘要、发布时间、图片链接等）

### 4. 本地存储策略

- **SQLite 数据库（单文件）**
  - 建议表结构（后续实现时再细化）：
    - `tasks`：任务配置与状态
    - `records`：采集结果（URL、标题、正文、时间戳、所属任务等）
    - `attachments`：图片 / 附件的本地路径与关联记录

- **文件系统存储**
  - 图片与附件保存到本地文件夹：
    - 默认路径：安装目录下的 `data/` 或 用户自定义路径
    - 按日期 / 任务 ID 建子目录，避免单目录文件过多

---

## 五、路径与配置规划

- 区分两类路径：
  - **应用安装目录**：程序本体及静态资源（通常只读）
  - **用户数据目录**：SQLite、日志、图片、导出文件（可写）
- 通过统一的 `path_manager` 管理：
  - 兼容「源码运行」与「PyInstaller 打包后运行」
  - 在打包环境下识别 `sys._MEIPASS` 等特殊路径
- 用户可在 UI 中选择数据存储路径，并写入配置（SQLite 或 配置文件）。

---

## 六、重试与代理容错设计（tenacity + 代理池）

- **重试逻辑（tenacity）**
  - 典型使用场景：
    - 网络波动（连接超时 / DNS 错误）
    - HTTP 5xx 等服务端错误
  - 策略示例（后续在代码中具体实现）：
    - 限制最大重试次数（如 3~5 次）
    - 固定或指数退避延迟

- **代理自动切换（proxy_pool）**
  - 支持配置多个代理（IP:端口，附带鉴权信息）
  - 提供：
    - `get_next_proxy()`：获取下一个可用代理
    - 标记失败代理，并进行冷却或降级
  - Requests 和 QWebEngine 都需统一走此代理配置层

---

## 七、打包与安装思路（概要）

### 1. PyInstaller 打包主程序

- 确定统一入口：`webharvest/main.py`
- 打包关注点：
  - 正确包含 PySide6 和 QWebEngine 必需的：
    - 动态库
    - `qtwebengine_process.exe`
    - `resources.pak` / `icudtl.dat` 等资源文件
  - 保证打包后目录结构中，Qt 能正常找到这些资源
- 目标产物：
  - 类似 `dist/WebHarvest/` 结构的可运行程序目录（含 exe + 所有依赖）

### 2. Inno Setup 制作安装包

- 安装功能目标：
  - 安装向导（语言选择、安装路径选择）
  - 默认安装到用户目录（如 `%LOCALAPPDATA%\WebHarvest`），避免管理员权限
  - 创建桌面快捷方式 & 开始菜单项
  - 提供卸载入口
- 卸载注意：
  - 程序文件默认删除
  - 用户数据（数据库 / 采集数据）可提供「是否一并删除」选择

---

## 八、常见风险与避坑点（设计阶段提醒）

- **PySide6 + QWebEngine 体积与依赖复杂度**
  - 打包体积会偏大，这是正常现象
  - 需要多次试打包，检查缺失的 Qt 组件与资源文件

- **路径与权限**
  - 避免将可写数据放在 `C:\Program Files` 等需要管理员权限的目录
  - 优先使用用户目录 / 用户自选路径，并保证兼容中文、空格路径

- **Qt 线程限制**
  - QWebEngineView 必须在主 GUI 线程中操作
  - 高并发建议主要放在 Requests 引擎中，WebEngine 用于少量需要 JS / 登录的页面

- **后续升级兼容性**
  - Inno Setup 需固定 `AppId`，保证后续升级覆盖安装
  - 数据库结构变更时，需要考虑迁移策略

---

## 九、Git 提交和推送脚本使用说明

项目提供了便捷的 Git 操作脚本，用于提交代码和推送到远程仓库。

### 9.1 提交和推送脚本 (`commit_and_push.bat`)

**功能**：
- 自动切换到 `dev` 分支
- 检查并添加所有更改的文件
- 提交代码（需要输入提交信息）
- 推送到远程 `dev` 分支
- 详细的执行过程提示和错误诊断

**使用方法**：
```bash
# 在项目根目录下运行
.\commit_and_push.bat
```

**脚本执行流程**：
1. ✅ 检查 Git 仓库状态
2. ✅ 自动切换到 `dev` 分支（如不存在则创建）
3. ✅ 显示待提交的文件列表
4. ✅ 添加所有更改到暂存区
5. ✅ 提示输入提交信息并提交
6. ✅ 测试 SSH 连接
7. ✅ 推送到远程仓库
8. ✅ 显示推送结果和后续提示

**推送成功示例**：
```
[成功] 推送完成!
[信息] 推送详情:
e3761f5 feat: 新增功能
[提示] 你可以在Gitee上查看更新:
  https://gitee.com/fanchenn/web-harvest
```

**推送失败时的诊断信息**：
- SSH 密钥问题排查
- 权限问题检查
- 网络连接提示
- 远程仓库地址确认
- 分支问题解决方案

### 9.2 SSH 诊断脚本 (`fix_ssh_push.bat`)

**功能**：
- 诊断 SSH 连接问题
- 检查 SSH 密钥配置
- 测试 Gitee 连接
- 修复常见 SSH 问题

**使用方法**：
```bash
# 当推送遇到 SSH 问题时运行
.\fix_ssh_push.bat
```

**诊断步骤**：
1. 检查 SSH 密钥文件是否存在
2. 将密钥添加到 SSH agent
3. 检查 agent 中的密钥
4. 测试 SSH 连接到 Gitee
5. 尝试推送并显示详细错误信息

### 9.3 SSH 密钥配置

**如果遇到 SSH 认证失败**：

1. **检查公钥是否已添加到 Gitee**：
   - 访问：https://gitee.com/profile/sshkeys
   - 确认公钥已添加

2. **查看当前公钥**：
   ```bash
   type %USERPROFILE%\.ssh\id_rsa_account.pub
   ```

3. **手动测试 SSH 连接**：
   ```bash
   ssh -T git@gitee.com
   ```

4. **如果连接失败，运行诊断脚本**：
   ```bash
   .\fix_ssh_push.bat
   ```

### 9.4 手动推送命令

如果脚本无法使用，可以手动执行：

```bash
# 1. 确保在 dev 分支
git checkout dev

# 2. 添加更改
git add .

# 3. 提交
git commit -m "你的提交信息"

# 4. 推送（首次推送需要设置上游）
git push -u origin dev

# 或后续推送
git push origin dev
```

---

## 十、后续实施建议步骤

1. 在 `WebHarvest` 目录中按本说明文档，大致搭出空目录与空模块文件。
2. 先完成：基础 UI + Requests 引擎 + SQLite 存储的最小可用版本。
3. 再集成 QWebEngineView，打通动态页面采集流程。
4. 最后调试 PyInstaller 打包与 Inno Setup 安装脚本，逐步补齐依赖和路径问题。

> 本文档会作为实现过程中的「蓝图」，后续如有新需求或架构调整，可以在此基础上迭代更新。
