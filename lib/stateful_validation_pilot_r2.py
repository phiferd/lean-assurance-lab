"""R2 selects a syntax-correct generic harness, preserving all R1 bindings."""
from lib import stateful_validation_pilot as prior

prior.HARNESS = prior.BASE/'StatefulHarnessR2.lean'
prior.TOOLING = [*prior.TOOLING, str(prior.HARNESS), 'lib/stateful_validation_pilot_r2.py',
                 'scripts/stateful-validation-pilot-r2','tests/test_stateful_validation_pilot_r2.py']
main = prior.main
