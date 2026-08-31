"""

Supports patterns like: for (int i = 0; i < n; i++) {
It converts the header to: for i in range(0, n):
"""
from pysharp.extensions import register_pattern

# pattern groups: 1=var, 2=start, 3=end
register_pattern(
    r'^for\s*\(\s*(?:int|var)\s+([A-Za-z_]\w*)\s*=\s*(\d+)\s*;\s*\1\s*<\s*([A-Za-z_]\w*|\d+)\s*;\s*\1\+\+\s*\)$',
    'for {1} in range({2}, {3}):',
)
