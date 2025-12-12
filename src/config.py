"""
Configuration settings for HL7 MLLP Testing Framework
"""

# Mirth Connect MLLP Settings
MIRTH_HOST = "localhost"
MIRTH_PORT = 6661
MIRTH_TIMEOUT = 30  # seconds

# Database Settings (for routing log validation)
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "mirth_db",
    "user": "mirth_user",
    "password": "your_password"
}

# Test Settings
WAIT_TIME_BEFORE_QUERY = 10  # seconds to wait before querying routing log
ACK_TIMEOUT = 5  # seconds to wait for ACK response

# Report Settings
REPORT_OUTPUT_DIR = "reports"
REPORT_TITLE = "HL7 MLLP Test Report"

# Logging Settings
LOG_LEVEL = "INFO"
LOG_FILE = "test_execution.log"