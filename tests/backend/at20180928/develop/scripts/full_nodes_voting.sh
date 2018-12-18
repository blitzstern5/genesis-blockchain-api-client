this_dir="$(cd "$(dirname "$0")" && pwd)"
proj_dir="$(cd $this_dir/../../../../.. && pwd)"

qs_dir="$HOME/quick-start"
qs_bin="$qs_dir/manage.sh"

echo "Restoring DB ..."
db_dumps="$(cd "$qs_dir" && find . -mindepth 1 -maxdepth 1 -name 'db-dumps-*' | tail -1)"
[ -z "$db_dumps" ] && echo "DB dumps not found" && exit 1
(cd "$qs_dir" && ./manage.sh frest $db_dumps)

num_of_nodes=$($qs_bin key-ids | wc -l | awk '{print $1}')
priv_keys=$($qs_bin priv-keys | sed -E 's/([0-9]+): (.*)$/APLA_NODE\1_OWNER_PRIV_KEY=\2/' | tr -d '\r' | tr '\n' ' ')

key_ids=$($qs_bin key-ids | sed -E 's/([0-9]+): (.*)$/APLA_NODE\1_OWNER_KEY_ID=\2/' | tr -d '\r' | tr '\n' ' ')

pub_keys=$($qs_bin pub-keys | sed -E 's/([0-9]+): (.*)$/APLA_NODE\1_OWNER_PUB_KEY=\2/' | tr -d '\r' | tr '\n' ' ')

int_api_urls=$($qs_bin int-api-urls | sed -E 's/([0-9]+): (.*)$/APLA_NODE\1_INT_API_URL=\2/' | tr -d '\r' | tr '\n' ' ')

api_urls=$($qs_bin api-urls | sed -E 's/([0-9]+): (.*)$/APLA_NODE\1_API_URL=\2/' | tr -d '\r' | tr '\n' ' ')

int_tcp_addrs=$($qs_bin int-tcp-addrs | sed -E 's/([0-9]+): (.*)$/APLA_NODE\1_INT_TCP_ADDR=\2/' | tr -d '\r' | tr '\n' ' ')

#echo "priv_keys: $priv_keys"
#echo "key_ids: $key_ids"
#echo "pub_keys: $pub_keys"
#echo "api_urls: $api_urls"
#echo "int_api_urls: $int_api_urls"
#echo "int_tcp_addrs: $int_tcp_addrs"

str="(cd $proj_dir && PYTHONPATH=$proj_dir NUM_OF_NODES=$num_of_nodes $priv_keys $key_ids $pub_keys $int_api_urls $api_urls $int_tcp_addrs python $this_dir/full_nodes_voting.py)"
echo "$str"
eval "$str"
