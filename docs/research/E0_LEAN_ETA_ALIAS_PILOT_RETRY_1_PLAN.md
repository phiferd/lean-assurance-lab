# Lean PR15373 preserved-alias eta recovery

Evidence class: E0

Recover the unchanged four-case pilot after its first attempt was stopped solely by an elapsed-time controller that did not observe Docker-daemon progress. Preserve that attempt and reuse the exact fixture, official runner identity, oracle and 4 GiB scientific-container limit.

The one allowed base-image pull uses an empty task-local Docker config because the host config names `credsStore: desktop` but contains no auth hosts. This avoids reading or unlocking credentials. Observe the pull process tree with commands and CPU time plus read-only vpnkit byte counters, Docker VM disk allocation, relevant daemon-log growth and final image presence. Stop only on a resource/control fault or a sustained absence of pull output and corroborating daemon-side progress; allow demonstrated progress regardless of elapsed time.

If the image arrives, download and verify only the official PR15373 archive with the frozen size and SHA-256, then run only the prepared four cases under `linux/amd64` with a 4 GiB container limit. No additional image, source build, setting change, credential access, unrelated-container action, publication or upstream action is allowed.
