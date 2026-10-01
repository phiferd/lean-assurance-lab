#!/usr/bin/env bash
# Functional-test observation only. Run --install before the action, --check afterwards.
set -euo pipefail
case "${1:-}" in
  --install)
    trace_dir="$(mktemp -d "${RUNNER_TEMP:?}/nanoda-tools.XXXXXX")"
    export NANODA_TOOL_TRACE_DIR="$trace_dir"
    export NANODA_OBSERVED_ELAN="$(command -v elan)"
    export NANODA_OBSERVED_GIT="$(command -v git)"
    export NANODA_OBSERVED_CARGO="$(command -v cargo || true)"
    export NANODA_OBSERVED_EXPORTER="$(elan which leanexport)"
    export NANODA_OBSERVED_CHECKER="$(elan which nanoda_bin)"
    test -x "$NANODA_OBSERVED_EXPORTER"
    test -x "$NANODA_OBSERVED_CHECKER"
    mkdir "$trace_dir/bin"
    : > "$trace_dir/invocations"
    cat > "$trace_dir/bin/tool" <<'WRAPPER'
#!/usr/bin/env bash
set -euo pipefail
record() { printf '%s\n' "$1" >> "${NANODA_TOOL_TRACE_DIR:?}/invocations"; }
case "${0##*/}" in
  elan)
    if [ "${1:-}" = which ] && [ "${2:-}" = leanexport ]; then
      "$NANODA_OBSERVED_ELAN" "$@" >/dev/null
      printf '%s\n' "$NANODA_TOOL_TRACE_DIR/bin/leanexport"
    elif [ "${1:-}" = which ] && [ "${2:-}" = nanoda_bin ]; then
      "$NANODA_OBSERVED_ELAN" "$@" >/dev/null
      printf '%s\n' "$NANODA_TOOL_TRACE_DIR/bin/nanoda_bin"
    else
      exec "$NANODA_OBSERVED_ELAN" "$@"
    fi ;;
  leanexport) record bundled-exporter; exec "$NANODA_OBSERVED_EXPORTER" "$@" ;;
  nanoda_bin) record bundled-checker; exec "$NANODA_OBSERVED_CHECKER" "$@" ;;
  git)
    if [ "${1:-}" = clone ]; then
      for arg in "$@"; do
        case "$arg" in
          https://github.com/leanprover/lean4export.git|https://github.com/ammkrn/nanoda_lib.git)
            record forbidden-source-clone
            if [ "${NANODA_TEST_ALLOW_FALLBACK:-false}" != true ]; then
              echo 'Unexpected nanoda source clone in bundled-binaries test' >&2; exit 37
            fi ;;
        esac
      done
    fi
    exec "$NANODA_OBSERVED_GIT" "$@" ;;
  cargo)
    if [ "${1:-}" = build ]; then
      record forbidden-source-build
      if [ "${NANODA_TEST_ALLOW_FALLBACK:-false}" != true ]; then
        echo 'Unexpected Cargo build in bundled-binaries test' >&2; exit 37
      fi
    fi
    test -n "$NANODA_OBSERVED_CARGO"
    exec "$NANODA_OBSERVED_CARGO" "$@" ;;
  *) exit 98 ;;
esac
WRAPPER
    chmod +x "$trace_dir/bin/tool"
    for tool in elan git cargo leanexport nanoda_bin; do
      cp "$trace_dir/bin/tool" "$trace_dir/bin/$tool"
    done
    for variable in NANODA_TOOL_TRACE_DIR NANODA_OBSERVED_ELAN NANODA_OBSERVED_GIT NANODA_OBSERVED_CARGO NANODA_OBSERVED_EXPORTER NANODA_OBSERVED_CHECKER; do
      printf '%s=%s\n' "$variable" "${!variable}" >> "${GITHUB_ENV:?}"
    done
    printf '%s\n' "$trace_dir/bin" >> "${GITHUB_PATH:?}"
    ;;
  --check)
    trace="${NANODA_TOOL_TRACE_DIR:?}/invocations"
    grep -qx bundled-exporter "$trace"
    grep -qx bundled-checker "$trace"
    if grep -q '^forbidden-source-' "$trace"; then
      echo 'The source fallback ran despite the bundled-binaries expectation' >&2; exit 1
    fi
    echo 'Both bundled tools ran; no source clone or build was observed'
    ;;
  *) echo 'Use --install or --check' >&2; exit 2 ;;
esac
