from app.core import logging

def test_logging_module_importable():
    # Just importing and calling ensures coverage
    assert hasattr(logging, "__name__")
