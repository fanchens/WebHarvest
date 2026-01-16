@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo Git提交脚本 - dev分支
echo ========================================
echo.

REM 切换到项目目录
cd /d "E:\PyCharm\PythonProject\WebHarvest"

REM 检查是否在git仓库中
if not exist ".git" (
    echo 错误: 当前目录不是git仓库!
    pause
    exit /b 1
)

REM 检查git状态
echo Checking git status...
git status --short

REM 切换到dev分支
echo.
echo 切换到dev分支...
git branch --show-current > temp_branch.txt
set /p currentBranch=<temp_branch.txt
del temp_branch.txt

if not "!currentBranch!"=="dev" (
    git branch -a | findstr /C:"dev" >nul
    if !errorlevel! equ 0 (
        git checkout dev
    ) else (
        echo dev分支不存在，创建dev分支...
        git checkout -b dev
    )
) else (
    echo 当前已在dev分支
)

REM 检查是否有未提交的更改
echo.
echo Checking for uncommitted changes...
git status --porcelain > temp_status.txt
set /p hasChanges=<temp_status.txt
del temp_status.txt

if "!hasChanges!"=="" (
    echo No changes to commit, working tree is clean.
    echo.
    pause
    exit /b 0
)

REM 添加所有更改
echo.
echo Adding all changed files...
git add .

REM 获取提交信息
echo.
set /p commitMessage="Enter commit message: "
if "!commitMessage!"=="" (
    echo Error: Commit message cannot be empty!
    pause
    exit /b 1
)

REM 提交更改
echo.
echo Committing changes...
git commit -m "!commitMessage!"

if !errorlevel! neq 0 (
    echo Commit failed!
    pause
    exit /b 1
)

echo Commit successful!

REM 推送到远程
echo.
set /p push="Push to remote dev branch? (y/n): "
if /i "!push!"=="y" (
    echo.
    echo Testing SSH connection...
    ssh -T git@gitee.com > temp_ssh_test.txt 2>&1
    findstr /C:"DeployKey" temp_ssh_test.txt >nul
    if !errorlevel! equ 0 (
        echo.
        echo [WARNING] Current SSH key is a DeployKey!
        echo DeployKey only supports pull/fetch operations, cannot push.
        echo.
        echo Solution:
        echo 1. Generate a new SSH key for your account:
        echo    ssh-keygen -t rsa -C "your_email@example.com" -f "%USERPROFILE%\.ssh\id_rsa_account"
        echo.
        echo 2. Add the new public key to Gitee account SSH keys:
        echo    https://gitee.com/profile/sshkeys
        echo    Copy content from: %USERPROFILE%\.ssh\id_rsa_account.pub
        echo.
        echo 3. Configure SSH to use the account key for Gitee:
        echo    Edit %USERPROFILE%\.ssh\config and add:
        echo    Host gitee.com
        echo        HostName gitee.com
        echo        User git
        echo        IdentityFile ~/.ssh/id_rsa_account
        echo.
        type temp_ssh_test.txt
        del temp_ssh_test.txt
        echo.
        set /p continue="Continue to try push anyway? (y/n): "
        if /i not "!continue!"=="y" (
            echo Push cancelled.
            pause
            exit /b 0
        )
    ) else (
        del temp_ssh_test.txt
        echo SSH connection OK
    )
    
    echo.
    echo Pushing to remote dev branch...
    git push origin dev
    
    if !errorlevel! equ 0 (
        echo.
        echo ========================================
        echo Commit and push successful!
        echo ========================================
    ) else (
        echo.
        echo ========================================
        echo Push failed!
        echo ========================================
        echo.
        echo Troubleshooting:
        echo 1. SSH key issue: Run ssh -T git@gitee.com to test
        echo 2. Permission issue: Confirm you have push permission
        echo 3. Network issue: Check network connection
        echo 4. Repository URL: Confirm remote repository URL is correct
        echo.
        echo Current remote repository URL:
        git remote -v
        echo.
        pause
        exit /b 1
    )
) else (
    echo.
    echo ========================================
    echo Commit successful! (not pushed)
    echo ========================================
)

pause

