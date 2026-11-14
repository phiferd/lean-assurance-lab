# Exact checked-import runtime recovery

**What did we find?** The historical checker binaries were intact, but they
lived in a 15.3 GB writable container layer rather than its nominal base image.
A direct snapshot failed for lack of Docker storage. A selective export retained
the exact Lean runtime, lean4export importer, Nanoda binary and required OS
state in a 3.7 GB ARM64 image. All four pinned hashes matched in a fresh isolated
container. A compressed 851 MiB image archive is retained outside Git.

**Is it interesting?** Yes, operationally. The confirmation no longer depends
on the old running container ID, and a reviewer can recover the exact profile
without rebuilding or silently substituting a newer checker. This says nothing
about checker correctness.

**Does it require more work?** The image must be loaded and its ID and pinned
file hashes verified before every confirmation or replay. Distribution of the
ignored external archive remains an explicit custody step; Git alone does not
contain the 851 MiB payload.

## Bound identity

- Image tag: `lean-assurance-lab/checked-import-runtime:2026-11-14`
- Image ID: `sha256:1a144bf428c8c7dd7ed1df886273b77ca331079cb17ebfb9712e1ea2ea643b73`
- Platform: `linux/arm64`
- Uncompressed image size: `3838283731` bytes
- Archive: `external/runtime-images/checked-import-runtime-2026-11-14.tar.zst`
- Archive size: `892351532` bytes
- Archive SHA-256: `eae9bd60f3dafd5213c58f662d45a2b7591268eb1b6801f37a31556b87ae4f2c`

The archive is an ignored external payload. Preserve or transfer it together
with this record; its absence is a recovery blocker, not permission to change
profiles.

## Recovery and verification

```sh
shasum -a 256 external/runtime-images/checked-import-runtime-2026-11-14.tar.zst
zstd -dc external/runtime-images/checked-import-runtime-2026-11-14.tar.zst | docker load
docker image inspect \
  sha256:1a144bf428c8c7dd7ed1df886273b77ca331079cb17ebfb9712e1ea2ea643b73
docker run --rm --network none --read-only \
  --tmpfs /tmp:rw,noexec,nosuid,size=64m \
  --memory 12g --memory-swap 12g --cpus 4 --pids-limit 512 \
  --security-opt no-new-privileges \
  sha256:1a144bf428c8c7dd7ed1df886273b77ca331079cb17ebfb9712e1ea2ea643b73 \
  sha256sum \
  /opt/lean-fast/bin/lean \
  /opt/nanoda/target/release/nanoda_bin \
  /opt/comparator/.lake/packages/lean4export/.lake/build/lib/lean/Export/Parse.olean \
  /opt/comparator/.lake/packages/lean4export/Export/Parse.lean
```

Expected file hashes are, in that order:

```text
79fb1d26fa5a39385d59fdc48a711a14b0710ca6480271acce99b4d177cea085
5e99b44c8b371ca1aedbc1a609a391ca5ac61b834b14fa60871298affb23d962
c264ea4ad5e30bd90cd03a1b48d944c4a7317e53b483b99c04df8c3a6882f133
1f943b5cc776eece6d528937b976509c8bd57d10bc69a39b1c119bfb6d664286
```

## Construction record

The image was created on 2026-11-14 by exporting container
`580ee65b7ba85f7e16898abdc16f3e5add59caf63a83c03fda765097209b16a4`
and excluding unrelated `/work`, `/out`, older toolchains, language/build
caches, Redis assets and prior staged inputs. The retained root includes
`/opt/lean-fast`, `/opt/comparator/.lake/packages/lean4export`, `/opt/nanoda`,
required OS libraries, and the `checker` user (`uid=1001`, `gid=1001`). The
source container is construction provenance only; invocation and recovery use
the immutable image/archive above.
