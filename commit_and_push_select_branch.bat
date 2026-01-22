@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion

echo ========================================
echo Git 提交和推送脚本 - 分支选择版
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

REM 获取当前分支
echo [信息] 检查当前分支...
git branch --show-current > temp_current_branch.txt 2>nul
if exist temp_current_branch.txt (
    set /p currentBranch=<temp_current_branch.txt
    del temp_current_branch.txt 2>nul
) else (
    set currentBranch=
)

REM 获取默认分支
echo [信息] 检测默认分支...
git symbolic-ref refs/remotes/origin/HEAD > temp_default_branch.txt 2>nul
if exist temp_default_branch.txt (
    set /p defaultBranchRef=<temp_default_branch.txt
    del temp_default_branch.txt 2>nul
    for /f "tokens=4 delims=/" %%a in ("!defaultBranchRef!") do set defaultBranch=%%a
) else (
    git ls-remote --symref origin HEAD > temp_default_branch2.txt 2>nul
    if exist temp_default_branch2.txt (
        findstr /C:"refs/heads/" temp_default_branch2.txt > temp_default_branch3.txt 2>nul
        if exist temp_default_branch3.txt (
            for /f "tokens=2 delims=/ " %%a in (temp_default_branch3.txt) do (
                for /f "tokens=3 delims=/" %%b in ("%%a") do set defaultBranch=%%b
            )
        )
        del temp_default_branch2.txt 2>nul
        del temp_default_branch3.txt 2>nul
    )
    if not defined defaultBranch (
        set defaultBranch=master
    )
)

REM 列出所有分支
echo.
echo ========================================
echo 可用分支列表
echo ========================================
echo.
echo [当前分支] !currentBranch!
if defined defaultBranch (
    echo [默认分支] !defaultBranch!
)
echo.
echo 本地分支:
git branch 2>nul
echo.
echo 远程分支:
git branch -r 2>nul | findstr /V "HEAD"
echo.
echo ========================================
echo.

REM 显示分支说明
echo 分支说明:
echo   master - 主分支/生产环境
echo   dev    - 开发环境
echo   test   - 测试环境
echo   prod   - 生产环境
echo.

REM 让用户选择目标分支
:select_branch
set /p targetBranch="请选择目标分支 (master/dev/test/prod) [默认: !currentBranch!]: "
if "!targetBranch!"=="" (
    set targetBranch=!currentBranch!
)
if "!targetBranch!"=="" (
    echo [错误] 无法确定目标分支!
    pause
    exit /b 1
)

REM 验证分支是否存在
git branch --list !targetBranch! > temp_check_branch.txt 2>nul
git branch -r --list origin/!targetBranch! >> temp_check_branch.txt 2>nul
if exist temp_check_branch.txt (
    set /p branchExists=<temp_check_branch.txt
    del temp_check_branch.txt 2>nul
) else (
    set branchExists=
)

if "!branchExists!"=="" (
    echo.
    echo [警告] 分支 "!targetBranch!" 不存在!
    echo [提示] 是否创建新分支 "!targetBranch!"? (y/n)
    set /p createBranch=
    if /i "!createBranch!"=="y" (
        echo [信息] 正在创建分支 "!targetBranch!"...
        git checkout -b !targetBranch! 2>nul
        if !errorlevel! neq 0 (
            echo [错误] 创建分支失败!
            pause
            exit /b 1
        )
        echo [成功] 已创建并切换到分支 "!targetBranch!"
    ) else (
        echo [提示] 已取消，请重新选择分支
        echo.
        goto :select_branch
    )
) else (
    REM 切换到目标分支
    if not "!currentBranch!"=="!targetBranch!" (
        echo [信息] 当前分支: !currentBranch!
        echo [信息] 正在切换到分支: !targetBranch!
        git checkout !targetBranch! 2>nul
        if !errorlevel! neq 0 (
            echo [错误] 切换分支失败!
            pause
            exit /b 1
        )
        echo [成功] 已切换到分支 "!targetBranch!"
        set currentBranch=!targetBranch!
    ) else (
        echo [信息] 当前已在分支 "!targetBranch!"
    )
)
echo.

REM 显示git状态
echo [信息] 检查git状态...
echo ----------------------------------------
git status --short 2>nul
echo ----------------------------------------
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
echo [信息] 检测到以下更改
git status --short
echo.

REM 添加所有更改
echo [信息] 正在添加更改的文件...
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
echo [信息] 正在提交更改到分支 "!targetBranch!"...
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
echo [信息] 目标分支: !targetBranch!
echo [信息] 远程仓库信息:
git remote -v 2>nul
echo.

set /p push="是否推送到远程分支 origin/!targetBranch!? (y/n): "
if /i not "!push!"=="y" (
    echo.
    echo [提示] 已取消推送
    echo [提示] 你可以稍后使用以下命令手动推送:
    echo   git push origin !targetBranch!
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
echo [信息] 正在推送代码到远程分支 origin/!targetBranch!...
echo ----------------------------------------

if exist "!SSH_KEY!" (
    REM 使用SSH密钥文件推送（正确处理中文路径）
    powershell -NoProfile -Command "$sshKeyPath = Join-Path $env:USERPROFILE '.ssh\id_rsa_account'; $sshKey = (Resolve-Path $sshKeyPath).Path; $env:GIT_SSH_COMMAND = \"ssh -i `\"$sshKey`\"\"; cd 'E:\PyCharm\PythonProject\WebHarvest'; $branch = '!targetBranch!'; Write-Host \"[执行] git push origin $branch\" -ForegroundColor Yellow; git push origin $branch; $exitCode = $LASTEXITCODE; $env:GIT_SSH_COMMAND = $null; exit $exitCode"
) else (
    REM 使用默认SSH配置推送
    echo [信息] 使用默认SSH配置推送...
    git push origin !targetBranch!
)

set PUSH_RESULT=!errorlevel!

echo ----------------------------------------

if !PUSH_RESULT! equ 0 (
    echo.
    echo ========================================
    echo [成功] 推送完成!
    echo ========================================
    echo.
    echo [信息] 推送详情:
    echo   分支: !targetBranch!
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
    echo    - 检查仓库访问权限设置
    echo.
    echo 3. 网络问题:
    echo    - 检查网络连接是否正常
    echo    - 如需要可尝试使用VPN或代理
    echo.
    echo 4. 远程仓库地址:
    echo    - 当前远程地址:
    git remote -v 2>nul
    echo.
    echo 5. 分支问题:
    echo    - 确认远程分支存在或使用首次推送: git push -u origin !targetBranch!
    echo.
    echo [提示] 你可以稍后重试推送:
    echo   git push origin !targetBranch!
    echo.
)

pause
