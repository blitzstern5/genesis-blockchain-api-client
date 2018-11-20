qs_dir="$HOME/quick-start"
qs_bin="$qs_dir/manage.sh"
keys=$($qs_bin priv-keys | sed -E 's/([0-9]+): (.*)$/APLA_NODE\1_OWNER_PRIV_KEY=\2/' | tr '\n' ' ')
eval "$keys LOG_LEVEL=error nosetests -s ./backend/at20180928/develop/test_calls.py"
