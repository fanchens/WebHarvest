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
echo 检查git状态...
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

REM 添加所有更改
echo.
echo 添加所有更改的文件...
git add .

REM 获取提交信息
echo.
set /p commitMessage="请输入提交信息: "
if "!commitMessage!"=="" (
    echo 错误: 提交信息不能为空!
    pause
    exit /b 1
)

REM 提交更改
echo.
echo 提交更改...
git commit -m "!commitMessage!"

if !errorlevel! neq 0 (
    echo 提交失败!
    pause
    exit /b 1
)

echo 提交成功!

REM 推送到远程
echo.
set /p push="是否推送到远程dev分支? (y/n): "
if /i "!push!"=="y" (
    echo.
    echo 测试SSH连接...
    ssh -T git@gitee.com >nul 2>&1
    if !errorlevel! neq 0 (
        echo.
        echo [警告] SSH连接测试失败!
        echo 可能的原因:
        echo 1. SSH密钥未配置或未添加到Gitee账户
        echo 2. SSH密钥权限问题
        echo.
        echo 解决方案:
        echo 1. 检查SSH密钥: ssh-keygen -l -f ~/.ssh/id_rsa.pub
        echo 2. 将公钥添加到Gitee: https://gitee.com/profile/sshkeys
        echo 3. 测试连接: ssh -T git@gitee.com
        echo.
        set /p continue="是否继续尝试推送? (y/n): "
        if /i not "!continue!"=="y" (
            echo 已取消推送
            pause
            exit /b 0
        )
    ) else (
        echo SSH连接正常
    )
    
    echo.
    echo 推送到远程dev分支...
    git push origin dev
    
    if !errorlevel! equ 0 (
        echo.
        echo ========================================
        echo 提交并推送成功!
        echo ========================================
    ) else (
        echo.
        echo ========================================
        echo 推送失败!
        echo ========================================
        echo.
        echo 常见问题排查:
        echo 1. SSH密钥问题: 运行 ssh -T git@gitee.com 测试
        echo 2. 权限问题: 确认你有该仓库的推送权限
        echo 3. 网络问题: 检查网络连接
        echo 4. 仓库地址: 确认远程仓库地址正确
        echo.
        echo 当前远程仓库地址:
        git remote -v
        echo.
        pause
        exit /b 1
    )
) else (
    echo.
    echo ========================================
    echo 提交成功! (未推送)
    echo ========================================
)

pause

