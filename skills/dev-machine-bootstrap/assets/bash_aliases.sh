#!/usr/bin/env bash

hgrep() {
    if [ $# -ne 2 ]; then
        echo "Usage: hgrep <pattern> <file>"
        return 1
    fi

    local pattern="$1"
    local file_path="$2"
    local output_file="${file_path}.${pattern}.csv"

    if [ ! -f "$file_path" ]; then
        echo "Error: file '$file_path' does not exist"
        return 1
    fi

    if [[ "$file_path" == *.gz ]]; then
        zcat "$file_path" | head -n 1 > "$output_file"
        zgrep "$pattern" "$file_path" >> "$output_file"
    else
        head -n 1 "$file_path" > "$output_file"
        grep "$pattern" "$file_path" >> "$output_file"
    fi

    echo "Output -> $output_file"
}

head_tail() {
    if [ $# -lt 2 ]; then
        echo "Usage: head_tail <n_lines> <csv_file>"
        return 1
    fi
    local n="$1"
    local file="$2"
    local out="${file%.csv}_tail.csv"
    {
        head -n 1 "$file"
        tail -n "$n" "$file"
    } > "$out"
    echo "Output -> $out"
}

head_grep() {
    if [ $# -lt 2 ]; then
        echo "Usage: head_grep <pattern> <csv_file>"
        return 1
    fi
    local pattern="$1"
    local file="$2"
    local out="${file%.csv}_grep.csv"
    {
        head -n 1 "$file"
        grep "$pattern" "$file" | tail -n +2
    } > "$out"
    echo "Output -> $out"
}
