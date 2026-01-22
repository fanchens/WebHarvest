@echo off
chcp 437 >nul
setlocal enabledelayedexpansion

:: Clean temp files
if exist temp_branch.txt del temp_branch.txt
if exist temp_ssh_test.txt del temp_ssh_test.txt

echo ========================================
echo Git Push Script - Current to Target Branch
echo ========================================
echo.

:: Step 1: Get current branch
echo [INFO] Detecting current branch...
for /f "tokens=*" %%i in ('git branch --show-current 2^>nul') do set "currentBranch=%%i"
if "!currentBranch!"=="" (
    echo [ERROR] Failed to get current branch! Make sure you are in a Git repo.
    pause
    exit /b 1
)
echo [INFO] Current branch: !currentBranch!
echo.

:: Step 2: Input target branch
echo [INFO] Please enter target branch name (e.g.: test, dev, prod, main)
echo ----------------------------------------
set "targetBranch="
set /p targetBranch=Target branch name: 
echo ----------------------------------------
if "!targetBranch!"=="" (
    echo [ERROR] Target branch name cannot be empty!
    pause
    exit /b 1
)
if "!currentBranch!"=="!targetBranch!" (
    echo [INFO] Current branch is same as target branch, will push directly!
    echo.
)

:: Step 3: Switch to project directory
cd /d "E:\PyCharm\PythonProject\WebHarvest" 2>nul
if !errorlevel! neq 0 (
    echo [ERROR] Cannot switch to project directory: E:\PyCharm\PythonProject\WebHarvest
    pause
    exit /b 1
)

:: Step 4: Check Git repo
if not exist ".git" (
    echo [ERROR] Current directory is not a Git repository!
    pause
    exit /b 1
)

:: Step 5: Check changes
echo [INFO] Checking changes in current branch (!currentBranch!)...
echo ----------------------------------------
git status --short 2>nul
echo ----------------------------------------
echo.

:: Check uncommitted changes
set "hasChanges="
for /f "tokens=*" %%i in ('git status --porcelain 2^>nul') do set "hasChanges=1"
if not defined hasChanges (
    echo [INFO] No uncommitted changes, skip commit step
    echo.
    goto :push_section
)

:: Show changed files
echo [INFO] Detected changes:
git status --short 2>nul
echo.

:: Add to staging
echo [INFO] Adding changed files to staging...
git add . 2>nul
if !errorlevel! neq 0 (
    echo [ERROR] Failed to add files to staging!
    pause
    exit /b 1
)
echo [SUCCESS] All changed files added to staging
echo.

:: Input commit message
echo [INFO] Please enter commit message
echo ----------------------------------------
set "commitMessage="
set /p commitMessage=Commit message: 
echo ----------------------------------------
if "!commitMessage!"=="" (
    echo [ERROR] Commit message cannot be empty!
    pause
    exit /b 1
)
echo.

:: Commit changes
echo [INFO] Committing changes in current branch (!currentBranch!)...
echo [INFO] Commit message: !commitMessage!
git commit -m "!commitMessage!" 2>nul
if !errorlevel! neq 0 (
    echo [ERROR] Commit failed! Please check manually.
    pause
    exit /b 1
)
echo [SUCCESS] Commit succeeded!
echo.

:: Step 6: Push branch
:push_section
echo ========================================
echo Push current branch (!currentBranch!) to remote !targetBranch! branch
echo ========================================
echo.
echo [WARNING] This will push current branch code to remote !targetBranch! branch, confirm carefully!
echo [INFO] Remote repo info:
git remote -v 2>nul
echo.

set "pushConfirm="
set /p pushConfirm=Confirm push? (y/n): 
if /i not "!pushConfirm!"=="y" (
    echo.
    echo [INFO] Push cancelled
    pause
    exit /b 0
)
echo.

:: Prepare SSH connection
echo [INFO] Preparing SSH connection...
echo ----------------------------------------
set "SSH_KEY=%USERPROFILE%\.ssh\id_rsa_account"
if exist "!SSH_KEY!" (
    echo [INFO] Found SSH key: !SSH_KEY!
    echo [INFO] Adding key to SSH agent...
    ssh-add "!SSH_KEY!" 2>nul
    if !errorlevel! equ 0 (
        echo [SUCCESS] SSH key added to agent
    ) else (
        echo [INFO] Failed to add key to agent, will use key file directly
    )
    
    :: Test SSH connection
    echo.
    echo [INFO] Testing SSH connection...
    ssh -T git@gitee.com > temp_ssh_test.txt 2>nul
    findstr /C:"Hi " temp_ssh_test.txt >nul
    if !errorlevel! equ 0 (
        echo [SUCCESS] SSH connection normal
        type temp_ssh_test.txt | findstr /C:"Hi "
    ) else (
        echo [INFO] SSH connection test failed, still try to push
    )
) else (
    echo [INFO] SSH key not found: !SSH_KEY!, use system default SSH config
)
echo ----------------------------------------
echo.

:: Core push command
echo [INFO] Pushing !currentBranch! to remote !targetBranch!...
echo [INFO] Target: origin/!targetBranch!
echo ----------------------------------------

:: Use native git command (most stable)
git push -u origin "!currentBranch!:!targetBranch!"

:: Record push result
set "PUSH_RESULT=%errorlevel%"

echo ----------------------------------------

:: Push result
if !PUSH_RESULT! equ 0 (
    echo.
    echo ========================================
    echo [SUCCESS] Pushed !currentBranch! to remote !targetBranch! successfully!
    echo ========================================
    echo.
    echo [INFO] Latest commit:
    git log --oneline -1 2>nul
    echo.
    echo [INFO] View URL: https://gitee.com/fanchenn/web-harvest/tree/!targetBranch!
    echo.
) else (
    echo.
    echo ========================================
    echo [ERROR] Failed to push !currentBranch! to !targetBranch!
    echo ========================================
    echo.
    echo [TROUBLESHOOT]
    echo 1. Check SSH key: Make sure !SSH_KEY! exists and configured correctly
    echo 2. Test SSH manually: ssh -T git@gitee.com
    echo 3. Push manually: git push -u origin !currentBranch!:!targetBranch!
    echo 4. Permission issue: Check SSH key in Gitee settings
    echo.
)

:: Clean temp files
if exist temp_branch.txt del temp_branch.txt
if exist temp_ssh_test.txt del temp_ssh_test.txt

pause