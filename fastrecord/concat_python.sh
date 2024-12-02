#!/bin/bash

# Output file
output_file="fastrecord.py"

# Clear or create the output file
> "$output_file"

# Find all Python files recursively, excluding the output file itself
find . -type f -name "*.py" ! -name "$(basename $output_file)" | while read -r file; do
    # Get the relative path
    relative_path="${file#./}"

    # Add a separator and file path as a comment
    echo -e "\n# File: $relative_path\n# $(printf '=%.0s' {1..80})\n" >> "$output_file"

    # Add the content of the file
    cat "$file" >> "$output_file"

    # Add a newline for separation
    echo -e "\n" >> "$output_file"
done

# Make the output file executable
chmod +x "$output_file"

echo "All Python files have been concatenated into $output_file"