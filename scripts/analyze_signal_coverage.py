import json

# Load coverage data
with open('coverage-fixed.json', 'r') as f:
    data = json.load(f)

# Get Signal model data
signal_data = data['files']['backend\\models\\signal.py']

print("Signal Model Coverage Analysis")
print("=" * 40)
print(f"Overall: {signal_data['summary']['covered_lines']}/{signal_data['summary']['num_statements']} = {signal_data['summary']['percent_covered']:.1f}%")
print()

print("Missing lines:", signal_data['missing_lines'])
print()

print("Functions with missing coverage:")
for name, func in signal_data['functions'].items():
    if func['missing_lines']:
        print(f"  {name}: {func['missing_lines']}")
print()

print("Classes with missing coverage:")
for name, cls in signal_data['classes'].items():
    if cls['missing_lines']:
        print(f"  {name}: {cls['missing_lines']}") 