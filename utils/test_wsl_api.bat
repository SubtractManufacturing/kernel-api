@echo off
echo Testing API running in WSL...
echo.

REM Test health endpoint
echo Checking API health...
curl http://localhost:8000/api/v1/health
echo.
echo.

REM Upload and convert a STEP file to STL
echo Converting STEP to STL...
curl -X POST "http://localhost:8000/api/v1/convert" ^
  -F "file=@sample.step" ^
  -F "output_format=stl" ^
  -F "deflection=0.1" ^
  -o converted_output.stl

echo.
echo Conversion complete! Check converted_output.stl
pause