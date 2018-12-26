this_dir="$(cd "$(dirname "$0")" && pwd)"
proj_dir="$(cd $this_dir/../../../../.. && pwd)"
python_bin="python3"

qs_dir="$HOME/quick-start"
qs_bin="$qs_dir/manage.sh"

#echo "Restoring DB ..."
#db_dumps="$(cd "$qs_dir" && find . -mindepth 1 -maxdepth 1 -name 'db-dumps-*' | tail -1)"
#[ -z "$db_dumps" ] && echo "DB dumps not found" && exit 1
#(cd "$qs_dir" && ./manage.sh frest $db_dumps)

priv_key="$($qs_bin priv-key 1)"

api_url="$($qs_bin api-url 1)"

pub_keys=$($qs_bin pub-keys |  tail -n +2 | sed -E 's/([0-9]+): (.*)$/--pub-key=\2/' | tr -d '\r' | tr '\n' ' ')

amounts=$($qs_bin key-ids |  tail -n +2 | sed -E 's/([0-9]+): (.*)$/--amount=1000000000000000000000/' | tr -d '\r' | tr '\n' ' ')

#echo "pub_keys: $pub_keys"
#echo "amounts: $amounts"

str="(cd $proj_dir && PYTHONPATH=$proj_dir $python_bin $this_dir/new_users.py --priv-key=$priv_key --api-url=$api_url $key_ids $pub_keys $amounts)"
#echo "str: $str"
eval "$str"
