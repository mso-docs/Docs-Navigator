@echo off
echo Installing Tesseract OCR for Windows...
echo.

REM Check if chocolatey is available
where choco >nul 2>nul
if %errorlevel%==0 (
    echo Chocolatey found. Installing Tesseract...
    choco install tesseract -y
    if %errorlevel%==0 (
        echo Tesseract installed successfully!
        echo Testing installation...
        tesseract --version
        goto :test_python
    ) else (
        echo Chocolatey installation failed.
        goto :manual_instructions
    )
) else (
    echo Chocolatey not found.
    goto :manual_instructions
)

:manual_instructions
echo.
echo ==================================================
echo Manual Installation Instructions:
echo ==================================================
echo.
echo 1. Download Tesseract from:
echo    https://github.com/UB-Mannheim/tesseract/wiki
echo.
echo 2. Run the installer and make sure to:
echo    - Check "Add to PATH" option during installation
echo    - Or install to C:\Program Files\Tesseract-OCR\
echo.
echo 3. Restart your command prompt after installation
echo.
echo 4. Test by running: tesseract --version
echo.
echo Alternative installation methods:
echo - Scoop: scoop install tesseract
echo - Conda: conda install -c conda-forge tesseract
echo.
pause
exit /b 1

:test_python
echo.
echo Testing Python integration...
uv run python -c "import pytesseract; print('Tesseract version:', pytesseract.get_tesseract_version())"
if %errorlevel%==0 (
    echo.
    echo ✅ OCR setup completed successfully!
    echo.
    echo Next steps:
    echo 1. Run: uv run python tests/test_ocr.py
    echo 2. Start the app: uv run python app_gradio.py
    echo 3. Test OCR with your documents
) else (
    echo.
    echo ❌ Python integration test failed
    echo Make sure Tesseract is in your PATH
)

echo.
pause