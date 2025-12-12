"""
MLLP Client for sending HL7 messages to Mirth Connect
"""
import socket
import logging
from typing import Tuple, Optional

logger = logging.getLogger(__name__)

# MLLP Protocol Characters
START_OF_BLOCK = b'\x0b'
END_OF_BLOCK = b'\x1c'
CARRIAGE_RETURN = b'\x0d'

class MLLPClient:
    """Client for sending HL7 messages via MLLP protocol"""
    
    def __init__(self, host: str, port: int, timeout: int = 30):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.socket = None
    
    def connect(self) -> bool:
        """Establish connection to MLLP server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(self.timeout)
            self.socket.connect((self.host, self.port))
            logger.info(f"Connected to MLLP server at {self.host}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to MLLP server: {e}")
            return False
    
    def send_message(self, hl7_message: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Send HL7 message and receive ACK
        
        Returns:
            Tuple of (success, ack_message, error_message)
        """
        try:
            if not self.socket:
                if not self.connect():
                    return False, None, "Failed to connect to server"
            
            # Wrap message in MLLP envelope
            mllp_message = START_OF_BLOCK + hl7_message.encode('utf-8') + END_OF_BLOCK + CARRIAGE_RETURN
            
            # Send message
            self.socket.sendall(mllp_message)
            logger.info(f"Sent HL7 message ({len(hl7_message)} bytes)")
            
            # Receive ACK
            response = self._receive_response()
            
            if response:
                ack_message = self._unwrap_mllp(response)
                
                # Check if ACK is positive (AA) or negative (AE, AR)
                if self._is_positive_ack(ack_message):
                    logger.info("Received positive ACK")
                    return True, ack_message, None
                else:
                    logger.warning(f"Received negative ACK: {ack_message}")
                    return False, ack_message, "Negative ACK received"
            else:
                return False, None, "No ACK received"
                
        except socket.timeout:
            error = "Timeout waiting for ACK"
            logger.error(error)
            return False, None, error
        except Exception as e:
            error = f"Error sending message: {str(e)}"
            logger.error(error)
            return False, None, error
    
    def _receive_response(self) -> Optional[bytes]:
        """Receive MLLP response from server"""
        try:
            response = b''
            while True:
                chunk = self.socket.recv(4096)
                if not chunk:
                    break
                response += chunk
                # Check if we've received the complete message
                if END_OF_BLOCK + CARRIAGE_RETURN in response:
                    break
            return response
        except Exception as e:
            logger.error(f"Error receiving response: {e}")
            return None
    
    def _unwrap_mllp(self, mllp_message: bytes) -> str:
        """Remove MLLP envelope from message"""
        try:
            # Remove MLLP wrapper characters
            message = mllp_message.replace(START_OF_BLOCK, b'')
            message = message.replace(END_OF_BLOCK, b'')
            message = message.replace(CARRIAGE_RETURN, b'')
            return message.decode('utf-8')
        except Exception as e:
            logger.error(f"Error unwrapping MLLP message: {e}")
            return ""
    
    def _is_positive_ack(self, ack_message: str) -> bool:
        """Check if ACK is positive (AA acknowledgment code)"""
        # Look for MSA segment with AA acknowledgment code
        for line in ack_message.split('\n'):
            if line.startswith('MSA'):
                fields = line.split('|')
                if len(fields) > 1 and fields[1] == 'AA':
                    return True
        return False
    
    def close(self):
        """Close the socket connection"""
        if self.socket:
            try:
                self.socket.close()
                logger.info("Closed MLLP connection")
            except Exception as e:
                logger.error(f"Error closing connection: {e}")
            finally:
                self.socket = None

    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()