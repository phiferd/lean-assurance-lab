# Queue-test wrapper invocation correction

The first shell command expanded the `test_research_queue*.py` argument before
the validation wrapper ran. Zsh reported `no matches found`; no test process,
wrapper record, fixture, or research launch was created. The corrected command
quotes the same unittest discovery pattern and retains label `04-queue-tests`.
