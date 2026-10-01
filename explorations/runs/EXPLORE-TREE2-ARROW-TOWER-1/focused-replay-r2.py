from pathlib import Path
import sys,unittest
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'tests'))
from lib.survivor_cache_historical_v2 import portable_validation as cache
from lib.portable_evidence_replay import portable_validation as evidence
from lib.resource_envelope_legacy_portability import historical_attempt_scope
from lib.resource_test_portability import portable_suite
names=['test_arena_let_regression_erratum','test_survivor_cache_historical',
 'test_survivor_fvar_reachability_historical','test_survivor_thread_config_reachability_historical',
 'test_survivor_universe_diff_historical','test_survivor_universe_equivalence_historical','test_exploration']
suite=portable_suite(unittest.defaultTestLoader.loadTestsFromNames(names))
with cache(),evidence(),historical_attempt_scope():
 result=unittest.TextTestRunner(verbosity=2).run(suite)
sys.exit(0 if result.wasSuccessful() else 1)
