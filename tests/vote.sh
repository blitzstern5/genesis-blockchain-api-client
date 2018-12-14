qs_dir="$HOME/quick-start"
qs_bin="$qs_dir/manage.sh"

keys=$(sudo $qs_bin priv-keys | sed -E 's/([0-9]+): (.*)$/APLA_NODE\1_OWNER_PRIV_KEY=\2/' | tr -d '\r' | tr '\n' ' ')

key_ids=$(sudo $qs_bin key-ids | sed -E 's/([0-9]+): (.*)$/APLA_NODE\1_OWNER_KEY_ID=\2/' | tr -d '\r' | tr '\n' ' ')

pub_keys=$(sudo $qs_bin pub-keys | sed -E 's/([0-9]+): (.*)$/APLA_NODE\1_OWNER_PUB_KEY=\2/' | tr -d '\r' | tr '\n' ' ')

api_urls=""
i=1
for api_url in $($qs_bin api-urls); do
    [ -n "$api_urls" ] && api_urls="$api_urls "
    api_urls="${api_urls}APLA_NODE${i}_API_URL=$api_url"
    i="$(expr $i + 1)"
done

str="$api_urls $keys $key_ids $pub_keys LOG_LEVEL=error nosetests -s ./backend/at20180928/develop/test_calls.py"
eval $str
