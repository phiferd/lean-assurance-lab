# Preparation tooling invocation R1

The first producer test command used `python3 -m unittest tests.test_resource_envelope_producer -v`. It exited 1 with `ModuleNotFoundError: No module named 'tests.test_resource_envelope_producer'` because this repository's `tests` directory is not a Python package. No selected term or observer was involved. The corrected command, `python3 -m unittest discover -s tests -p test_resource_envelope_producer.py -v`, passed five synthetic-only tests. This is an invocation repair, not a scientific negative.
