#!/bin/bash
set -euo pipefail
export PATH=/opt/lean/bin:/opt/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
mkdir -p /opt/bin /opt/lal /out
echo '365d8c8656c732b14d70e621d972cb733e490621fb5b9c0876376bcf457dbb5d  /inputs/comparator-screen-landrun-arm64' | sha256sum -c -
cp /inputs/comparator-screen-landrun-arm64 /opt/bin/landrun
chmod 755 /opt/bin/landrun
lean --version
landrun --version
cp -a /inputs/comparator-screen-tool /opt/comparator
printf 'leanprover/lean4:v4.34.1\n' > /opt/comparator/lean-toolchain
cd /opt/comparator
lake build comparator lean4export
curl --fail --location https://sh.rustup.rs -o /tmp/rustup.sh
sh /tmp/rustup.sh -y --profile minimal --default-toolchain 1.99.0
export PATH=/root/.cargo/bin:$PATH
rustc --version
cargo --version
cp -a /inputs/comparator-screen-nanoda /opt/nanoda
cd /opt/nanoda
cargo build --release --locked
sha256sum /opt/lean/bin/lean /opt/comparator/.lake/build/bin/comparator /opt/comparator/.lake/packages/lean4export/.lake/build/bin/lean4export /opt/nanoda/target/release/nanoda_bin /opt/bin/landrun
useradd --create-home --uid 1001 checker
chown checker:checker /out
chmod -R a+rX /opt/nanoda/target/release /opt/bin
