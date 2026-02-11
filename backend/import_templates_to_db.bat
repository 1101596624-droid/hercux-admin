@echo off
REM HERCU HTML Simulator Templates Import Script
REM Generated: 2026-02-11

echo ========================================
echo HERCU HTML Simulator Templates Import
echo ========================================
echo.
echo Target Database: hercu_db@106.14.180.66
echo SQL File: import_templates.sql
echo Templates: 24 (8 subjects x 3 each)
echo Quality Score: 75 (baseline)
echo.

echo [1/3] Connecting to database...
set PGPASSWORD=Hercu2026Secure

echo [2/3] Executing SQL import...
psql -U hercu -d hercu_db -h 106.14.180.66 -f import_templates.sql

if %ERRORLEVEL% EQU 0 (
    echo.
    echo [3/3] Verifying import...
    psql -U hercu -d hercu_db -h 106.14.180.66 -c "SELECT subject, COUNT(*) as count, AVG(quality_score) as avg_score FROM simulator_templates WHERE quality_score = 75 GROUP BY subject ORDER BY subject;"
    echo.
    echo ========================================
    echo Import SUCCESSFUL!
    echo ========================================
) else (
    echo.
    echo ========================================
    echo Import FAILED! Error code: %ERRORLEVEL%
    echo ========================================
)

pause
