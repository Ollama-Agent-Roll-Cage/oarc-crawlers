import unittest
import sys
from pathlib import Path

def run_tests():
    """Run all tests in the tests directory."""
    # Add the project root to the path
    project_root = Path(__file__).parent
    sys.path.append(str(project_root))
    
    # Discover and run tests
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('tests', pattern='test_*.py')
    
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)
    
    # Return non-zero exit code if tests failed
    return 0 if result.wasSuccessful() else 1

if __name__ == '__main__':
    sys.exit(run_tests())