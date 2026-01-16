@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion

echo ========================================
echo Git 提交和推送脚本 - dev分支
echo ========================================
echo.

REM 切换到项目目录
cd /d "E:\PyCharm\PythonProject\WebHarvest" 2>nul
if !errorlevel! neq 0 (
    echo [错误] 无法切换到项目目录!
    pause
    exit /b 1
)

REM 检查是否是git仓库
if not exist ".git" (
    echo [错误] 当前目录不是git仓库!
    pause
    exit /b 1
)

REM 显示git状态
echo [信息] 检查git状态...
echo ----------------------------------------
git status --short 2>nul
echo ----------------------------------------
echo.

REM 切换到dev分支
echo [信息] 检查当前分支...
git branch --show-current > temp_branch.txt 2>nul
if exist temp_branch.txt (
    set /p currentBranch=<temp_branch.txt
    del temp_branch.txt 2>nul
) else (
    set currentBranch=
)

if not "!currentBranch!"=="dev" (
    echo [信息] 当前分支: !currentBranch!
    echo [信息] 正在切换到dev分支...
    git branch -a 2>nul | findstr /C:"dev" >nul
    if !errorlevel! equ 0 (
        git checkout dev 2>nul
        echo [成功] 已切换到dev分支
    ) else (
        echo [信息] dev分支不存在，正在创建dev分支...
        git checkout -b dev 2>nul
        echo [成功] 已创建并切换到dev分支
    )
) else (
    echo [信息] 当前已在dev分支
)
echo.

REM 检查是否有未提交的更改
echo [信息] 检查未提交的更改...
git status --porcelain > temp_status.txt 2>nul
if exist temp_status.txt (
    set /p hasChanges=<temp_status.txt
    del temp_status.txt 2>nul
) else (
    set hasChanges=
)

if "!hasChanges!"=="" (
    echo [提示] 没有需要提交的更改，跳过提交步骤
    echo.
    goto :push_section
)

REM 显示更改的文件
echo [信息] 检测到以下更改:
git status --short
echo.

REM 添加所有更改
echo [信息] 正在添加所有更改的文件...
git add . 2>nul
if !errorlevel! neq 0 (
    echo [错误] 添加文件失败!
    pause
    exit /b 1
)
echo [成功] 文件已添加到暂存区
echo.

REM 获取提交信息
echo [提示] 请输入提交信息
echo ----------------------------------------
set /p commitMessage="提交信息: "
echo ----------------------------------------
if "!commitMessage!"=="" (
    echo [错误] 提交信息不能为空!
    pause
    exit /b 1
)
echo.

REM 提交更改
echo [信息] 正在提交更改...
echo [信息] 提交信息: !commitMessage!
git commit -m "!commitMessage!" 2>nul

if !errorlevel! neq 0 (
    echo [错误] 提交失败!
    pause
    exit /b 1
)

echo [成功] 提交成功!
echo.

:push_section
REM 推送到远程
echo ========================================
echo 推送到远程仓库
echo ========================================
echo.
echo [信息] 远程仓库信息:
git remote -v 2>nul
echo.

set /p push="是否推送到远程dev分支? (y/n): "
if /i not "!push!"=="y" (
    echo.
    echo [提示] 已取消推送
    echo [提示] 你可以稍后使用以下命令手动推送:
    echo   git push origin dev
    echo.
    pause
    exit /b 0
)

echo.
echo [信息] 正在准备SSH连接...
echo ----------------------------------------

REM 确保SSH密钥已添加到agent
set "SSH_KEY=%USERPROFILE%\.ssh\id_rsa_account"
if exist "!SSH_KEY!" (
    echo [信息] 找到SSH密钥: !SSH_KEY!
    echo [信息] 正在将密钥添加到SSH agent...
    ssh-add "!SSH_KEY!" 2>nul
    if !errorlevel! equ 0 (
        echo [成功] SSH密钥已添加到agent
    ) else (
        echo [警告] 添加密钥到agent失败，将尝试直接使用密钥文件
    )
    
    echo.
    echo [信息] 正在测试SSH连接...
    ssh -T git@gitee.com > temp_ssh_test.txt 2>&1
    findstr /C:"Hi " temp_ssh_test.txt >nul
    if !errorlevel! equ 0 (
        echo [成功] SSH连接正常
        type temp_ssh_test.txt | findstr /C:"Hi "
    ) else (
        findstr /C:"successfully authenticated" temp_ssh_test.txt >nul
        if !errorlevel! equ 0 (
            echo [成功] SSH连接正常
        ) else (
            echo [警告] SSH连接测试未通过，但将继续尝试推送
            type temp_ssh_test.txt
        )
    )
    del temp_ssh_test.txt 2>nul
) else (
    echo [警告] 未找到SSH密钥文件，将使用默认SSH配置
)
echo ----------------------------------------
echo.

REM 执行推送
echo [信息] 正在推送到远程dev分支...
echo [信息] 目标: origin/dev
echo ----------------------------------------

powershell -NoProfile -Command "$sshKey = (Resolve-Path '%SSH_KEY%').Path; if (Test-Path '$sshKey') { ssh-add '$sshKey' 2>&1 | Out-Null; $env:GIT_SSH_COMMAND = \"ssh -i `\"$sshKey`\"\"; } cd 'E:\PyCharm\PythonProject\WebHarvest'; Write-Host '[执行] git push origin dev' -ForegroundColor Yellow; git push origin dev; $exitCode = $LASTEXITCODE; $env:GIT_SSH_COMMAND = $null; exit $exitCode"

set PUSH_RESULT=!errorlevel!

echo ----------------------------------------

if !PUSH_RESULT! equ 0 (
    echo.
    echo ========================================
    echo [成功] 推送完成!
    echo ========================================
    echo.
    echo [信息] 推送详情:
    git log --oneline -1 2>nul
    echo.
    echo [提示] 你可以在Gitee上查看更新:
    echo   https://gitee.com/fanchenn/web-harvest
    echo.
) else (
    echo.
    echo ========================================
    echo [错误] 推送失败!
    echo ========================================
    echo.
    echo [提示] 常见问题排查:
    echo.
    echo 1. SSH密钥问题:
    echo    - 运行: ssh -T git@gitee.com
    echo    - 检查: https://gitee.com/profile/sshkeys
    echo.
    echo 2. 权限问题:
    echo    - 确认你有该仓库的推送权限
    echo    - 检查仓库是否为私有且你有访问权限
    echo.
    echo 3. 网络问题:
    echo    - 检查网络连接
    echo    - 尝试使用VPN或代理
    echo.
    echo 4. 远程仓库地址:
    echo    - 当前远程地址:
    git remote -v 2>nul
    echo.
    echo 5. 分支问题:
    echo    - 确认远程dev分支存在
    echo    - 或使用: git push -u origin dev (首次推送)
    echo.
    echo [提示] 你可以稍后重试推送:
    echo   git push origin dev
    echo.
)

pause

