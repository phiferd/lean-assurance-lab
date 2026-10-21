target/release/nanoda_bin config.json < "$IN"
raw=$?
printf "%s\n" "$raw" > "$RAW_STATUS"
case "$raw" in 
  0) exit 0 ;;
  2) exit 2 ;;
  *) exit 1 ;;
esac
