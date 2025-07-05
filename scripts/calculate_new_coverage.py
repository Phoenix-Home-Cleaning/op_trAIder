import json

# Load new coverage data
with open('coverage-updated.json', 'r') as f:
    data = json.load(f)

# Define trading files (use backslashes for the new coverage data)
trading_files = [
    'models\\__init__.py',
    'models\\position.py',
    'models\\trade.py', 
    'models\\signal.py',
    'models\\market_data.py'
]

# Calculate coverage
covered = 0
total = 0

print("NEW Trading Logic Coverage Analysis:")
print("=" * 40)

for file in trading_files:
    if file in data['files']:
        file_covered = data['files'][file]['summary']['covered_lines']
        file_total = data['files'][file]['summary']['num_statements']
        file_percent = data['files'][file]['summary']['percent_covered']
        
        print(f"{file}: {file_covered}/{file_total} = {file_percent:.1f}%")
        
        covered += file_covered
        total += file_total
    else:
        print(f"{file}: NOT FOUND")

print("=" * 40)
if total > 0:
    overall_percent = (covered / total) * 100
    print(f"TOTAL TRADING LOGIC: {covered}/{total} = {overall_percent:.2f}%")
    print(f"TARGET: 90%")
    if overall_percent >= 90:
        print(f"✅ TARGET ACHIEVED! (+{overall_percent - 90:.2f} percentage points)")
    else:
        print(f"GAP: {90 - overall_percent:.2f} percentage points")
else:
    print("No trading files found!") 