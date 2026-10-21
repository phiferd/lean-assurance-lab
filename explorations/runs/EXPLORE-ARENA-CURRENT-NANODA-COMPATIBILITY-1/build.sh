set -eu
export PATH=/root/.cargo/bin:$PATH
export CARGO_NET_OFFLINE=true
export CARGO_BUILD_JOBS=4
grep -q 'STACK_SIZE: usize = 16_777_216;' src/lib.rs || { echo "STACK_SIZE patch does not apply any more"; exit 1; }
sed -i 's/STACK_SIZE: usize = 16_777_216;/STACK_SIZE: usize = 268_435_456;/' src/lib.rs
cargo build --release --locked
cat > config.json <<__END__
 {
   "use_stdin": true,
   "nat_extension": true,
   "string_extension": true,
   "unpermitted_axiom_hard_error": false,
   "unsafe_permit_all_axioms": true,
   "num_threads": 4
 }
__END__
