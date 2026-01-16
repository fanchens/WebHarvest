# Git 提交脚本 - 提交到 dev 分支
# 仓库地址: git@gitee.com:fanchenn/web-harvest.git (SSH)

$ErrorActionPreference = "Stop"

# 配置信息
$REPO_URL = "git@gitee.com:fanchenn/web-harvest.git"
$BRANCH = "dev"
$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path

# 切换到项目目录
Set-Location $SCRIPT_DIR

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Git 提交脚本 - 提交到 dev 分支" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 自动添加 Gitee SSH 主机密钥（避免首次连接时的手动确认）
$sshDir = Join-Path $env:USERPROFILE ".ssh"
$knownHosts = Join-Path $sshDir "known_hosts"
if (-not (Test-Path $sshDir)) {
    New-Item -ItemType Directory -Path $sshDir -Force | Out-Null
}
if (-not (Test-Path $knownHosts) -or (Get-Content $knownHosts -ErrorAction SilentlyContinue | Select-String -Pattern "gitee.com" -Quiet) -eq $false) {
    Write-Host "添加 Gitee SSH 主机密钥到 known_hosts..." -ForegroundColor Yellow
    $result = ssh-keyscan -t ed25519 gitee.com 2>$null
    if ($result) {
        Add-Content -Path $knownHosts -Value $result -ErrorAction SilentlyContinue
        Write-Host "[OK] SSH 主机密钥已添加" -ForegroundColor Green
    } else {
        Write-Host "[WARN] 无法自动添加 SSH 主机密钥，首次连接时需要手动确认" -ForegroundColor Yellow
    }
    Write-Host ""
}

# 检查是否已初始化 Git 仓库
if (-not (Test-Path ".git")) {
    Write-Host "初始化 Git 仓库..." -ForegroundColor Yellow
    git init
    Write-Host "[OK] Git 仓库初始化完成" -ForegroundColor Green
}

# 检查远程仓库配置
$remoteExists = git remote | Select-String -Pattern "origin" -Quiet
if (-not $remoteExists) {
    Write-Host "添加远程仓库..." -ForegroundColor Yellow
    git remote add origin $REPO_URL
        Write-Host "[OK] 远程仓库已添加: $REPO_URL" -ForegroundColor Green
} else {
    $currentUrl = git remote get-url origin
    if ($currentUrl -ne $REPO_URL) {
        Write-Host "更新远程仓库地址..." -ForegroundColor Yellow
        git remote set-url origin $REPO_URL
        Write-Host "[OK] 远程仓库地址已更新: $REPO_URL" -ForegroundColor Green
    } else {
        Write-Host "[OK] 远程仓库已配置: $REPO_URL" -ForegroundColor Green
    }
}

# 检查当前分支
$currentBranch = git branch --show-current
if ([string]::IsNullOrEmpty($currentBranch)) {
    # 如果还没有分支，创建并切换到 dev 分支
    Write-Host "创建 dev 分支..." -ForegroundColor Yellow
    git checkout -b $BRANCH
    Write-Host "[OK] 已创建并切换到 dev 分支" -ForegroundColor Green
} elseif ($currentBranch -ne $BRANCH) {
    # 如果当前不在 dev 分支，询问是否切换
    Write-Host "当前分支: $currentBranch" -ForegroundColor Yellow
    Write-Host "切换到 dev 分支..." -ForegroundColor Yellow
    git checkout -b $BRANCH 2>$null
    if ($LASTEXITCODE -ne 0) {
        git checkout $BRANCH
    }
    Write-Host "[OK] 已切换到 dev 分支" -ForegroundColor Green
} else {
    Write-Host "[OK] 当前已在 dev 分支" -ForegroundColor Green
}

Write-Host ""

# 显示当前状态
Write-Host "当前 Git 状态:" -ForegroundColor Cyan
git status --short

Write-Host ""

# 添加所有更改
Write-Host "添加所有更改到暂存区..." -ForegroundColor Yellow
git add .
if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] 文件已添加到暂存区" -ForegroundColor Green
} else {
    Write-Host "[ERROR] 添加文件失败" -ForegroundColor Red
    exit 1
}

Write-Host ""

# 检查是否有更改需要提交
$status = git status --porcelain
if ([string]::IsNullOrWhiteSpace($status)) {
    Write-Host "没有需要提交的更改" -ForegroundColor Yellow
    exit 0
}

# 获取提交信息
$commitMessage = Read-Host "请输入提交信息 (直接回车使用默认信息)"
if ([string]::IsNullOrWhiteSpace($commitMessage)) {
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $commitMessage = "Update: $timestamp"
}

Write-Host ""

# 提交更改
Write-Host "提交更改..." -ForegroundColor Yellow
git commit -m $commitMessage
if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] 提交成功" -ForegroundColor Green
} else {
    Write-Host "[ERROR] 提交失败" -ForegroundColor Red
    exit 1
}

Write-Host ""

# 推送到远程仓库
Write-Host "推送到远程仓库 (dev 分支)..." -ForegroundColor Yellow
git push -u origin $BRANCH
if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] 推送成功" -ForegroundColor Green
} else {
    Write-Host "推送失败，请检查网络连接和权限" -ForegroundColor Red
    Write-Host "提示: 如果是第一次推送，可能需要先拉取远程分支" -ForegroundColor Yellow
    Write-Host "提示: 请确保已配置 SSH 密钥并添加到 Gitee" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "[OK] 所有操作完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan

