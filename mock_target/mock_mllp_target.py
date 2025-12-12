import socket
import threading
from typing import Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class MockMLLPTarget:
    """
    Mock MLLP Target Server
    
    Listens on a configured port for incoming HL7 messages via MLLP protocol.
    Acts as a message receiver that validates, acknowledges, and logs messages.
    """
    
    def __init__(self, host: str = "0.0.0.0", port: int = 7001):
        """
        Initialize MLLP target server
        
        Args:
            host: Host address to bind to (0.0.0.0 = all interfaces)
            port: Port number to listen on (e.g., 7001)
        """
        self.host = host
        self.port = port
        self.server_socket = None
        self.running = False
        self.parser = HL7Parser()
        self.db_logger = DatabaseLogger()
        
        # MLLP protocol framing characters
        self.MLLP_START = b'\x0B'  # Vertical tab (start of message)
        self.MLLP_END = b'\x1C\x0D'  # File separator + carriage return (end)
    
    def start(self):
        """Start the MLLP target server and begin listening on the port"""
        try:
            # Create TCP socket
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # Bind to host and port
            self.server_socket.bind((self.host, self.port))
            
            # Start listening (backlog of 5 connections)
            self.server_socket.listen(5)
            
            self.running = True
            
            logger.info(f"Mock MLLP Target listening on {self.host}:{self.port}")
            print(f"✓ MLLP Target Server started")
            print(f"  Host: {self.host}")
            print(f"  Port: {self.port}")
            print(f"  Waiting for connections...")
            
            # Accept connections in a loop
            while self.running:
                try:
                    # Accept incoming connection (blocks until connection arrives)
                    client_socket, client_address = self.server_socket.accept()
                    
                    logger.info(f"Connection accepted from {client_address}")
                    
                    # Handle client in separate thread
                    client_thread = threading.Thread(
                        target=self._handle_client,
                        args=(client_socket, client_address)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                    
                except Exception as e:
                    if self.running:
                        logger.error(f"Error accepting connection: {e}")
        
        except Exception as e:
            logger.error(f"Failed to start MLLP target: {e}")
            raise
    
    def _handle_client(self, client_socket: socket.socket, 
                      client_address: Tuple[str, int]):
        """
        Handle a connected client
        
        Args:
            client_socket: Socket for the connected client
            client_address: Tuple of (host, port) for the client
        """
        try:
            logger.info(f"Handling client {client_address}")
            
            # Read message from socket
            message = self._read_mllp_message(client_socket)
            
            if message:
                received_time = datetime.now()
                logger.info(f"Received message from {client_address}: {len(message)} bytes")
                
                # Process the message
                self._process_message(message, client_address, received_time, client_socket)
            
        except Exception as e:
            logger.error(f"Error handling client {client_address}: {e}")
        
        finally:
            client_socket.close()
            logger.info(f"Connection closed: {client_address}")
    
    def _read_mllp_message(self, client_socket: socket.socket) -> str:
        """
        Read MLLP-framed message from socket
        
        MLLP Format: <0x0B>MESSAGE_CONTENT<0x1C><0x0D>
        
        Returns:
            Decoded message content (without MLLP framing)
        """
        try:
            buffer = b''
            
            # Read until we get the start byte
            while True:
                byte = client_socket.recv(1)
                if not byte:
                    return None
                if byte == self.MLLP_START:
                    break
            
            # Read message content until end bytes
            while True:
                byte = client_socket.recv(1)
                if not byte:
                    break
                
                buffer += byte
                
                # Check for end sequence
                if buffer.endswith(self.MLLP_END):
                    # Remove end bytes and decode
                    message = buffer[:-2].decode('utf-8', errors='ignore')
                    return message
            
            return None
            
        except Exception as e:
            logger.error(f"Error reading MLLP message: {e}")
            return None
    
    def stop(self):
        """Stop the MLLP target server"""
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        logger.info("Mock MLLP Target stopped")