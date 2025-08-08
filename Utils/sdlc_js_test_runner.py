import os
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
import time

from Utils.llm.config import Model

RESULTS_BASE_PATH = Path(os.getenv("RESULTS_REPO_PATH"))


class JSTestRunner:
    """JavaScript/Jest test runner for SDLC experiment results"""

    def __init__(self, experiment_path: str, test_set: Optional[str] = None):
        self.experiment_path = Path(experiment_path)
        self.test_dir = Path(__file__).parent / "sdlc_test"
        self.test_set = test_set
        self.test_results = {}

    def run_tests_for_iteration(self, iteration_name: str, component_code: str) -> Dict[str, Any]:
        """Run Jest tests for a specific iteration"""
        print(f"Testing {iteration_name}...")

        # Copy component code to test environment
        component_file = self.test_dir / "src" / self.test_set / "component.tsx"

        try:
            # Write component code
            with open(component_file, "w") as f:
                f.write(component_code)

            # Determine which test files to run based on iteration (cumulative)
            test_files = self.get_test_files_for_iteration(iteration_name)
            test_path_patterns = [str(Path("src", self.test_set, test_file)) for test_file in test_files]

            # Run Jest tests for all relevant test files (cumulative testing)
            test_pattern = "|".join(test_path_patterns)
            result = subprocess.run(
                ["npm", "test", "--", f"--testPathPattern=({test_pattern})", "--passWithNoTests"],
                cwd=self.test_dir,
                capture_output=True,
                text=True,
                timeout=60,
            )

            # Parse test results
            test_results = self.parse_jest_output(result.stdout, result.stderr, result.returncode)

            # Add iteration info
            test_results["iteration"] = iteration_name
            test_results["test_files_used"] = test_files
            test_results["component_code_length"] = len(component_code)
            test_results["timestamp"] = int(time.time())

            return test_results

        except subprocess.TimeoutExpired:
            return {
                "iteration": iteration_name,
                "success": False,
                "error": "Test execution timeout",
                "tests_passed": 0,
                "tests_total": 0,
                "timestamp": int(time.time()),
            }
        except Exception as e:
            return {
                "iteration": iteration_name,
                "success": False,
                "error": f"Test execution error: {str(e)}",
                "tests_passed": 0,
                "tests_total": 0,
                "timestamp": int(time.time()),
            }
        finally:
            # Clean up component files after test
            self.cleanup_component_files()

    def get_test_files_for_iteration(self, iteration_name: str) -> List[str]:
        """Determine which test files to run based on iteration (cumulative testing)"""
        # Extract iteration number from name like 'iteration_1', 'iteration_2', etc.
        if iteration_name.startswith("iteration_"):
            try:
                iteration_num = int(iteration_name.split("_")[1])
                # Run all test files from 1 up to current iteration number
                test_files = []
                for i in range(1, iteration_num + 1):
                    test_files.append(f"iteration_{i}.test.tsx")
                return test_files

            except (IndexError, ValueError):
                return ["iteration_1.test.tsx"]  # fallback
        else:
            return ["iteration_1.test.tsx"]  # fallback

    def cleanup_component_files(self):
        """Remove component files from test directory"""
        component_file = self.test_dir / "src" / self.test_set / "component.tsx"

        if component_file.exists():
            component_file.unlink()
            print(f"  Cleaned up {component_file.name}")

    def parse_jest_output(self, stdout: str, stderr: str, return_code: int) -> Dict[str, Any]:
        """Parse Jest test output to extract results"""
        results = {
            "success": return_code == 0,
            "tests_passed": 0,
            "tests_total": 0,
            "test_suites_passed": 0,
            "test_suites_total": 0,
            "failed_tests": [],
            "raw_output": stdout,
            "raw_error": stderr,
        }

        # Try to parse JSON output if available
        try:
            # Look for JSON output in test-results.json
            json_file = self.test_dir / "test-results.json"
            if json_file.exists():
                with open(json_file, "r") as f:
                    jest_json = json.load(f)

                results["tests_passed"] = jest_json.get("numPassedTests", 0)
                results["tests_total"] = jest_json.get("numTotalTests", 0)
                results["test_suites_passed"] = jest_json.get("numPassedTestSuites", 0)
                results["test_suites_total"] = jest_json.get("numTotalTestSuites", 0)

                # Extract failed test details
                if "testResults" in jest_json:
                    for test_suite in jest_json["testResults"]:
                        if "assertionResults" in test_suite:
                            for test in test_suite["assertionResults"]:
                                if test["status"] == "failed":
                                    results["failed_tests"].append(
                                        {"title": test.get("title", ""), "message": test.get("failureMessages", [])}
                                    )
        except Exception as e:
            print(f"Could not parse JSON test results: {e}")

        # Fallback: parse text output
        if results["tests_total"] == 0:
            # Look for patterns in stdout
            import re

            # Pattern: "Tests: X failed, Y passed, Z total"
            test_summary = re.search(r"Tests:\s*(?:(\d+) failed,?\s*)?(\d+) passed,?\s*(\d+) total", stdout)
            if test_summary:
                failed = int(test_summary.group(1) or 0)
                passed = int(test_summary.group(2) or 0)
                total = int(test_summary.group(3) or 0)

                results["tests_passed"] = passed
                results["tests_total"] = total

            # Pattern: "Test Suites: X failed, Y passed, Z total"
            suite_summary = re.search(r"Test Suites:\s*(?:(\d+) failed,?\s*)?(\d+) passed,?\s*(\d+) total", stdout)
            if suite_summary:
                results["test_suites_passed"] = int(suite_summary.group(2) or 0)
                results["test_suites_total"] = int(suite_summary.group(3) or 0)

        # Calculate pass rate
        if results["tests_total"] > 0:
            results["pass_rate"] = (results["tests_passed"] / results["tests_total"]) * 100
        else:
            results["pass_rate"] = 0

        return results

    def run_all_tests(self) -> Dict[str, Any]:
        """Run tests on all iterations in the experiment"""
        print(f"Running Jest tests for experiment: {self.experiment_path}")

        # Find all step directories (generated by SDLC experiment)
        step_dirs = sorted([d for d in self.experiment_path.iterdir() if d.is_dir() and d.name.startswith("step_")])

        all_results = {}

        for step_dir in step_dirs:
            step_name = step_dir.name
            component_file = step_dir / "component.tsx"

            if not component_file.exists():
                print(f"Warning: No component.tsx found in {step_name}")
                continue

            # Read component code
            with open(component_file, "r") as f:
                component_code = f.read()

            # Map step_X to iteration_X for test file naming
            step_num = int(step_name.split("_")[1])
            iteration_name = f"iteration_{step_num}"

            # Run tests for this step
            test_result = self.run_tests_for_iteration(iteration_name, component_code)
            test_result["step_name"] = step_name  # Track original step name
            all_results[step_name] = test_result

            # Print summary
            self.print_iteration_summary(step_name, test_result)

        # Test final version if exists
        final_dir = self.experiment_path / "final"
        if final_dir.exists():
            component_file = final_dir / "component.tsx"
            if component_file.exists():
                print(f"\nTesting final version...")
                with open(component_file, "r") as f:
                    component_code = f.read()

                test_result = self.run_tests_for_iteration("final", component_code)
                all_results["final"] = test_result
                self.print_iteration_summary("final", test_result)

        # Generate comprehensive report
        self.generate_comprehensive_report(all_results)

        # Save detailed results
        self.save_test_results(all_results)

        return all_results

    def print_iteration_summary(self, iteration_name: str, results: Dict[str, Any]):
        """Print test summary for an iteration"""
        print(f"  {iteration_name}:")
        print(f"    Tests: {results['tests_passed']}/{results['tests_total']} passed ({results['pass_rate']:.1f}%)")
        print(f"    Status: {'✓ PASSED' if results['success'] else '✗ FAILED'}")

        if results.get("failed_tests"):
            print(f"    Failed tests: {len(results['failed_tests'])}")
            for failed_test in results["failed_tests"][:3]:  # Show first 3
                print(f"      - {failed_test['title']}")

        if results.get("error"):
            print(f"    Error: {results['error']}")

    def generate_comprehensive_report(self, all_results: Dict[str, Any]):
        """Generate comprehensive test report"""
        print(f"\n{'='*70}")
        print("COMPREHENSIVE TEST REPORT")
        print(f"{'='*70}")

        if not all_results:
            print("No test results found.")
            return

        # Overall statistics
        total_tests_run = sum(r.get("tests_total", 0) for r in all_results.values())
        total_tests_passed = sum(r.get("tests_passed", 0) for r in all_results.values())
        overall_pass_rate = (total_tests_passed / total_tests_run * 100) if total_tests_run > 0 else 0

        print(f"Overall Results:")
        print(f"  Total Tests Run: {total_tests_run}")
        print(f"  Total Tests Passed: {total_tests_passed}")
        print(f"  Overall Pass Rate: {overall_pass_rate:.1f}%")

        # Step progression
        steps = [(k, v) for k, v in all_results.items() if k.startswith("step_")]
        steps.sort(key=lambda x: int(x[0].split("_")[1]) if x[0].split("_")[1].isdigit() else 0)

        print(f"\nProgression by Step:")
        for step_name, results in steps:
            pass_rate = results.get("pass_rate", 0)
            status = "✓" if results.get("success", False) else "✗"
            print(f"  {step_name}: {pass_rate:.1f}% {status}")

        # Best and worst steps
        if len(steps) > 1:
            best = max(steps, key=lambda x: x[1].get("pass_rate", 0))
            worst = min(steps, key=lambda x: x[1].get("pass_rate", 0))

            print(f"\nBest Performance: {best[0]} ({best[1].get('pass_rate', 0):.1f}%)")
            print(f"Worst Performance: {worst[0]} ({worst[1].get('pass_rate', 0):.1f}%)")

            if len(steps) >= 2:
                improvement = steps[-1][1].get("pass_rate", 0) - steps[0][1].get("pass_rate", 0)
                print(f"Total Improvement: {improvement:.1f}% points")

        # Common failure patterns
        all_failed_tests = []
        for results in all_results.values():
            all_failed_tests.extend(results.get("failed_tests", []))

        if all_failed_tests:
            print(f"\nMost Common Test Failures:")
            failure_counts = {}
            for failed_test in all_failed_tests:
                title = failed_test["title"]
                failure_counts[title] = failure_counts.get(title, 0) + 1

            for test_name, count in sorted(failure_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"  - {test_name} ({count} times)")

    def save_test_results(self, all_results: Dict[str, Any]):
        """Save detailed test results to file"""
        results_file = self.experiment_path / "jest_test_results.json"

        # Prepare results for JSON serialization
        serializable_results = {}
        for iteration, results in all_results.items():
            serializable_results[iteration] = {**results, "timestamp": results.get("timestamp", int(time.time()))}

        with open(results_file, "w") as f:
            json.dump(serializable_results, f, indent=2, default=str)

        print(f"\nDetailed test results saved to: {results_file}")

        # Also save a summary CSV for easy analysis
        summary_file = self.experiment_path / "test_summary.csv"
        with open(summary_file, "w") as f:
            f.write("step,tests_passed,tests_total,pass_rate,success\n")
            for step, results in all_results.items():
                f.write(
                    f"{step},{results.get('tests_passed', 0)},{results.get('tests_total', 0)},{results.get('pass_rate', 0):.1f},{results.get('success', False)}\n"
                )

        print(f"Summary CSV saved to: {summary_file}")


def main(model):
    """Main function to run Jest tests on SDLC experiment"""

    experiment_path = RESULTS_BASE_PATH / "Output" / model.model_id / "SDLC" / "enhanced_todo_component/1753883589"
    # experiment_path = RESULTS_BASE_PATH / "Output" / model.model_id / "SDLC" / "enhanced_todo_component/1753886605" #sonnet_4

    runner = JSTestRunner(experiment_path, test_set="todo_component")
    results = runner.run_all_tests()

    print(f"\nJest testing completed! Check jest_test_results.json for detailed results.")


if __name__ == "__main__":
    main(Model.GPT41_0414)
    # main(Model.Sonnet_4)
