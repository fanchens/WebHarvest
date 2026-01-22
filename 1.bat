@echo off
chcp 437 >nul 2>&1
setlocal enabledelayedexpansion

echo ========================================
echo Git Commit & Push Script - test branch
echo ========================================
echo.

REM Switch to project directory
cd /d "E:\PyCharm\PythonProject\WebHarvest" 2>nul
if !errorlevel! neq 0 (
    echo [ERROR] Failed to switch to project directory!
    pause
    exit /b 1
)

REM Check if it's a git repository
if not exist ".git" (
    echo [ERROR] Current directory is not a git repository!
    pause
    exit /b 1
)

REM Show git status
echo [INFO] Checking git status...
echo ----------------------------------------
git status --short 2>nul
echo ----------------------------------------
echo.

REM Switch to test branch
echo [INFO] Checking current branch...
git branch --show-current > temp_branch.txt 2>nul
if exist temp_branch.txt (
    set /p currentBranch=<temp_branch.txt
    del temp_branch.txt 2>nul
) else (
    set currentBranch=
)

if not "!currentBranch!"=="test" (
    echo [INFO] Current branch: !currentBranch!
    echo [INFO] Switching to test branch...
    git branch -a 2>nul | findstr /C:"test" >nul
    if !errorlevel! equ 0 (
        git checkout test 2>nul
        echo [SUCCESS] Switched to test branch
    ) else (
        echo [INFO] test branch not exist, create from dev...
        git checkout dev 2>nul
        git pull origin dev 2>nul
        git checkout -b test 2>nul
        echo [SUCCESS] Created and switched to test branch
    )
) else (
    echo [INFO] Already on test branch
)
echo.

REM Pull remote test branch first (avoid non-fast-forward error)
echo [INFO] Pulling latest code from remote test branch...
git pull origin test 2>nul
if !errorlevel! equ 0 (
    echo [SUCCESS] Pulled latest code from remote test branch
) else (
    echo [WARNING] No remote test branch (first push)
)
echo.

REM Check uncommitted changes
echo [INFO] Checking uncommitted changes...
git status --porcelain > temp_status.txt 2>nul
set "hasChanges="
for /f "delims=" %%a in (temp_status.txt) do set hasChanges=1
del temp_status.txt 2>nul

if not defined hasChanges (
    echo [INFO] No uncommitted changes, skip commit
    echo.
    goto :push_section
)

REM Show changed files
echo [INFO] Detected changes:
git status --short
echo.

REM Add all changes
echo [INFO] Adding changed files...
git add . 2>nul
if !errorlevel! neq 0 (
    echo [ERROR] Failed to add files!
    pause
    exit /b 1
)
echo [SUCCESS] Files added to staging area
echo.

REM Get commit message
echo [INFO] Enter commit message
echo ----------------------------------------
set /p commitMessage="Commit message: "
echo ----------------------------------------
if "!commitMessage!"=="" (
    echo [ERROR] Commit message cannot be empty!
    pause
    exit /b 1
)
echo.

REM Commit changes
echo [INFO] Committing changes...
echo [INFO] Commit message: !commitMessage!
git commit -m "!commitMessage!" 2>nul

if !errorlevel! neq 0 (
    echo [ERROR] Commit failed!
    pause
    exit /b 1
)

echo [SUCCESS] Commit successful!
echo.

:push_section
REM Push to remote test branch
echo ========================================
echo Push to remote repository - test branch
echo ========================================
echo.
echo [INFO] Remote repository info:
git remote -v 2>nul
echo.

set /p push="Push to remote test branch? (y/n): "
if /i not "!push!"=="y" (
    echo.
    echo [INFO] Push cancelled
    echo [INFO] Manual push command: git push origin test
    echo.
    pause
    exit /b 0
)

echo.
echo [INFO] Preparing SSH connection...
echo ----------------------------------------

REM Add SSH key to agent
set "SSH_KEY=%USERPROFILE%\.ssh\id_rsa_account"
if exist "!SSH_KEY!" (
    echo [INFO] Found SSH key: !SSH_KEY!
    echo [INFO] Adding SSH key to agent...
    ssh-add "!SSH_KEY!" 2>nul
    if !errorlevel! equ 0 (
        echo [SUCCESS] SSH key added to agent
    ) else (
        echo [WARNING] Failed to add SSH key to agent
    )
    
    echo.
    echo [INFO] Testing SSH connection...
    ssh -T git@gitee.com > temp_ssh_test.txt 2>&1
    findstr /C:"Hi " temp_ssh_test.txt >nul
    if !errorlevel! equ 0 (
        echo [SUCCESS] SSH connection normal
        type temp_ssh_test.txt | findstr /C:"Hi "
    ) else (
        echo [WARNING] SSH connection test failed, continue push
    )
    del temp_ssh_test.txt 2>nul
) else (
    echo [WARNING] SSH key file not found
)
echo ----------------------------------------
echo.

REM Execute push (with -u for first push)
echo [INFO] Pushing code to remote test branch...
echo [INFO] Target: origin/test
echo ----------------------------------------

if exist "!SSH_KEY!" (
    powershell -NoProfile -Command "$sshKey = (Resolve-Path '%SSH_KEY%').Path; $env:GIT_SSH_COMMAND = 'ssh -i `\"$sshKey`\"'; cd 'E:\PyCharm\PythonProject\WebHarvest'; git push -u origin test; exit $LASTEXITCODE"
) else (
    git push -u origin test
)

set PUSH_RESULT=!errorlevel!

echo ----------------------------------------

if !PUSH_RESULT! equ 0 (
    echo.
    echo ========================================
    echo [SUCCESS] Push completed!
    echo ========================================
    echo.
    echo [INFO] Latest commit:
    git log --oneline -1 2>nul
    echo.
    echo [INFO] View on Gitee: https://gitee.com/fanchenn/web-harvest/tree/test
    echo.
) else (
    echo.
    echo ========================================
    echo [ERROR] Push failed!
    echo ========================================
    echo.
    echo [TROUBLESHOOTING]
    echo 1. SSH key issue: Run 'ssh -T git@gitee.com'
    echo 2. Pull remote changes first: 'git pull origin test'
    echo 3. Manual push command: 'git push -u origin test'
    echo.
)

pause