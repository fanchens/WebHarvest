@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo SSH Account Key Setup Script
echo ========================================
echo.
echo This script will help you set up an SSH key for your Gitee account
echo (different from DeployKey which only supports pull operations)
echo.

REM 检查是否已存在账户密钥
if exist "%USERPROFILE%\.ssh\id_rsa_account" (
    echo [WARNING] Account SSH key already exists: id_rsa_account
    echo.
    set /p overwrite="Overwrite existing key? (y/n): "
    if /i not "!overwrite!"=="y" (
        echo Cancelled.
        pause
        exit /b 0
    )
)

echo.
echo Step 1: Generating SSH key for account...
echo.
ssh-keygen -t rsa -C "2932926493@qq.com" -f "%USERPROFILE%\.ssh\id_rsa_account" -N ""

if !errorlevel! neq 0 (
    echo Failed to generate SSH key!
    pause
    exit /b 1
)

echo.
echo [√] SSH key generated successfully!
echo.

REM 显示公钥内容
echo ========================================
echo Your public key (copy this to Gitee):
echo ========================================
type "%USERPROFILE%\.ssh\id_rsa_account.pub"
echo.
echo ========================================
echo.

REM 配置SSH config
echo Step 2: Configuring SSH config...
if not exist "%USERPROFILE%\.ssh\config" (
    echo Creating SSH config file...
    (
        echo Host gitee.com
        echo     HostName gitee.com
        echo     User git
        echo     IdentityFile ~/.ssh/id_rsa_account
        echo     PreferredAuthentications publickey
    ) > "%USERPROFILE%\.ssh\config"
    echo [√] SSH config file created!
) else (
    echo SSH config file already exists.
    findstr /C:"Host gitee.com" "%USERPROFILE%\.ssh\config" >nul
    if !errorlevel! equ 0 (
        echo [WARNING] Gitee.com host already configured in SSH config.
        echo Please manually edit %USERPROFILE%\.ssh\config
        echo Add or update the following:
        echo.
        echo Host gitee.com
        echo     HostName gitee.com
        echo     User git
        echo     IdentityFile ~/.ssh/id_rsa_account
        echo     PreferredAuthentications publickey
        echo.
    ) else (
        echo Adding Gitee configuration to SSH config...
        (
            echo.
            echo Host gitee.com
            echo     HostName gitee.com
            echo     User git
            echo     IdentityFile ~/.ssh/id_rsa_account
            echo     PreferredAuthentications publickey
        ) >> "%USERPROFILE%\.ssh\config"
        echo [√] SSH config updated!
    )
)

echo.
echo ========================================
echo Next Steps:
echo ========================================
echo.
echo 1. Copy the public key shown above
echo.
echo 2. Go to Gitee and add the SSH key:
echo    https://gitee.com/profile/sshkeys
echo.
echo 3. Click "Add SSH Key" and paste the public key
echo.
echo 4. Test the connection:
echo    ssh -T git@gitee.com
echo.
echo    You should see: Hi fanchen(@fanchenn)! ...
echo    (NOT "Anonymous (DeployKey)")
echo.
echo ========================================
pause

