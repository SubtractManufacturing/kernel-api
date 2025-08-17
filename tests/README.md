# Tests

## Structure

- **integration/** - Integration tests for the API and conversion pipeline
  - `test_api.py` - Basic API endpoint tests
  - `test_conversion.py` - Conversion pipeline tests
  - `test_ocp.py` - OpenCascade functionality tests
  - `test_real_step.py` - STEP file conversion tests
  - `test_step_api.py` - STEP API integration tests
  - `test_step_conversion.py` - STEP conversion tests

## Running Tests

### All Tests
```bash
pytest tests/
```

### Specific Test File
```bash
python tests/integration/test_conversion.py
```

### With Coverage
```bash
pytest tests/ --cov=app --cov-report=html
```

## Test Requirements

- Tests assume the API server is NOT running (they use TestClient)
- For STEP tests, WSL2 or Linux environment is recommended
- Some tests create temporary files in `temp/` directory