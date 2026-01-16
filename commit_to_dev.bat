@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM Git 提交脚本 - 提交到 dev 分支
REM 仓库地址: git@gitee.com:fanchenn/web-harvest.git (SSH)

set REPO_URL=git@gitee.com:fanchenn/web-harvest.git
set BRANCH=dev
set SCRIPT_DIR=%~dp0

cd /d "%SCRIPT_DIR%"

echo ========================================
echo Git 提交脚本 - 提交到 dev 分支
echo ========================================
echo.

REM 自动添加 Gitee SSH 主机密钥（避免首次连接时的手动确认）
set SSH_DIR=%USERPROFILE%\.ssh
set KNOWN_HOSTS=%SSH_DIR%\known_hosts
if not exist "%SSH_DIR%" mkdir "%SSH_DIR%"
if not exist "%KNOWN_HOSTS%" (
    echo. > "%KNOWN_HOSTS%"
)
findstr /C:"gitee.com" "%KNOWN_HOSTS%" >nul 2>&1
if errorlevel 1 (
    echo 添加 Gitee SSH 主机密钥到 known_hosts...
    where ssh-keyscan >nul 2>&1
    if errorlevel 1 (
        echo [WARN] 未找到 ssh-keyscan 命令，首次连接时需要手动输入 yes
    ) else (
        ssh-keyscan -t ed25519 gitee.com >> "%KNOWN_HOSTS%" 2>nul
        if errorlevel 1 (
            echo [WARN] 无法自动添加 SSH 主机密钥，首次连接时需要手动输入 yes
        ) else (
            echo [OK] SSH 主机密钥已添加
        )
    )
    echo.
)

REM 检查是否已初始化 Git 仓库
if not exist ".git" (
    echo 初始化 Git 仓库...
    git init
    if errorlevel 1 (
        echo [ERROR] Git 初始化失败
        pause
        exit /b 1
    )
    echo [OK] Git 仓库初始化完成
)

REM 检查远程仓库配置
git remote | findstr /C:"origin" >nul
if errorlevel 1 (
    echo 添加远程仓库...
    git remote add origin %REPO_URL%
    if errorlevel 1 (
        echo [ERROR] 添加远程仓库失败
        pause
        exit /b 1
    )
    echo [OK] 远程仓库已添加: %REPO_URL%
) else (
    REM 检查并更新远程仓库 URL（如果不同）
    for /f "tokens=*" %%u in ('git remote get-url origin 2^>nul') do set CURRENT_URL=%%u
    if not "!CURRENT_URL!"=="%REPO_URL%" (
        echo 更新远程仓库地址...
        git remote set-url origin %REPO_URL%
        if errorlevel 1 (
            echo [ERROR] 更新远程仓库地址失败
            pause
            exit /b 1
        )
        echo [OK] 远程仓库地址已更新: %REPO_URL%
    ) else (
        echo [OK] 远程仓库已配置: %REPO_URL%
    )
)

REM 检查当前分支
for /f "tokens=*" %%i in ('git branch --show-current 2^>nul') do set CURRENT_BRANCH=%%i
if "!CURRENT_BRANCH!"=="" (
    echo 创建 dev 分支...
    git checkout -b %BRANCH%
    if errorlevel 1 (
        echo [ERROR] 创建分支失败
        pause
        exit /b 1
    )
    echo [OK] 已创建并切换到 dev 分支
) else if not "!CURRENT_BRANCH!"=="%BRANCH%" (
    echo 当前分支: !CURRENT_BRANCH!
    echo 切换到 dev 分支...
    git checkout -b %BRANCH% 2>nul
    if errorlevel 1 (
        git checkout %BRANCH%
        if errorlevel 1 (
            echo [ERROR] 切换分支失败
            pause
            exit /b 1
        )
    )
    echo [OK] 已切换到 dev 分支
) else (
    echo [OK] 当前已在 dev 分支
)

echo.
echo 当前 Git 状态:
git status --short 2>nul

echo.

