"""
Main execution script for HL7 MLLP Testing Framework
"""
import logging
import sys
from datetime import datetime

from test_runner import TestRunner
from report_generator import ReportGenerator
import config

def setup_logging():
    """Configure logging"""
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(log_format))
    
    # File handler
    file_handler = logging.FileHandler(config.LOG_FILE)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(log_format))
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

def main():
    """Main execution function"""
    print("="*70)
    print(" HL7 MLLP Testing Framework")
    print("="*70)
    print()
    
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # Get CSV file path
        csv_file = input("Enter path to CSV test file (or press Enter for 'test_cases.csv'): ").strip()
        if not csv_file:
            csv_file = "test_cases.csv"
        
        # Initialize test runner
        logger.info(f"Initializing test runner with file: {csv_file}")
        runner = TestRunner(csv_file)
        
        # Load test cases
        if not runner.load_test_cases():
            logger.error("Failed to load test cases")
            return 1
        
        print(f"\nLoaded {len(runner.test_cases)} test cases")
        print()
        
        # Confirm execution
        response = input("Do you want to proceed with test execution? (y/n): ").strip().lower()
        if response != 'y':
            print("Test execution cancelled")
            return 0
        
        print()
        print("Starting test execution...")
        print()
        
        # Run tests
        start_time = datetime.now()
        test_results = runner.run_tests()
        end_time = datetime.now()
        
        # Get summary
        summary = runner.get_summary()
        
        # Display summary
        print()
        print("="*70)
        print(" TEST EXECUTION SUMMARY")
        print("="*70)
        print(f"Total Tests:           {summary['total_tests']}")
        print(f"Passed:                {summary['passed']}")
        print(f"Failed:                {summary['failed']}")
        print(f"Success Rate:          {summary['success_rate']:.1f}%")
        print(f"Total Execution Time:  {summary['total_execution_time']:.2f}s")
        print(f"Average Time per Test: {summary['average_execution_time']:.2f}s")
        print("="*70)
        print()
        
        # Generate reports
        print("Generating reports...")
        report_gen = ReportGenerator(test_results)
        
        html_report = report_gen.generate_html_report()
        print(f"HTML Report: {html_report}")
        
        pdf_report = report_gen.generate_pdf_report()
        print(f"PDF Report:  {pdf_report}")
        
        print()
        print("Test execution completed successfully!")
        
        return 0 if summary['failed'] == 0 else 1
        
    except KeyboardInterrupt:
        print("\n\nTest execution interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        print(f"\nError: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())