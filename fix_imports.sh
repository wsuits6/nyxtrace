#!/bin/bash
cd "$(dirname "$0")" || exit

# Fix ALL modules - replace relative imports
for file in modules/*.py; do
    if grep -q "from ..core" "$file"; then
        echo "Fixing $file..."
        sed -i 's|from ..core|from core|g' "$file"
        sed -i 's|from ..modules|from modules|g' "$file"
    fi
done

# Fix core files too
for file in core/*.py; do
    if grep -q "from .." "$file"; then
        echo "Fixing $file..."
        sed -i 's|from ..core|from core|g' "$file"
        sed -i 's|from ..modules|from modules|g' "$file"
    fi
done

echo "✅ ALL IMPORTS FIXED"
