"""
Master Test Runner for AI Resume Analyzer
Runs all unit tests via unittest discovery and prints a clean status report.
Usage:
python tests/run_all_tests.py
Or:
python -m unittest discover -s tests -v
"""

import os
import sys
import unittest

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)


def run_master_suite():
    print("=" * 68)
    print("       AI RESUME ANALYZER - AUTOMATED MASTER TEST SUITE       ")
    print("=" * 68)
    print("Discovering tests in 'tests' directory...\n")

    loader = unittest.TestLoader()
    suite = loader.discover(start_dir=os.path.join(BASE_DIR, "tests"), pattern="test_*.py")

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" * 68)
    print("                       TEST SUMMARY REPORT                     ")
    print("=" * 68)
    print(f" Total Tests Executed: {result.testsRun}")
    print(f" Total Passed:         {result.testsRun - len(result.failures) - len(result.errors)} [PASS]")
    print(f" Total Failed:         {len(result.failures)} [FAIL]")
    print(f" Total Errors:         {len(result.errors)} [ERROR]")
    print("=" * 68)

    if result.wasSuccessful():
        print(" [PASS] ALL AUTOMATED TESTS PASSED! Application is verified and ready.\n")
        return 0
    else:
        print(" [FAIL] SOME TESTS FAILED. Please review the tracebacks above.\n")
        return 1


if __name__ == "__main__":
    sys.exit(run_master_suite())
