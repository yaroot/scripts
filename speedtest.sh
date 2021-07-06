
BASE_URL=https://mirrors.edge.kernel.org/archlinux/iso/latest


parse_filename() {
    curl -s $BASE_URL/ | grep '.iso"' | head -n1 | perl -lne 'print for /"(.+)"/'
}

main() {
    local fn=`parse_filename`
    local url=$BASE_URL/$fn
    echo "Curling '$url'"
    curl "$url" > /dev/null
}

main
