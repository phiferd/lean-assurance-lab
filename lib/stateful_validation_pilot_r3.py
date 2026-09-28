"""R3 replaces the nonexistent Options.setNat call with supported typed Options.set."""
from lib import stateful_validation_pilot_r2
from lib import stateful_validation_pilot as prior

prior.HARNESS = prior.BASE/'StatefulHarnessR3.lean'
prior.TOOLING = [*prior.TOOLING, str(prior.HARNESS), 'lib/stateful_validation_pilot_r3.py',
                 'scripts/stateful-validation-pilot-r3','scripts/prepare-stateful-r3',
                 'tests/test_stateful_validation_pilot_r3.py',str(prior.BASE/'tooling-options.lean')]
main = prior.main
