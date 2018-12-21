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
contracts_dir="$(cd $this_dir/../fixtures/contracts && pwd)"
path="$contracts_dir/empty.json"

str="(cd $proj_dir && PYTHONPATH=$proj_dir $python_bin $this_dir/import_dapp_from_file.py --priv-key=$priv_key --api-url=$api_url --path=$path)"
eval "$str"
