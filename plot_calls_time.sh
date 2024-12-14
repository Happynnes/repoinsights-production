#!/bin/bash

dir=$1

if [ -z "$dir" ]; then
    echo "Usage: $0 <path/to/log/file>"
    exit 1
fi

function get_repo_name {
    log_file=$1
    echo $log_file
}

function log_time {
    log_file=$1
    start_time=$(cat "$log_file" | grep "Extracting from GitHub" | grep "DESDE -> None" | awk '{print $1, $2}' | head -n 1)
    end_time=$(cat "$log_file" | grep "Project ENQUEUE to CURADO published" | awk '{print $1, $2}' | tail -n 1)
    
    if [ -z "$start_time" ] || [ -z "$end_time" ]; then
        echo "-1"
        return
    fi

    start_epoch=$(date -d "$start_time" +%s)
    end_epoch=$(date -d "$end_time" +%s)

    total_time=$((end_epoch - start_epoch))
    echo $total_time
}

function count_occurrences {
    log_file=$1
    search_string=$2
    count=$(grep "$search_string" $log_file | wc -l)
    if [ -z "$count" ]; then
        echo "-1"
        return
    fi
    echo $count
}


function create_json {
    repo_name=$1
    total_time=$2
    api_calls=$3
    cache_calls=$4
    total_calls=$((api_calls + cache_calls))
    json_string='{"repo": "'$repo_name'", "time": '$total_time', "calls": '$api_calls', "cache_calls": '$cache_calls', "total_calls": '$total_calls'}'
    echo $json_string
}

result='['
sep=''
for file in $(find $dir -name "*.log" -path "*extract*"); do
    repo_name=$(get_repo_name $file)
    total_time=$(log_time $file)
    if [ "$total_time" -eq "-1" ]; then
        echo "Start or End time not found in $repo_name"
        continue
    fi
    api_calls=$(count_occurrences $file "services.extract_service.extract_module.github_api.github_api:get")
    cache_calls=$(count_occurrences $file "cacheado")
    if [ "$api_calls" -eq "-1" ] || [ "$cache_calls" -eq "-1" ]; then
        echo "No API or cache calls found in $repo_name"
        continue
    fi
    result+=$sep$(create_json "$repo_name" $total_time $api_calls $cache_calls)
    sep=', '
done
result+=']'

echo $result > extract_results.json

