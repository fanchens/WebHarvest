@echo off
:: 切换UTF-8编码，避免中文乱码
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion

echo ========================================
echo Git 提交和推送脚本 - 自定义分支版
echo ========================================
echo.

REM ===================== 手动输入目标分支 =====================
echo [信息] 请输入要操作的目标分支名称（例如：test、dev、prod、main）
echo ----------------------------------------
set /p targetBranch="目标分支名: "
echo ----------------------------------------
if "!targetBranch!"=="" (
    echo [错误] 分支名称不能为空！
    pause
    exit /b 1
)
echo.
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
echo [信息] 检查Git工作区状态...
echo ----------------------------------------
git status --short 2>nul
echo ----------------------------------------
echo.

:: 切换到目标分支
echo [信息] 检查当前分支...
git branch --show-current > temp_branch.txt 2>nul
if exist temp_branch.txt (
    set /p currentBranch=<temp_branch.txt
    del temp_branch.txt 2>nul
) else (
    set currentBranch=
)

if not "!currentBranch!"=="!targetBranch!" (
    echo [信息] 当前分支: !currentBranch!
    echo [信息] 正在切换到 !targetBranch! 分支...
    git branch -a 2>nul | findstr /C:"!targetBranch!" >nul
    if !errorlevel! equ 0 (
        git checkout !targetBranch! 2>nul
        echo [成功] 已切换到 !targetBranch! 分支
    ) else (
        echo [信息] !targetBranch! 分支不存在，基于dev分支创建...
        git checkout dev 2>nul
        git pull origin dev 2>nul
        git checkout -b !targetBranch! 2>nul
        echo [成功] 已创建并切换到 !targetBranch! 分支
    )
) else (
    echo [信息] 已处于 !targetBranch! 分支
)
echo.

:: 拉取远程目标分支最新代码
echo [信息] 拉取远程 !targetBranch! 分支最新代码...
git pull origin !targetBranch! 2>nul
if !errorlevel! equ 0 (
    echo [成功] 已拉取远程 !targetBranch! 分支最新代码
) else (
    echo [提示] 远程 !targetBranch! 分支不存在（首次推送）
)
echo.

:: 检查未提交的更改
echo [信息] 检查未提交的更改...
git status --porcelain > temp_status.txt 2>nul
set "hasChanges="
for /f "delims=" %%a in (temp_status.txt) do set hasChanges=1
del temp_status.txt 2>nul

if not defined hasChanges (
    echo [信息] 没有未提交的更改，跳过提交步骤
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
set /p commitMessage="提交信息: "
echo ----------------------------------------
if "!commitMessage!"=="" (
    echo [错误] 提交信息不能为空！
    pause
    exit /b 1
)
echo.

:: 提交更改
echo [信息] 正在提交更改...
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
echo 推送到远程仓库 - !targetBranch! 分支
echo ========================================
echo.
echo [信息] 远程仓库信息：
git remote -v 2>nul
echo.

set /p push="是否推送到远程 !targetBranch! 分支? (y/n): "
if /i not "!push!"=="y" (
    echo.
    echo [信息] 已取消推送
    echo [信息] 手动推送命令：git push origin !targetBranch!
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

:: 执行推送（首次推送自动加-u）
echo [信息] 正在推送代码到远程 !targetBranch! 分支...
echo [信息] 目标：origin/!targetBranch!
echo ----------------------------------------

if exist "!SSH_KEY!" (
    :: 兼容中文路径的PowerShell命令
    powershell -NoProfile -Command "$sshKey = [System.IO.Path]::GetFullPath('%SSH_KEY%'); $env:GIT_SSH_COMMAND = 'ssh -i ''$sshKey'''; Set-Location 'E:\PyCharm\PythonProject\WebHarvest'; git push -u origin !targetBranch!; exit $LASTEXITCODE"
) else (
    git push -u origin !targetBranch!
)

set PUSH_RESULT=!errorlevel!

echo ----------------------------------------

if !PUSH_RESULT! equ 0 (
    echo.
    echo ========================================
    echo [成功] !targetBranch! 分支推送完成！
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
    echo [错误] !targetBranch! 分支推送失败！
    echo ========================================
    echo.
    echo [排查建议]
    echo 1. SSH密钥问题：执行命令 'ssh -T git@gitee.com'
    echo 2. 拉取远程更新：执行命令 'git pull origin !targetBranch!'
    echo 3. 手动推送命令：'git push -u origin !targetBranch!'
    echo.
)

pause