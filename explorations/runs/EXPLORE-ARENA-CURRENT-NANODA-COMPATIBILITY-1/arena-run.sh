target/release/nanoda_bin config.json < "$IN"
case $? in 
  0) exit 0 ;;
  2) exit 2 ;;
  *) exit 1 ;;
esac
