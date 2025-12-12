"""
Configuration for Mock MLLP Target Server
"""

# ============================================================================
# SERVER SETTINGS - Configure where the target listens
# ============================================================================

# Host address to bind to
# - "0.0.0.0" = Listen on all network interfaces (accessible from network)
# - "localhost" or "127.0.0.1" = Listen only on local machine
# - Specific IP = Listen on that IP address only
MOCK_TARGET_HOST = "0.0.0.0"

# Port number to listen on
# - Must be available (not in use by another application)
# - Must match the port configured in Mirth Connect destination
# - Common HL7 ports: 7001, 7002, 6661, etc.
MOCK_TARGET_PORT = 7001

# ============================================================================
# DATABASE SETTINGS
# ============================================================================

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "mirth_db",
    "user": "mirth_user",
    "password": "your_password"
}

# ============================================================================
# LOGGING SETTINGS
# ============================================================================

# Channel ID for logging
CHANNEL_ID = "mock_target_channel"

# Log level (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL = "INFO"

# ============================================================================
# ACK BEHAVIOR
# ============================================================================

# Always send positive acknowledgment (AA)
ALWAYS_SEND_POSITIVE_ACK = True

# Simulate errors for testing (0.0 to 1.0, where 0.1 = 10% error rate)
ERROR_SIMULATION_RATE = 0.0