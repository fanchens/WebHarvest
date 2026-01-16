@echo off
chcp 65001 >nul
echo ========================================
echo SSH连接诊断脚本
echo ========================================
echo.

echo 1. 检查SSH密钥文件...
if exist "%USERPROFILE%\.ssh\id_rsa.pub" (
    echo [√] 找到SSH公钥: %USERPROFILE%\.ssh\id_rsa.pub
    echo.
    echo 公钥内容:
    type "%USERPROFILE%\.ssh\id_rsa.pub"
    echo.
) else if exist "%USERPROFILE%\.ssh\id_ed25519.pub" (
    echo [√] 找到SSH公钥: %USERPROFILE%\.ssh\id_ed25519.pub
    echo.
    echo 公钥内容:
    type "%USERPROFILE%\.ssh\id_ed25519.pub"
    echo.
) else (
    echo [×] 未找到SSH公钥文件
    echo.
    echo 请运行以下命令生成SSH密钥:
    echo ssh-keygen -t rsa -C "your_email@example.com"
    echo.
    pause
    exit /b 1
)

echo 2. 测试Gitee SSH连接...
ssh -T git@gitee.com

if %errorlevel% equ 0 (
    echo.
    echo [√] SSH连接成功!
) else (
    echo.
    echo [×] SSH连接失败!
    echo.
    echo 可能的原因和解决方案:
    echo.
    echo 1. SSH密钥未添加到Gitee账户
    echo    解决: 访问 https://gitee.com/profile/sshkeys
    echo           添加上面显示的公钥内容
    echo.
    echo 2. SSH密钥权限问题
    echo    解决: 检查 .ssh 文件夹权限 (应该是 700)
    echo           检查私钥文件权限 (应该是 600)
    echo.
    echo 3. SSH配置问题
    echo    解决: 检查 %USERPROFILE%\.ssh\config 文件
    echo.
)

echo.
echo 3. 检查Git远程仓库配置...
cd /d "E:\PyCharm\PythonProject\WebHarvest"
if exist ".git" (
    echo 远程仓库地址:
    git remote -v
) else (
    echo [×] 当前目录不是Git仓库
)

echo.
echo ========================================
pause

