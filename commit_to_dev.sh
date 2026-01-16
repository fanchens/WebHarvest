#!/bin/bash
# Git 提交脚本 - 提交到 dev 分支
# 仓库地址: git@gitee.com:fanchenn/web-harvest.git (SSH)

# 配置信息
REPO_URL="git@gitee.com:fanchenn/web-harvest.git"
BRANCH="dev"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 切换到项目目录
cd "$SCRIPT_DIR" || exit 1

echo "========================================"
echo "Git 提交脚本 - 提交到 dev 分支"
echo "========================================"
echo ""

# 检查是否已初始化 Git 仓库
if [ ! -d ".git" ]; then
    echo "初始化 Git 仓库..."
    git init
    if [ $? -ne 0 ]; then
        echo "✗ Git 初始化失败"
        exit 1
    fi
    echo "✓ Git 仓库初始化完成"
fi

# 检查远程仓库配置
if ! git remote | grep -q "^origin$"; then
    echo "添加远程仓库..."
    git remote add origin "$REPO_URL"
    if [ $? -ne 0 ]; then
        echo "✗ 添加远程仓库失败"
        exit 1
    fi
    echo "✓ 远程仓库已添加: $REPO_URL"
else
    CURRENT_URL=$(git remote get-url origin 2>/dev/null)
    if [ "$CURRENT_URL" != "$REPO_URL" ]; then
        echo "更新远程仓库地址..."
        git remote set-url origin "$REPO_URL"
        if [ $? -ne 0 ]; then
            echo "✗ 更新远程仓库地址失败"
            exit 1
        fi
        echo "✓ 远程仓库地址已更新: $REPO_URL"
    else
        echo "✓ 远程仓库已配置: $REPO_URL"
    fi
fi

# 检查当前分支
CURRENT_BRANCH=$(git branch --show-current 2>/dev/null)
if [ -z "$CURRENT_BRANCH" ]; then
    # 如果还没有分支，创建并切换到 dev 分支
    echo "创建 dev 分支..."
    git checkout -b "$BRANCH"
    if [ $? -ne 0 ]; then
        echo "✗ 创建分支失败"
        exit 1
    fi
    echo "✓ 已创建并切换到 dev 分支"
elif [ "$CURRENT_BRANCH" != "$BRANCH" ]; then
    # 如果当前不在 dev 分支，尝试切换
    echo "当前分支: $CURRENT_BRANCH"
    echo "切换到 dev 分支..."
    git checkout -b "$BRANCH" 2>/dev/null
    if [ $? -ne 0 ]; then
        git checkout "$BRANCH"
        if [ $? -ne 0 ]; then
            echo "✗ 切换分支失败"
            exit 1
        fi
    fi
    echo "✓ 已切换到 dev 分支"
else
    echo "✓ 当前已在 dev 分支"
fi

echo ""

# 显示当前状态
echo "当前 Git 状态:"
git status --short

echo ""

# 添加所有更改
echo "添加所有更改到暂存区..."
git add .
if [ $? -ne 0 ]; then
    echo "✗ 添加文件失败"
    exit 1
fi
echo "✓ 文件已添加到暂存区"

echo ""

# 检查是否有更改需要提交
if [ -z "$(git status --porcelain)" ]; then
    echo "没有需要提交的更改"
    exit 0
fi

# 获取提交信息
read -p "请输入提交信息 (直接回车使用默认信息): " COMMIT_MESSAGE
if [ -z "$COMMIT_MESSAGE" ]; then
    TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")
    COMMIT_MESSAGE="Update: $TIMESTAMP"
fi

echo ""

# 提交更改
echo "提交更改..."
git commit -m "$COMMIT_MESSAGE"
if [ $? -ne 0 ]; then
    echo "✗ 提交失败"
    exit 1
fi
echo "✓ 提交成功"

echo ""

# 推送到远程仓库
echo "推送到远程仓库 (dev 分支)..."
git push -u origin "$BRANCH"
if [ $? -ne 0 ]; then
    echo "✗ 推送失败，请检查网络连接和权限"
    echo "提示: 如果是第一次推送，可能需要先拉取远程分支"
    echo "提示: 请确保已配置 SSH 密钥并添加到 Gitee"
    exit 1
fi
echo "✓ 推送成功"

echo ""
echo "========================================"
echo "✓ 所有操作完成！"
echo "========================================"