REM 检查是否有未跟踪或已修改的文件
git status --porcelain | findstr /R "." >nul 2>&1
if errorlevel 1 (
    echo [INFO] 没有需要提交的更改，工作区干净
    echo.
    REM 检查远程分支是否存在
    git ls-remote --heads origin %BRANCH% >nul 2>&1
    if errorlevel 1 (
        REM 远程分支不存在，直接推送
        echo 远程分支不存在，将创建并推送...
        echo.
        goto :push_only
    )
    REM 检查是否有未推送的提交
    git log origin/%BRANCH%..HEAD --oneline 2>nul | findstr /R "." >nul 2>&1
    if not errorlevel 1 (
        echo 检测到本地有未推送的提交，继续推送...
        echo.
        goto :push_only
    ) else (
        echo 本地和远程已同步，没有需要推送的内容
        pause
        exit /b 0
    )
)

REM 添加所有更改
echo 添加所有更改到暂存区
git add .
if errorlevel 1 (
    echo [ERROR] 添加文件失败
    pause
    exit /b 1
)
echo [OK] 文件已添加到暂存区

echo.

REM 再次检查是否有更改需要提交
git status --porcelain | findstr /R "." >nul 2>&1
if errorlevel 1 (
    echo [INFO] 添加后没有需要提交的更改
    echo.
    REM 检查远程分支是否存在
    git ls-remote --heads origin %BRANCH% >nul 2>&1
    if errorlevel 1 (
        REM 远程分支不存在，直接推送
        echo 远程分支不存在，将创建并推送...
        echo.
        goto :push_only
    )
    REM 检查是否有未推送的提交
    git log origin/%BRANCH%..HEAD --oneline 2>nul | findstr /R "." >nul 2>&1
    if not errorlevel 1 (
        echo 检测到本地有未推送的提交，继续推送...
        echo.
        goto :push_only
    ) else (
        echo 本地和远程已同步，没有需要提交和推送的内容
        pause
        exit /b 0
    )
)

REM 获取提交信息
set /p COMMIT_MESSAGE="请输入提交信息 (直接回车使用默认信息): "
if "!COMMIT_MESSAGE!"=="" (
    for /f "tokens=1-3 delims=/ " %%a in ('date /t') do set DATE_STR=%%c-%%a-%%b
    for /f "tokens=1-2 delims=: " %%a in ('time /t') do set TIME_STR=%%a:%%b
    set COMMIT_MESSAGE=Update: !DATE_STR! !TIME_STR!
)

echo.

REM 提交更改
echo 提交更改...
git commit -m "!COMMIT_MESSAGE!"
if errorlevel 1 (
    echo [WARN] 提交失败，可能是没有需要提交的更改
    REM 检查远程分支是否存在
    git ls-remote --heads origin %BRANCH% >nul 2>&1
    if errorlevel 1 (
        REM 远程分支不存在，直接推送
        echo 远程分支不存在，将创建并推送...
        echo.
        goto :push_only
    )
    REM 检查是否有未推送的提交
    git log origin/%BRANCH%..HEAD --oneline 2>nul | findstr /R "." >nul 2>&1
    if not errorlevel 1 (
        echo 检测到本地有未推送的提交，继续推送...
        echo.
        goto :push_only
    ) else (
        echo 本地和远程已同步，没有需要提交和推送的内容
        pause
        exit /b 0
    )
)
echo [OK] 提交成功

echo.

:push_only
REM 推送到远程仓库
echo 推送到远程仓库 (dev 分支)...
REM 设置 SSH 选项，自动接受新的主机密钥（如果之前没有添加成功）
set GIT_SSH_COMMAND=ssh -o StrictHostKeyChecking=accept-new
git push -u origin %BRANCH%
set GIT_SSH_COMMAND=
if errorlevel 1 (
    echo [ERROR] 推送失败，请检查网络连接和权限
    echo 提示: 如果是第一次推送，可能需要先拉取远程分支
    echo 提示: 请确保已配置 SSH 密钥并添加到 Gitee
    echo 提示: 如果遇到主机密钥确认提示，请输入 yes 并重新运行脚本
    pause
    exit /b 1
)
echo [OK] 推送成功

echo.
echo ========================================
echo [OK] 所有操作完成！
echo ========================================
pause

