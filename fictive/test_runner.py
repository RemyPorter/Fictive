"""
Helper functions to execute a test script against a game.
"""

from .states import Machine, Statebag
from .parser import parse
from .test_parser import parse_test
from .loader import load_test
from typing import Dict, List
from pathlib import Path

def build_test_results(loaded_test, results):
    """Construct the output string for a test run"""
    result = []
    for k,r in results.items():
        result.append(f"Test: {k}")
        if all(r):
            result.append("---- All Tests Pass")
        else:
            for i,b in enumerate(r):
                if not b:
                    result.append(f"---- Failed({i}): {loaded_test[k]['steps'][i]}")
    return "\n".join(result)

def print_test_results(loaded_test, results):
    """Print the output string"""
    print(build_test_results(loaded_test, results))
                
def run_tests(test:dict, machine:Machine, statebag:Statebag)->Dict[str, List[bool]]:
    """Run a series of tests against a state machine"""
    results:Dict[str, List[bool]] = {}
    for name in test.keys():
        if name == "failed_test":
            breakpoint()
        parsed = parse_test(name, test[name])
        results[name] = parsed.run(machine, statebag)
    return results

def test_main(loaded:list, root: Path):
    """
    Handle the loading and executions of our test scripts, print
    the results.
    """
    machine,statebag,title = parse(loaded)
    for l in loaded[::-1]: # search for a test entry, backwards because we favor putting it an the end in parsing
        if "tests" in l:
            for t in l["tests"]:
                loaded_test = load_test(root / Path(t))
                res = run_tests(loaded_test,machine,statebag)
                print_test_results(loaded_test, res)


