#!/bin/bash
set -euo pipefail
# Repair only the final setup step: Ubuntu already occupies UID 1000.
useradd --create-home --uid 1001 checker
mkdir /work
cp -a /inputs/comparator-screen-workspace/. /work/
mkdir -p /work/.lake/packages
cp -a /inputs/comparator-screen-mathlib /work/.lake/packages/mathlib
chown -R checker:checker /work /opt/comparator/.lake
chmod -R a+rX /opt/lean /opt/nanoda/target/release /opt/bin
mkdir /out /opt/lal
chown checker:checker /out
su -s /bin/bash checker -c 'export PATH=/opt/lean/bin:/opt/bin:$PATH; cd /work; MATHLIB_NO_CACHE_ON_UPDATE=1 lake update; lake exe cache get'
