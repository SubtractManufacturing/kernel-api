@echo off
REM Docker OpenCascade Test Script for Windows
REM This script builds the Docker image and runs comprehensive tests

echo ======================================
echo Docker OpenCascade Build ^& Test
echo ======================================

REM Step 1: Build Docker image
echo.
echo Step 1: Building Docker image...
docker build -t kernel-api:test . --no-cache
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Docker image build failed
    exit /b 1
)
echo [SUCCESS] Docker image built successfully

REM Step 2: Run OCP import test
echo.
echo Step 2: Testing OCP import in container...
docker run --rm kernel-api:test python -c "import OCP; print('OCP imported successfully')"
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] OCP import test failed
    exit /b 1
)
echo [SUCCESS] OCP import test passed

REM Step 3: Run comprehensive tests
echo.
echo Step 3: Running comprehensive OpenCascade tests...
docker run --rm -v %cd%/tests:/app/tests kernel-api:test python /app/tests/docker_opencascade_test.py
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Comprehensive tests failed
    exit /b 1
)
echo [SUCCESS] Comprehensive tests passed

REM Step 4: Start services with docker-compose
echo.
echo Step 4: Starting services with docker-compose...
docker-compose up -d
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to start services
    exit /b 1
)
echo [SUCCESS] Services started

REM Wait for API to be ready
echo.
echo Waiting for API to be ready...
set MAX_RETRIES=30
set RETRY_COUNT=0

:wait_loop
set /a RETRY_COUNT+=1
if %RETRY_COUNT% GTR %MAX_RETRIES% (
    echo [ERROR] API failed to start in 30 seconds
    exit /b 1
)

curl -s http://localhost:8000/api/v1/health >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] API is ready
    goto :api_ready
)

timeout /t 1 /nobreak >nul
echo|set /p=.
goto :wait_loop

:api_ready

REM Step 5: Test API endpoints
echo.
echo.
echo Step 5: Testing API endpoints...

REM Test health endpoint
curl -s http://localhost:8000/api/v1/health | findstr "healthy" >nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Health endpoint not working
    exit /b 1
)
echo [SUCCESS] Health endpoint working

REM Test formats endpoint
curl -s http://localhost:8000/api/v1/formats | findstr "step" >nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Formats endpoint doesn't list STEP support
    exit /b 1
)
echo [SUCCESS] Formats endpoint lists STEP support

REM Step 6: Create and test STEP file conversion
echo.
echo Step 6: Testing STEP conversion via API...

REM Create a test STEP file using the container
docker exec kernel-api python -c "from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox; from OCP.STEPControl import STEPControl_Writer, STEPControl_StepModelType; box = BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape(); writer = STEPControl_Writer(); writer.Transfer(box, STEPControl_StepModelType.STEPControl_AsIs); writer.Write('/app/test_box.step'); print('Test STEP file created')"
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to create test STEP file
    exit /b 1
)
echo [SUCCESS] Test STEP file created

REM Copy the test file from container
docker cp kernel-api:/app/test_box.step test_box.step

REM Convert STEP to STL via API
echo.
echo Converting STEP to STL via API...
curl -s -X POST "http://localhost:8000/api/v1/convert" -F "file=@test_box.step;type=application/step" -F "output_format=stl" -F "quality=medium" -o test_output.stl -w "%%{http_code}" > response_code.txt
set /p RESPONSE_CODE=<response_code.txt
del response_code.txt

if "%RESPONSE_CODE%"=="200" (
    echo [SUCCESS] STEP to STL conversion successful
    if exist test_output.stl (
        for %%F in (test_output.stl) do echo   Output file size: %%~zF bytes
        del test_output.stl
    )
) else (
    echo [ERROR] STEP to STL conversion failed ^(HTTP %RESPONSE_CODE%^)
    exit /b 1
)

REM Clean up test files
del test_box.step 2>nul
docker exec kernel-api rm -f /app/test_box.step

REM Step 7: Check container logs for errors
echo.
echo Step 7: Checking container logs...
docker-compose logs api 2>&1 | findstr /i error >nul
if %ERRORLEVEL% EQU 0 (
    echo [WARNING] Found error messages in logs
) else (
    echo [SUCCESS] No errors in container logs
)

REM Summary
echo.
echo ======================================
echo All tests completed successfully!
echo ======================================
echo.
echo OpenCascade is fully operational in Docker.
echo The API is running at http://localhost:8000
echo API documentation: http://localhost:8000/docs
echo.
echo To stop the services, run: docker-compose down
echo To view logs, run: docker-compose logs -f