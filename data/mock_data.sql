-- Clear existing test data (optional)
-- DELETE FROM hlp_routing_log WHERE message_id LIKE 'MSG%';

-- Insert mock routing log entries

-- ADT Messages (Admission, Discharge, Transfer)
INSERT INTO hlp_routing_log 
    (message_id, channel_id, destination_host, destination_port, status, error_message, sent_time, received_time)
VALUES
    ('MSG001', 'ADT_Channel', '192.168.1.100', 7001, 'SUCCESS', NULL, 
     NOW() - INTERVAL '1 hour', NOW() - INTERVAL '1 hour' + INTERVAL '2 seconds'),
    
    ('MSG002', 'ADT_Channel', '192.168.1.100', 7001, 'SUCCESS', NULL,
     NOW() - INTERVAL '50 minutes', NOW() - INTERVAL '50 minutes' + INTERVAL '1 second'),
    
    ('MSG003', 'ADT_Channel', '192.168.1.100', 7001, 'FAILED', 'Connection timeout',
     NOW() - INTERVAL '45 minutes', NOW() - INTERVAL '45 minutes' + INTERVAL '30 seconds'),
    
    ('MSG004', 'ADT_Channel', '192.168.1.101', 7001, 'SUCCESS', NULL,
     NOW() - INTERVAL '40 minutes', NOW() - INTERVAL '40 minutes' + INTERVAL '1 second'),

-- ORU Messages (Lab Results)
    ('MSG005', 'ORU_Channel', '192.168.1.50', 7002, 'SUCCESS', NULL,
     NOW() - INTERVAL '35 minutes', NOW() - INTERVAL '35 minutes' + INTERVAL '3 seconds'),
    
    ('MSG006', 'ORU_Channel', '192.168.1.50', 7002, 'SUCCESS', NULL,
     NOW() - INTERVAL '30 minutes', NOW() - INTERVAL '30 minutes' + INTERVAL '2 seconds'),
    
    ('MSG007', 'ORU_Channel', '192.168.1.51', 7002, 'FAILED', 'Invalid HL7 format',
     NOW() - INTERVAL '25 minutes', NOW() - INTERVAL '25 minutes' + INTERVAL '1 second'),

-- ORM Messages (Orders)
    ('MSG008', 'ORM_Channel', '192.168.1.75', 7003, 'SUCCESS', NULL,
     NOW() - INTERVAL '20 minutes', NOW() - INTERVAL '20 minutes' + INTERVAL '2 seconds'),
    
    ('MSG009', 'ORM_Channel', '192.168.1.75', 7003, 'SUCCESS', NULL,
     NOW() - INTERVAL '15 minutes', NOW() - INTERVAL '15 minutes' + INTERVAL '1 second'),
    
    ('MSG010', 'ORM_Channel', '192.168.1.75', 7003, 'PENDING', NULL,
     NOW() - INTERVAL '10 minutes', NULL),

-- MDM Messages (Medical Documents)
    ('MSG011', 'MDM_Channel', '192.168.1.200', 7004, 'SUCCESS', NULL,
     NOW() - INTERVAL '8 minutes', NOW() - INTERVAL '8 minutes' + INTERVAL '4 seconds'),
    
    ('MSG012', 'MDM_Channel', '192.168.1.200', 7004, 'FAILED', 'Destination unreachable',
     NOW() - INTERVAL '6 minutes', NOW() - INTERVAL '6 minutes' + INTERVAL '30 seconds'),

-- SIU Messages (Scheduling)
    ('MSG013', 'SIU_Channel', '192.168.1.150', 7005, 'SUCCESS', NULL,
     NOW() - INTERVAL '5 minutes', NOW() - INTERVAL '5 minutes' + INTERVAL '2 seconds'),
    
    ('MSG014', 'SIU_Channel', '192.168.1.150', 7005, 'SUCCESS', NULL,
     NOW() - INTERVAL '3 minutes', NOW() - INTERVAL '3 minutes' + INTERVAL '1 second'),

-- DFT Messages (Financial Transactions)
    ('MSG015', 'DFT_Channel', '192.168.1.180', 7006, 'SUCCESS', NULL,
     NOW() - INTERVAL '2 minutes', NOW() - INTERVAL '2 minutes' + INTERVAL '2 seconds'),
    
    ('MSG016', 'DFT_Channel', '192.168.1.180', 7006, 'FAILED', 'Authentication failed',
     NOW() - INTERVAL '1 minute', NOW() - INTERVAL '1 minute' + INTERVAL '5 seconds'),

-- VXU Messages (Vaccination Updates)
    ('MSG017', 'VXU_Channel', '192.168.1.220', 7007, 'SUCCESS', NULL,
     NOW() - INTERVAL '30 seconds', NOW() - INTERVAL '30 seconds' + INTERVAL '1 second'),
    
    ('MSG018', 'VXU_Channel', '192.168.1.220', 7007, 'SUCCESS', NULL,
     NOW() - INTERVAL '15 seconds', NOW() - INTERVAL '15 seconds' + INTERVAL '2 seconds'),

-- BAR Messages (Billing Account)
    ('MSG019', 'BAR_Channel', '192.168.1.190', 7008, 'SUCCESS', NULL,
     NOW() - INTERVAL '10 seconds', NOW() - INTERVAL '10 seconds' + INTERVAL '1 second'),
    
    ('MSG020', 'BAR_Channel', '192.168.1.190', 7008, 'PENDING', NULL,
     NOW() - INTERVAL '5 seconds', NULL);

-- Verify inserted data
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
ORDER BY sent_time DESC
LIMIT 20;