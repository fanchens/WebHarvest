@echo off
setlocal enabledelayedexpansion

REM Git commit script - commit to dev branch
REM Repository: git@gitee.com:fanchenn/web-harvest.git (SSH)

set REPO_URL=git@gitee.com:fanchenn/web-harvest.git
set BRANCH=dev
set SCRIPT_DIR=%~dp0

cd /d "%SCRIPT_DIR%"

echo ========================================
echo Git commit script - commit to dev branch
echo ========================================
echo.

REM Auto-add Gitee SSH host key
set SSH_DIR=%USERPROFILE%\.ssh
set KNOWN_HOSTS=%SSH_DIR%\known_hosts
if not exist "%SSH_DIR%" mkdir "%SSH_DIR%"
if not exist "%KNOWN_HOSTS%" (
    echo. > "%KNOWN_HOSTS%"
)
findstr /C:"gitee.com" "%KNOWN_HOSTS%" >nul 2>&1
if errorlevel 1 (
    echo Adding Gitee SSH host key to known_hosts...
    where ssh-keyscan >nul 2>&1
    if errorlevel 1 (
        echo [WARN] ssh-keyscan not found, need to type yes on first connection
    ) else (
        ssh-keyscan -t ed25519 gitee.com >> "%KNOWN_HOSTS%" 2>nul
        if errorlevel 1 (
            echo [WARN] Failed to add SSH host key, need to type yes on first connection
        ) else (
            echo [OK] SSH host key added
        )
    )
    echo.
)

REM Check if Git repository is initialized
if not exist ".git" (
    echo Initializing Git repository...
    git init
    if errorlevel 1 (
        echo [ERROR] Git initialization failed
        pause
        exit /b 1
    )
    echo [OK] Git repository initialized
)

REM Check remote repository configuration
git remote | findstr /C:"origin" >nul
if errorlevel 1 (
    echo Adding remote repository...
    git remote add origin %REPO_URL%
    if errorlevel 1 (
        echo [ERROR] Failed to add remote repository
        pause
        exit /b 1
    )
    echo [OK] Remote repository added: %REPO_URL%
) else (
    REM Check and update remote URL if different
    for /f "tokens=*" %%u in ('git remote get-url origin 2^>nul') do set CURRENT_URL=%%u
    if not "!CURRENT_URL!"=="%REPO_URL%" (
        echo Updating remote repository URL...
        git remote set-url origin %REPO_URL%
        if errorlevel 1 (
            echo [ERROR] Failed to update remote repository URL
            pause
            exit /b 1
        )
        echo [OK] Remote repository URL updated: %REPO_URL%
    ) else (
        echo [OK] Remote repository configured: %REPO_URL%
    )
)

REM Check current branch
for /f "tokens=*" %%i in ('git branch --show-current 2^>nul') do set CURRENT_BRANCH=%%i
if "!CURRENT_BRANCH!"=="" (
    echo Creating dev branch...
    git checkout -b %BRANCH%
    if errorlevel 1 (
        echo [ERROR] Failed to create branch
        pause
        exit /b 1
    )
    echo [OK] Created and switched to dev branch
) else if not "!CURRENT_BRANCH!"=="%BRANCH%" (
    echo Current branch: !CURRENT_BRANCH!
    echo Switching to dev branch...
    git checkout -b %BRANCH% 2>nul
    if errorlevel 1 (
        git checkout %BRANCH%
        if errorlevel 1 (
            echo [ERROR] Failed to switch branch
            pause
            exit /b 1
        )
    )
    echo [OK] Switched to dev branch
) else (
    echo [OK] Already on dev branch
)

echo.
echo Current Git status:
git status --short 2>nul

echo.

REM Check for untracked or modified files
git status --porcelain | findstr /R "." >nul 2>&1
if errorlevel 1 (
    echo [INFO] No changes to commit, working tree clean
    echo.
    REM Check if remote branch exists
    git ls-remote --heads origin %BRANCH% >nul 2>&1
    if errorlevel 1 (
        REM Remote branch doesn't exist, push directly
        echo Remote branch doesn't exist, will create and push...
        echo.
        goto :push_only
    )
    REM Check for unpushed commits
    git log origin/%BRANCH%..HEAD --oneline 2>nul | findstr /R "." >nul 2>&1
    if not errorlevel 1 (
        echo Detected unpushed commits, continuing push...
        echo.
        goto :push_only
    ) else (
        echo Local and remote are synchronized, nothing to push
        pause
        exit /b 0
    )
)

REM Add all changes
echo Adding all changes to staging area
git add .
if errorlevel 1 (
    echo [ERROR] Failed to add files
    pause
    exit /b 1
)
echo [OK] Files added to staging area

echo.

