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
git status --short

echo.

REM 添加所有更改
echo 添加所有更改到暂存区...
git add .
if errorlevel 1 (
    echo [ERROR] 添加文件失败
    pause
    exit /b 1
)
echo [OK] 文件已添加到暂存区

echo.

REM 检查是否有更改需要提交
git status --porcelain >nul
if errorlevel 1 (
    echo 没有需要提交的更改
    pause
    exit /b 0
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
    echo [ERROR] 提交失败
    pause
    exit /b 1
)
echo [OK] 提交成功

echo.

REM 推送到远程仓库
echo 推送到远程仓库 (dev 分支)...
git push -u origin %BRANCH%
if errorlevel 1 (
    echo [ERROR] 推送失败，请检查网络连接和权限
    echo 提示: 如果是第一次推送，可能需要先拉取远程分支
    echo 提示: 请确保已配置 SSH 密钥并添加到 Gitee
    pause
    exit /b 1
)
echo [OK] 推送成功

echo.
echo ========================================
echo [OK] 所有操作完成！
echo ========================================
pause

