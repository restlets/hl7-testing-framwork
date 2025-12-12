"""
Test runner for executing HL7 MLLP tests
"""
import csv
import time
import logging
from datetime import datetime
from typing import List, Dict, Any
from dataclasses import dataclass, field

from mllp_client import MLLPClient
from db_query import RoutingLogQuery
import config

logger = logging.getLogger(__name__)

@dataclass
class TestCase:
    """Test case data structure"""
    test_id: str
    test_name: str
    description: str
    hl7_message: str
    expected_host: str
    expected_port: str
    expected_status: str

@dataclass
class TestResult:
    """Test result data structure"""
    test_case: TestCase
    passed: bool
    execution_time: float
    ack_received: bool
    ack_message: str = ""
    routing_found: bool = False
    actual_host: str = ""
    actual_port: str = ""
    actual_status: str = ""
    assertions: List[Dict[str, Any]] = field(default_factory=list)
    error_message: str = ""

class TestRunner:
    """Execute HL7 MLLP tests"""
    
    def __init__(self, csv_file: str):
        self.csv_file = csv_file
        self.test_cases: List[TestCase] = []
        self.test_results: List[TestResult] = []
    
    def load_test_cases(self) -> bool:
        """Load test cases from CSV file"""
        try:
            with open(self.csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    test_case = TestCase(
                        test_id=row['test_id'],
                        test_name=row['test_name'],
                        description=row['description'],
                        hl7_message=row['hl7_message'].replace('\n', '\n'),
                        expected_host=row['expected_host'],
                        expected_port=row['expected_port'],
                        expected_status=row['expected_status']
                    )
                    self.test_cases.append(test_case)
            
            logger.info(f"Loaded {len(self.test_cases)} test cases from {self.csv_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to load test cases: {e}")
            return False
    
    def run_tests(self) -> List[TestResult]:
        """Execute all test cases"""
        logger.info("Starting test execution")
        
        for i, test_case in enumerate(self.test_cases, 1):
            logger.info(f"\n{'='*60}")
            logger.info(f"Executing Test {i}/{len(self.test_cases)}: {test_case.test_name}")
            logger.info(f"{'='*60}")
            
            result = self._execute_test(test_case)
            self.test_results.append(result)
            
            # Log result
            status = "PASSED" if result.passed else "FAILED"
            logger.info(f"Test {test_case.test_id}: {status}")
        
        logger.info("\nTest execution completed")
        return self.test_results
    
    def _execute_test(self, test_case: TestCase) -> TestResult:
        """Execute a single test case"""
        start_time = time.time()
        result = TestResult(
            test_case=test_case,
            passed=False,
            execution_time=0.0,
            ack_received=False
        )
        
        try:
            # Step 1: Send MLLP message to Mirth
            logger.info("Step 1: Sending MLLP message to Mirth")
            message_sent_time = datetime.now()
            
            with MLLPClient(config.MIRTH_HOST, config.MIRTH_PORT, config.MIRTH_TIMEOUT) as client:
                success, ack_message, error = client.send_message(test_case.hl7_message)
                
                result.ack_received = success
                result.ack_message = ack_message or ""
                
                if not success:
                    result.error_message = error or "Failed to send message"
                    result.assertions.append({
                        'name': 'MLLP Message Sent',
                        'passed': False,
                        'message': result.error_message
                    })
                    result.execution_time = time.time() - start_time
                    return result
                
                result.assertions.append({
                    'name': 'MLLP Message Sent',
                    'passed': True,
                    'message': 'Message sent successfully'
                })
                
                result.assertions.append({
                    'name': 'ACK Received',
                    'passed': True,
                    'message': 'Positive ACK received from Mirth'
                })
            
            # Step 2: Wait for configured time before querying database
            logger.info(f"Step 2: Waiting {config.WAIT_TIME_BEFORE_QUERY} seconds before querying routing log")
            time.sleep(config.WAIT_TIME_BEFORE_QUERY)
            
            # Step 3: Query routing log from database
            logger.info("Step 3: Querying routing log from database")
            message_id = self._extract_message_id(test_case.hl7_message)
            
            with RoutingLogQuery(config.DB_CONFIG) as db:
                routing_data = db.query_routing_log(message_id, message_sent_time)
                
                if routing_data:
                    result.routing_found = True
                    result.actual_host = routing_data.get('destination_host', '')
                    result.actual_port = str(routing_data.get('destination_port', ''))
                    result.actual_status = routing_data.get('status', '')
                    
                    result.assertions.append({
                        'name': 'Routing Log Found',
                        'passed': True,
                        'message': f'Found routing log for message {message_id}'
                    })
                else:
                    result.assertions.append({
                        'name': 'Routing Log Found',
                        'passed': False,
                        'message': f'No routing log found for message {message_id}'
                    })
                    result.error_message = "Routing log not found in database"
                    result.execution_time = time.time() - start_time
                    return result
            
            # Step 4: Assert routing results
            logger.info("Step 4: Asserting routing results")
            
            # Assert destination host
            host_match = result.actual_host == test_case.expected_host
            result.assertions.append({
                'name': 'Destination Host Match',
                'passed': host_match,
                'message': f'Expected: {test_case.expected_host}, Actual: {result.actual_host}'
            })
            
            # Assert destination port
            port_match = result.actual_port == test_case.expected_port
            result.assertions.append({
                'name': 'Destination Port Match',
                'passed': port_match,
                'message': f'Expected: {test_case.expected_port}, Actual: {result.actual_port}'
            })
            
            # Assert routing status
            status_match = result.actual_status == test_case.expected_status
            result.assertions.append({
                'name': 'Routing Status Match',
                'passed': status_match,
                'message': f'Expected: {test_case.expected_status}, Actual: {result.actual_status}'
            })
            
            # Test passes if all assertions pass
            result.passed = all(assertion['passed'] for assertion in result.assertions)
            
        except Exception as e:
            logger.error(f"Error executing test: {e}")
            result.error_message = str(e)
            result.assertions.append({
                'name': 'Test Execution',
                'passed': False,
                'message': f'Exception: {str(e)}'
            })
        
        result.execution_time = time.time() - start_time
        return result
    
    def _extract_message_id(self, hl7_message: str) -> str:
        """Extract message control ID from HL7 message"""
        try:
            # MSH segment is the first line
            msh_segment = hl7_message.split('\n')[0]
            fields = msh_segment.split('|')
            # Message control ID is MSH-10 (index 9)
            if len(fields) > 9:
                return fields[9]
        except Exception as e:
            logger.warning(f"Could not extract message ID: {e}")
        return "UNKNOWN"
    
    def get_summary(self) -> Dict[str, Any]:
        """Get test execution summary"""
        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r.passed)
        failed = total - passed
        
        total_time = sum(r.execution_time for r in self.test_results)
        
        return {
            'total_tests': total,
            'passed': passed,
            'failed': failed,
            'success_rate': (passed / total * 100) if total > 0 else 0,
            'total_execution_time': total_time,
            'average_execution_time': total_time / total if total > 0 else 0
        }