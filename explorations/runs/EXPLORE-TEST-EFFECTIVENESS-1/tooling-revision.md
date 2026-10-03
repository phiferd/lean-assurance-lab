# Runner revision after invalid shared-target attempt

The first scientific attempt completed 368 checker invocations, but its four
recorded executable hashes were identical. Cargo had reused one shared target
directory across four task-local source roots with the same package identity.
Consequently, that attempt observed the pristine executable four times and is
scientifically inconclusive.

`run-v2.py` assigns one Cargo target directory to each source root, copies each
executable from that profile-specific directory, and refuses completion unless
all four binary hashes are distinct. It also uses separate v2 raw-output and
summary paths. The source revisions, three patches, selected 90-file compact
corpus, two augmented files, baseline comparison, supervision limits, and
questions are unchanged.
