@echo off
echo ===================================================
echo TechGenie Image Fixer
echo ===================================================
echo.
echo This script will copy the custom AI-generated images
echo from your artifacts folder to the project assets folder.
echo.

if not exist "src\assets" (
    echo Creating assets directory...
    mkdir "src\assets"
)

echo Copying images...
copy "C:\Users\HP\.gemini\antigravity\brain\23ba3f52-eea7-4cee-bc93-0ff1d0f527d4\ai_agent_discovery_1768938373339.png" "src\assets\ai_agent_discovery.png" > nul
if %errorlevel% equ 0 ( echo [OK] AI Agent Discovery ) else ( echo [FAIL] AI Agent Discovery )

copy "C:\Users\HP\.gemini\antigravity\brain\23ba3f52-eea7-4cee-bc93-0ff1d0f527d4\instant_generation_1768938393239.png" "src\assets\instant_generation.png" > nul
if %errorlevel% equ 0 ( echo [OK] Instant Generation ) else ( echo [FAIL] Instant Generation )

copy "C:\Users\HP\.gemini\antigravity\brain\23ba3f52-eea7-4cee-bc93-0ff1d0f527d4\multi_level_support_1768938414424.png" "src\assets\multi_level_support.png" > nul
if %errorlevel% equ 0 ( echo [OK] Multi-Level Support ) else ( echo [FAIL] Multi-Level Support )

copy "C:\Users\HP\.gemini\antigravity\brain\23ba3f52-eea7-4cee-bc93-0ff1d0f527d4\fully_customizable_1768938431401.png" "src\assets\fully_customizable.png" > nul
if %errorlevel% equ 0 ( echo [OK] Fully Customizable ) else ( echo [FAIL] Fully Customizable )

copy "C:\Users\HP\.gemini\antigravity\brain\23ba3f52-eea7-4cee-bc93-0ff1d0f527d4\academic_integrity_1768938446903.png" "src\assets\academic_integrity.png" > nul
if %errorlevel% equ 0 ( echo [OK] Academic Integrity ) else ( echo [FAIL] Academic Integrity )

copy "C:\Users\HP\.gemini\antigravity\brain\23ba3f52-eea7-4cee-bc93-0ff1d0f527d4\continuous_updates_1768938462307.png" "src\assets\continuous_updates.png" > nul
if %errorlevel% equ 0 ( echo [OK] Continuous Updates ) else ( echo [FAIL] Continuous Updates )

echo.
echo ===================================================
echo Done! 
echo.
echo Please reload your website.
echo You may need to uncomment the image imports in src/components/Features.js
echo ===================================================
pause
