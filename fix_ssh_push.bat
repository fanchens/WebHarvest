@echo off
chcp 65001 >nul 2>&1
echo ========================================
echo SSH推送问题诊断和修复脚本
echo ========================================
echo.

REM 切换到项目目录
cd /d "E:\PyCharm\PythonProject\WebHarvest" 2>nul
if errorlevel 1 (
    echo 错误: 无法切换到项目目录!
    pause
    exit /b 1
)

echo [1/5] 检查SSH密钥文件...
set "SSH_KEY=%USERPROFILE%\.ssh\id_rsa_account"
if exist "%SSH_KEY%" (
    echo ✓ SSH密钥文件存在: %SSH_KEY%
) else (
    echo ✗ SSH密钥文件不存在: %SSH_KEY%
    echo.
    echo 请先生成SSH密钥:
    echo   ssh-keygen -t rsa -C "your_email@example.com" -f "%SSH_KEY%"
    pause
    exit /b 1
)

echo.
echo [2/5] 将SSH密钥添加到agent...
ssh-add "%SSH_KEY%" 2>nul
if errorlevel 1 (
    echo ✗ 添加密钥到agent失败
) else (
    echo ✓ 密钥已添加到agent
)

echo.
echo [3/5] 检查agent中的密钥...
ssh-add -l
if errorlevel 1 (
    echo ✗ agent中没有密钥
) else (
    echo ✓ agent中有密钥
)

echo.
echo [4/5] 测试SSH连接...
ssh -T git@gitee.com > temp_ssh_output.txt 2>&1
findstr /C:"successfully authenticated" temp_ssh_output.txt >nul
if errorlevel 1 (
    findstr /C:"Hi " temp_ssh_output.txt >nul
    if errorlevel 1 (
        echo ✗ SSH连接失败
        echo.
        echo SSH测试输出:
        type temp_ssh_output.txt
        echo.
        echo 可能的原因:
        echo 1. 公钥未添加到Gitee账户
        echo 2. 公钥已过期或被删除
        echo.
        echo 请检查:
        echo - 访问 https://gitee.com/profile/sshkeys
        echo - 确认公钥已添加
        echo.
        echo 当前公钥内容:
        if exist "%SSH_KEY%.pub" (
            type "%SSH_KEY%.pub"
        )
    ) else (
        echo ✓ SSH连接成功（检测到Gitee欢迎消息）
        type temp_ssh_output.txt
    )
) else (
    echo ✓ SSH连接成功
    type temp_ssh_output.txt
)
del temp_ssh_output.txt 2>nul

echo.
echo [5/5] 尝试推送...
echo.
set /p confirm="是否尝试推送到远程dev分支? (y/n): "
if /i "%confirm%"=="y" (
    echo.
    echo 正在推送...
    powershell -NoProfile -Command "$sshKey = (Resolve-Path '%SSH_KEY%').Path; ssh-add '$sshKey' 2>&1 | Out-Null; $env:GIT_SSH_COMMAND = \"ssh -i `\"$sshKey`\"\"; cd 'E:\PyCharm\PythonProject\WebHarvest'; git push origin dev; $exitCode = $LASTEXITCODE; $env:GIT_SSH_COMMAND = $null; exit $exitCode"
    if errorlevel 1 (
        echo.
        echo ✗ 推送失败
        echo.
        echo 解决方案:
        echo 1. 确认公钥已添加到Gitee: https://gitee.com/profile/sshkeys
        echo 2. 检查仓库权限: 确认你有推送权限
        echo 3. 检查远程仓库地址: git remote -v
    ) else (
        echo.
        echo ✓ 推送成功!
    )
) else (
    echo 已取消推送
)

echo.
pause

