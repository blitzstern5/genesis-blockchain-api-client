this_dir="$(cd "$(dirname "$0")" && pwd)"
proj_dir="$(cd $this_dir/../../../../.. && pwd)"
python_bin="python3"

qs_dir="$HOME/quick-start"
qs_bin="$qs_dir/manage.sh"

echo "Restoring DB ..."
db_dumps="$(cd "$qs_dir" && find . -mindepth 1 -maxdepth 1 -name 'db-dumps-*' | tail -1)"
[ -z "$db_dumps" ] && echo "DB dumps not found" && exit 1
(cd "$qs_dir" && ./manage.sh frest $db_dumps)

priv_key="$($qs_bin priv-key 1)"

api_url="$($qs_bin api-url 1)"

key_ids=$($qs_bin key-ids | sed -E 's/([0-9]+): (.*)$/--node-key-id=\2/' | tr -d '\r' | tr '\n' ' ')

api_urls=$($qs_bin int-api-urls | sed -E 's/([0-9]+): (.*)$/--node-api-url=\2/' | tr -d '\r' | tr '\n' ' ')

tcp_addrs=$($qs_bin int-tcp-addrs | sed -E 's/([0-9]+): (.*)$/--node-tcp-addr=\2/' | tr -d '\r' | tr '\n' ' ')

pub_keys=$($qs_bin pub-keys | sed -E 's/([0-9]+): (.*)$/--node-pub-key=\2/' | tr -d '\r' | tr '\n' ' ')

str="(cd $proj_dir && PYTHONPATH=$proj_dir $python_bin $this_dir/update_full_nodes.py --call-priv-key=$priv_key --call-api-url=$api_url $key_ids $api_urls $tcp_addrs $pub_keys)"
eval "$str"
