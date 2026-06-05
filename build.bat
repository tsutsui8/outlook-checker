@echo off
chcp 65001 > nul
echo ========================================
echo  受信メール確認 — exeビルド
echo ========================================

echo [1/3] 依存ライブラリをインストール中...
pip install pywin32 pyinstaller --quiet
if errorlevel 1 (
    echo エラー: pip install に失敗しました
    pause & exit /b 1
)

echo [2/3] pywin32 のポストインストール処理...
python Scripts\pywin32_postinstall.py -install 2>nul
python -c "import pywin32_bootstrap" 2>nul

echo [3/3] exe をビルド中...
pyinstaller ^
    --onefile ^
    --windowed ^
    --name "受信メール確認" ^
    --hidden-import win32com ^
    --hidden-import win32com.client ^
    --hidden-import pythoncom ^
    --hidden-import pywintypes ^
    --collect-submodules win32com ^
    outlook_checker.py

if errorlevel 1 (
    echo エラー: ビルドに失敗しました
    pause & exit /b 1
)

echo.
echo ========================================
echo  完了！dist\受信メール確認.exe を配布してください
echo ========================================
pause