REM Check again if there are changes to commit
git status --porcelain | findstr /R "." >nul 2>&1
if errorlevel 1 (
    echo [INFO] No changes to commit after adding
    echo.
    REM Check if remote branch exists
    git ls-remote --heads origin %BRANCH% >nul 2>&1
    if errorlevel 1 (
        REM Remote branch doesn't exist, push directly
        echo Remote branch doesn't exist, will create and push...
        echo.
        goto :push_only
    )
    REM Check for unpushed commits
    git log origin/%BRANCH%..HEAD --oneline 2>nul | findstr /R "." >nul 2>&1
    if not errorlevel 1 (
        echo Detected unpushed commits, continuing push...
        echo.
        goto :push_only
    ) else (
        echo Local and remote are synchronized, nothing to commit and push
        pause
        exit /b 0
    )
)

REM Get commit message
set /p COMMIT_MESSAGE="Enter commit message (press Enter for default): "
if "!COMMIT_MESSAGE!"=="" (
    for /f "tokens=1-3 delims=/ " %%a in ('date /t') do set DATE_STR=%%c-%%a-%%b
    for /f "tokens=1-2 delims=: " %%a in ('time /t') do set TIME_STR=%%a:%%b
    set COMMIT_MESSAGE=Update: !DATE_STR! !TIME_STR!
)

echo.

REM Commit changes
echo Committing changes...
git commit -m "!COMMIT_MESSAGE!"
if errorlevel 1 (
    echo [WARN] Commit failed, may be no changes to commit
    REM Check if remote branch exists
    git ls-remote --heads origin %BRANCH% >nul 2>&1
    if errorlevel 1 (
        REM Remote branch doesn't exist, push directly
        echo Remote branch doesn't exist, will create and push...
        echo.
        goto :push_only
    )
    REM Check for unpushed commits
    git log origin/%BRANCH%..HEAD --oneline 2>nul | findstr /R "." >nul 2>&1
    if not errorlevel 1 (
        echo Detected unpushed commits, continuing push...
        echo.
        goto :push_only
    ) else (
        echo Local and remote are synchronized, nothing to commit and push
        pause
        exit /b 0
    )
)
echo [OK] Commit successful

echo.

:push_only
REM Push to remote repository
echo Pushing to remote repository (dev branch)...
REM Detect available SSH key file
set SSH_KEY_FILE=
if exist "%USERPROFILE%\.ssh\id_ed25519" (
    set SSH_KEY_FILE=%USERPROFILE%\.ssh\id_ed25519
) else if exist "%USERPROFILE%\.ssh\id_rsa" (
    set SSH_KEY_FILE=%USERPROFILE%\.ssh\id_rsa
)
REM Set SSH options, auto-accept host key, and specify key file
if defined SSH_KEY_FILE (
    set GIT_SSH_COMMAND=ssh -o StrictHostKeyChecking=accept-new -i "%SSH_KEY_FILE%"
) else (
    set GIT_SSH_COMMAND=ssh -o StrictHostKeyChecking=accept-new
)
git push -u origin %BRANCH% >temp_push_output.txt 2>&1
set PUSH_ERROR=%ERRORLEVEL%
type temp_push_output.txt
findstr /C:"rejected" /C:"fetch first" temp_push_output.txt >nul
if not errorlevel 1 (
    REM Push rejected, use force push to overwrite remote branch
    echo [INFO] Remote has new changes, using force push to overwrite...
    git push -u origin %BRANCH% --force-with-lease
    if errorlevel 1 (
        echo [ERROR] Force push failed
        del temp_push_output.txt >nul 2>&1
        set GIT_SSH_COMMAND=
        set SSH_KEY_FILE=
        pause
        exit /b 1
    )
    echo [OK] Force push successful
) else (
    if %PUSH_ERROR% neq 0 (
        REM Other push errors
        echo [ERROR] Push failed, please check network connection and permissions
        echo.
        echo Troubleshooting:
        echo 1. If using DeployKey, it only supports pull, not push
        echo    Need to add SSH public key to Gitee personal account settings (not repository DeployKey)
        echo 2. Check if SSH key is correctly added to Gitee personal account
        echo    Visit: https://gitee.com/profile/sshkeys
        echo 3. If prompted for host key confirmation, type yes and run script again
        echo 4. Check if Git is using the correct SSH key
        echo.
        echo Test SSH connection: ssh -T git@gitee.com
        del temp_push_output.txt >nul 2>&1
        set GIT_SSH_COMMAND=
        set SSH_KEY_FILE=
        pause
        exit /b 1
    )
)
del temp_push_output.txt >nul 2>&1
set GIT_SSH_COMMAND=
set SSH_KEY_FILE=
echo [OK] Push successful

echo.
echo ========================================
echo [OK] All operations completed!
echo ========================================
pause
