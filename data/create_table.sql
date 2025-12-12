-- Create the routing log table
CREATE TABLE IF NOT EXISTS hlp_routing_log (
    id SERIAL PRIMARY KEY,
    message_id VARCHAR(255) NOT NULL,
    channel_id VARCHAR(255),
    destination_host VARCHAR(255),
    destination_port INTEGER,
    status VARCHAR(50),
    error_message TEXT,
    sent_time TIMESTAMP,
    received_time TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    message_type VARCHAR(50),
    sending_application VARCHAR(255),
    sending_facility VARCHAR(255),
    receiving_application VARCHAR(255),
    receiving_facility VARCHAR(255)
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_message_id ON hlp_routing_log(message_id);
CREATE INDEX IF NOT EXISTS idx_received_time ON hlp_routing_log(received_time);
CREATE INDEX IF NOT EXISTS idx_status ON hlp_routing_log(status);
CREATE INDEX IF NOT EXISTS idx_message_type ON hlp_routing_log(message_type);

-- Verify table structure
SELECT 
    column_name, 
    data_type, 
    character_maximum_length,
    is_nullable
FROM information_schema.columns
WHERE table_name = 'hlp_routing_log'
ORDER BY ordinal_position;