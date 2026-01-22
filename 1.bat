@echo off
:: 切换到GBK编码（适配ANSI脚本的中文显示）
chcp 936 >nul 2>&1
setlocal enabledelayedexpansion

echo ========================================
echo Git 推送脚本 - 当前分支推目标分支版
echo ========================================
echo.

:: 获取当前所在分支
echo [信息] 检测当前分支...
git branch --show-current > temp_branch.txt 2>nul
if exist temp_branch.txt (
    set /p currentBranch=<temp_branch.txt
    del temp_branch.txt 2>nul
) else (
    echo [错误] 无法获取当前分支！
    pause
    exit /b 1
)
echo [信息] 当前分支：!currentBranch!
echo.

REM ===================== 输入要推送的目标分支 =====================
echo [信息] 请输入要推送的目标分支名称（例如：test、dev、prod、main）
echo ----------------------------------------
set /p targetBranch=目标分支名: 
echo ----------------------------------------
if "!targetBranch!"=="" (
    echo [错误] 分支名称不能为空！
    pause
    exit /b 1
)
if "!currentBranch!"=="!targetBranch!" (
    echo [提示] 当前分支和目标分支相同，将直接推送当前分支到远程！
    echo.
)
REM =============================================================

:: 切换到项目目录
cd /d "E:\PyCharm\PythonProject\WebHarvest" 2>nul
if !errorlevel! neq 0 (
    echo [错误] 无法切换到项目目录！
    pause
    exit /b 1
)

:: 检查是否是Git仓库
if not exist ".git" (
    echo [错误] 当前目录不是Git仓库！
    pause
    exit /b 1
)

:: 显示Git状态
echo [信息] 检查当前分支（!currentBranch!）的更改...
echo ----------------------------------------
git status --short 2>nul
echo ----------------------------------------
echo.

:: 检查未提交的更改
echo [信息] 检查未提交的更改...
git status --porcelain > temp_status.txt 2>nul
set "hasChanges="
for /f "delims=" %%a in (temp_status.txt) do set hasChanges=1
del temp_status.txt 2>nul

if not defined hasChanges (
    echo [信息] 当前分支没有未提交的更改，跳过提交步骤
    echo.
    goto :push_section
)

:: 显示变更文件
echo [信息] 检测到以下更改：
git status --short
echo.

:: 添加所有更改到暂存区
echo [信息] 正在添加变更文件到暂存区...
git add . 2>nul
if !errorlevel! neq 0 (
    echo [错误] 添加文件到暂存区失败！
    pause
    exit /b 1
)
echo [成功] 所有变更文件已添加到暂存区
echo.

:: 获取提交信息
echo [信息] 请输入提交信息
echo ----------------------------------------
set /p commitMessage=提交信息: 
echo ----------------------------------------
if "!commitMessage!"=="" (
    echo [错误] 提交信息不能为空！
    pause
    exit /b 1
)
echo.

:: 提交当前分支的更改
echo [信息] 正在提交当前分支（!currentBranch!）的更改...
echo [信息] 提交信息: !commitMessage!
git commit -m "!commitMessage!" 2>nul

if !errorlevel! neq 0 (
    echo [错误] 提交失败！
    pause
    exit /b 1
)

echo [成功] 提交成功！
echo.

:push_section
:: 推送到远程目标分支
echo ========================================
echo 推送当前分支（!currentBranch!）到远程 !targetBranch! 分支
echo ========================================
echo.
echo [警告] 此操作会将当前分支（!currentBranch!）的代码推送到远程 !targetBranch! 分支！
echo [信息] 远程仓库信息：
git remote -v 2>nul
echo.

set /p push=确认推送? (y/n): 
if /i not "!push!"=="y" (
    echo.
    echo [信息] 已取消推送
    echo.
    pause
    exit /b 0
)

echo.
echo [信息] 正在准备SSH连接...
echo ----------------------------------------

:: 添加SSH密钥到agent
set "SSH_KEY=%USERPROFILE%\.ssh\id_rsa_account"
if exist "!SSH_KEY!" (
    echo [信息] 找到SSH密钥：!SSH_KEY!
    echo [信息] 正在将密钥添加到SSH agent...
    ssh-add "!SSH_KEY!" 2>nul
    if !errorlevel! equ 0 (
        echo [成功] SSH密钥已添加到agent
    ) else (
        echo [提示] 添加密钥到agent失败，将直接使用密钥文件
    )
    
    echo.
    echo [信息] 测试SSH连接...
    ssh -T git@gitee.com > temp_ssh_test.txt 2>&1
    findstr /C:"Hi " temp_ssh_test.txt >nul
    if !errorlevel! equ 0 (
        echo [成功] SSH连接正常
        type temp_ssh_test.txt | findstr /C:"Hi "
    ) else (
        echo [提示] SSH连接测试未通过，将继续尝试推送
    )
    del temp_ssh_test.txt 2>nul
) else (
    echo [提示] 未找到SSH密钥文件，将使用默认SSH配置
)
echo ----------------------------------------
echo.

:: 核心推送命令
echo [信息] 正在推送 !currentBranch! 分支到远程 !targetBranch! 分支...
echo [信息] 目标：origin/!targetBranch!
echo ----------------------------------------

if exist "!SSH_KEY!" (
    powershell -NoProfile -Command "$sshKey = [System.IO.Path]::GetFullPath('%SSH_KEY%'); $env:GIT_SSH_COMMAND = 'ssh -i ''$sshKey'''; Set-Location 'E:\PyCharm\PythonProject\WebHarvest'; git push -u origin !currentBranch!:!targetBranch!; exit $LASTEXITCODE"
) else (
    git push -u origin !currentBranch!:!targetBranch!
)

set PUSH_RESULT=!errorlevel!

echo ----------------------------------------

if !PUSH_RESULT! equ 0 (
    echo.
    echo ========================================
    echo [成功] 已将 !currentBranch! 分支推送到远程 !targetBranch! 分支！
    echo ========================================
    echo.
    echo [信息] 最新提交记录：
    git log --oneline -1 2>nul
    echo.
    echo [信息] 查看地址：https://gitee.com/fanchenn/web-harvest/tree/!targetBranch!
    echo.
) else (
    echo.
    echo ========================================
    echo [错误] 推送 !currentBranch! 到 !targetBranch! 分支失败！
    echo ========================================
    echo.
    echo [排查建议]
    echo 1. SSH密钥问题：执行命令 'ssh -T git@gitee.com'
    echo 2. 检查目标分支权限：确认有权限推送至 !targetBranch! 分支
    echo 3. 手动推送命令：'git push -u origin !currentBranch!:!targetBranch!'
    echo.
)

pause