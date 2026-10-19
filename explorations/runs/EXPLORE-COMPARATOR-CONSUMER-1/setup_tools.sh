#!/bin/bash
set -euo pipefail
mkdir -p /opt/lean /opt/bin
echo '47bf4bbd78f70c2e9670598ab7124d92b6efb7330ff33e5fbb4030f6fd72e4e4  /inputs/comparator-screen-lean-amd64.tar.zst' | sha256sum -c -
tar --zstd -xf /inputs/comparator-screen-lean-amd64.tar.zst -C /opt/lean --strip-components=1
echo '6ada66a06669e8994e174a7271af2db636308e55a0d6ec896cc7d326b46727f6  /inputs/comparator-screen-landrun' | sha256sum -c -
cp /inputs/comparator-screen-landrun /opt/bin/landrun
chmod 755 /opt/bin/landrun
export PATH=/opt/lean/bin:/opt/bin:$PATH
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
useradd --create-home --uid 1000 checker
mkdir /work
cp -a /inputs/comparator-screen-workspace/. /work/
chown -R checker:checker /work /opt/comparator/.lake
chmod -R a+rX /opt/lean /opt/nanoda/target/release /opt/bin
