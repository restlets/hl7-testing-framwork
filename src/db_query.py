"""
Database query module for validating routing logs
"""
import psycopg2
import logging
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class RoutingLogQuery:
    """Query routing logs from PostgreSQL database"""
    
    def __init__(self, db_config: Dict[str, Any]):
        self.db_config = db_config
        self.connection = None
    
    def connect(self) -> bool:
        """Connect to PostgreSQL database"""
        try:
            self.connection = psycopg2.connect(
                host=self.db_config['host'],
                port=self.db_config['port'],
                database=self.db_config['database'],
                user=self.db_config['user'],
                password=self.db_config['password']
            )
            logger.info("Connected to PostgreSQL database")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            return False
    
    def query_routing_log(self, message_id: str, start_time: datetime) -> Optional[Dict[str, Any]]:
        """
        Query routing log for a specific message
        
        Args:
            message_id: HL7 message control ID
            start_time: Time when message was sent
        
        Returns:
            Dictionary with routing information or None if not found
        """
        try:
            if not self.connection:
                if not self.connect():
                    return None
            
            cursor = self.connection.cursor()
            
            # Query routing log table
            # Adjust table and column names based on your Mirth database schema
            query = """
                SELECT 
                    message_id,
                    channel_id,
                    destination_host,
                    destination_port,
                    status,
                    error_message,
                    sent_time,
                    received_time
                FROM hlp_routing_log
                WHERE message_id = %s
                    AND sent_time >= %s
                ORDER BY sent_time DESC
                LIMIT 1
            """
            
            cursor.execute(query, (message_id, start_time))
            result = cursor.fetchone()
            
            if result:
                routing_data = {
                    'message_id': result[0],
                    'channel_id': result[1],
                    'destination_host': result[2],
                    'destination_port': result[3],
                    'status': result[4],
                    'error_message': result[5],
                    'sent_time': result[6],
                    'received_time': result[7]
                }
                logger.info(f"Found routing log for message {message_id}")
                return routing_data
            else:
                logger.warning(f"No routing log found for message {message_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error querying routing log: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
    
    def close(self):
        """Close database connection"""
        if self.connection:
            try:
                self.connection.close()
                logger.info("Closed database connection")
            except Exception as e:
                logger.error(f"Error closing database connection: {e}")
            finally:
                self.connection = None
    
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()