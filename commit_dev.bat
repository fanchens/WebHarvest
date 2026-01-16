@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion

echo ========================================
echo Git�ύ�ű� - dev��֧
echo ========================================
echo.

REM �л�����ĿĿ¼
cd /d "E:\PyCharm\PythonProject\WebHarvest" 2>nul
if !errorlevel! neq 0 (
    echo ����: �޷��л�����ĿĿ¼!
    pause
    exit /b 1
)

REM ����Ƿ���git�ֿ���
if not exist ".git" (
    echo ����: ��ǰĿ¼����git�ֿ�!
    pause
    exit /b 1
)

REM ���git״̬
echo ���git״̬...
git status --short 2>nul

REM �л���dev��֧
echo.
echo �л���dev��֧...
git branch --show-current > temp_branch.txt 2>nul
if exist temp_branch.txt (
    set /p currentBranch=<temp_branch.txt
    del temp_branch.txt 2>nul
) else (
    set currentBranch=
)

if not "!currentBranch!"=="dev" (
    git branch -a 2>nul | findstr /C:"dev" >nul
    if !errorlevel! equ 0 (
        git checkout dev 2>nul
    ) else (
        echo dev��֧�����ڣ�����dev��֧...
        git checkout -b dev 2>nul
    )
) else (
    echo ��ǰ����dev��֧
)

REM ����Ƿ���δ�ύ�ĸ���
echo.
echo ���δ�ύ�ĸ���...
git status --porcelain > temp_status.txt 2>nul
if exist temp_status.txt (
    set /p hasChanges=<temp_status.txt
    del temp_status.txt 2>nul
) else (
    set hasChanges=
)

if "!hasChanges!"=="" (
    echo û����Ҫ�ύ�ĸ��ģ��������ɾ���
    echo.
    pause
    exit /b 0
)

REM �������и���
echo.
echo �������и��ĵ��ļ�...
git add . 2>nul

REM ��ȡ�ύ��Ϣ
echo.
set /p commitMessage="�������ύ��Ϣ: "
if "!commitMessage!"=="" (
    echo ����: �ύ��Ϣ����Ϊ��!
    pause
    exit /b 1
)

REM �ύ����
echo.
echo �ύ����...
git commit -m "!commitMessage!" 2>nul

if !errorlevel! neq 0 (
    echo �ύʧ��!
    pause
    exit /b 1
)

echo �ύ�ɹ�!

REM ���͵�Զ��
echo.
set /p push="�Ƿ����͵�Զ��dev��֧? (y/n): "
if /i "!push!"=="y" (
    echo.
    echo ����SSH����...
    ssh -T git@gitee.com > temp_ssh_test.txt 2>&1
    findstr /C:"DeployKey" temp_ssh_test.txt >nul 2>nul
    if !errorlevel! equ 0 (
        echo.
        echo [����] ��ǰSSH��Կ��DeployKey!
        echo DeployKey��֧����ȡ�������޷����͡�
        echo.
        echo �������:
        echo 1. Ϊ�˻������µ�SSH��Կ:
        echo    ssh-keygen -t rsa -C "your_email@example.com" -f "%USERPROFILE%\.ssh\id_rsa_account"
        echo.
        echo 2. ���¹�Կ���ӵ�Gitee�˻�SSH��Կ:
        echo    https://gitee.com/profile/sshkeys
        echo    ����������: %USERPROFILE%\.ssh\id_rsa_account.pub
        echo.
        echo 3. ����SSHʹ���˻���Կ:
        echo    �༭ %USERPROFILE%\.ssh\config ������:
        echo    Host gitee.com
        echo        HostName gitee.com
        echo        User git
        echo        IdentityFile ~/.ssh/id_rsa_account
        echo.
        if exist temp_ssh_test.txt type temp_ssh_test.txt
        del temp_ssh_test.txt 2>nul
        echo.
        set /p continue="�Ƿ������������? (y/n): "
        if /i not "!continue!"=="y" (
            echo ��ȡ�����͡�
            pause
            exit /b 0
        )
    ) else (
        if exist temp_ssh_test.txt del temp_ssh_test.txt 2>nul
        echo SSH��������
    )
    
    echo.
    echo ���͵�Զ��dev��֧...
    
    REM ����SSH������ʹ���˻���Կ���������·�����⣩
    set "SSH_KEY_PATH=%USERPROFILE%\.ssh\id_rsa_account"
    if exist "!SSH_KEY_PATH!" (
        echo ʹ��SSH��Կ: !SSH_KEY_PATH!
        REM ʹ��PowerShell���û���������ִ��git push
        powershell -NoProfile -Command "$sshKey = (Resolve-Path '%USERPROFILE%\.ssh\id_rsa_account').Path; $env:GIT_SSH_COMMAND = \"ssh -i `\"$sshKey`\"\"; cd 'E:\PyCharm\PythonProject\WebHarvest'; git push origin dev; $exitCode = $LASTEXITCODE; $env:GIT_SSH_COMMAND = $null; exit $exitCode"
        set PUSH_RESULT=!errorlevel!
    ) else (
        REM ���δ�ҵ��˻���Կ��ʹ��Ĭ�Ϸ�ʽ
        git push origin dev 2>nul
        set PUSH_RESULT=!errorlevel!
    )
    
    if !PUSH_RESULT! equ 0 (
        echo.
        echo ========================================
        echo �ύ�����ͳɹ�!
        echo ========================================
    ) else (
        echo.
        echo ========================================
        echo ����ʧ��!
        echo ========================================
        echo.
        echo �����Ų�:
        echo 1. SSH��Կ����: ���� ssh -T git@gitee.com ����
        echo 2. Ȩ������: ȷ����������Ȩ��
        echo 3. ��������: �����������
        echo 4. �ֿ��ַ: ȷ��Զ�ֿ̲��ַ��ȷ
        echo.
        echo ��ǰԶ�ֿ̲��ַ:
        git remote -v 2>nul
        echo.
        pause
        exit /b 1
    )
) else (
    echo.
    echo ========================================
    echo �ύ�ɹ�! (δ����)
    echo ========================================
)

pause
