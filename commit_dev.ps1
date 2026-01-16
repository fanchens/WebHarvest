# Git提交脚本 - 提交到dev分支
# 使用方法: .\commit_dev.ps1 [提交信息]

param(
    [string]$commitMessage = ""
)

# 设置错误处理
$ErrorActionPreference = "Stop"

# 切换到项目目录
$projectPath = "E:\PyCharm\PythonProject\WebHarvest"
Set-Location $projectPath

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Git提交脚本 - dev分支" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查是否在git仓库中
if (-not (Test-Path ".git")) {
    Write-Host "错误: 当前目录不是git仓库!" -ForegroundColor Red
    exit 1
}

# 检查git状态
Write-Host "检查git状态..." -ForegroundColor Yellow
git status --short

# 检查是否有未提交的更改
$status = git status --porcelain
if ([string]::IsNullOrWhiteSpace($status)) {
    Write-Host "没有需要提交的更改!" -ForegroundColor Yellow
    exit 0
}

# 切换到dev分支
Write-Host ""
Write-Host "切换到dev分支..." -ForegroundColor Yellow
$currentBranch = git branch --show-current
if ($currentBranch -ne "dev") {
    # 检查dev分支是否存在
    $branchExists = git branch -a | Select-String "dev"
    if ($branchExists) {
        git checkout dev
    } else {
        Write-Host "dev分支不存在，创建dev分支..." -ForegroundColor Yellow
        git checkout -b dev
    }
} else {
    Write-Host "当前已在dev分支" -ForegroundColor Green
}

# 添加所有更改
Write-Host ""
Write-Host "添加所有更改的文件..." -ForegroundColor Yellow
git add .

# 获取提交信息
if ([string]::IsNullOrWhiteSpace($commitMessage)) {
    Write-Host ""
    $commitMessage = Read-Host "请输入提交信息"
    if ([string]::IsNullOrWhiteSpace($commitMessage)) {
        Write-Host "错误: 提交信息不能为空!" -ForegroundColor Red
        exit 1
    }
}

# 提交更改
Write-Host ""
Write-Host "提交更改..." -ForegroundColor Yellow
git commit -m $commitMessage

if ($LASTEXITCODE -ne 0) {
    Write-Host "提交失败!" -ForegroundColor Red
    exit 1
}

Write-Host "提交成功!" -ForegroundColor Green

# 推送到远程
Write-Host ""
$push = Read-Host "是否推送到远程dev分支? (y/n)"
if ($push -eq "y" -or $push -eq "Y") {
    # 测试SSH连接
    Write-Host ""
    Write-Host "测试SSH连接..." -ForegroundColor Yellow
    $sshTest = ssh -T git@gitee.com 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[警告] SSH连接测试失败!" -ForegroundColor Red
        Write-Host ""
        Write-Host "可能的原因:" -ForegroundColor Yellow
        Write-Host "1. SSH密钥未配置或未添加到Gitee账户"
        Write-Host "2. SSH密钥权限问题"
        Write-Host ""
        Write-Host "解决方案:" -ForegroundColor Yellow
        Write-Host "1. 检查SSH密钥: ssh-keygen -l -f ~/.ssh/id_rsa.pub"
        Write-Host "2. 将公钥添加到Gitee: https://gitee.com/profile/sshkeys"
        Write-Host "3. 测试连接: ssh -T git@gitee.com"
        Write-Host ""
        $continue = Read-Host "是否继续尝试推送? (y/n)"
        if ($continue -ne "y" -and $continue -ne "Y") {
            Write-Host "已取消推送" -ForegroundColor Yellow
            exit 0
        }
    } else {
        Write-Host "SSH连接正常" -ForegroundColor Green
    }
    
    Write-Host ""
    Write-Host "推送到远程dev分支..." -ForegroundColor Yellow
    git push origin dev
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Green
        Write-Host "提交并推送成功!" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Red
        Write-Host "推送失败!" -ForegroundColor Red
        Write-Host "========================================" -ForegroundColor Red
        Write-Host ""
        Write-Host "常见问题排查:" -ForegroundColor Yellow
        Write-Host "1. SSH密钥问题: 运行 ssh -T git@gitee.com 测试"
        Write-Host "2. 权限问题: 确认你有该仓库的推送权限"
        Write-Host "3. 网络问题: 检查网络连接"
        Write-Host "4. 仓库地址: 确认远程仓库地址正确"
        Write-Host ""
        Write-Host "当前远程仓库地址:" -ForegroundColor Yellow
        git remote -v
        Write-Host ""
        exit 1
    }
} else {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "提交成功! (未推送)" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
}

