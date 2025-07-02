import json

# Load coverage data
with open('coverage-fixed.json', 'r') as f:
    data = json.load(f)

# Get MarketData model data
market_data = data['files']['backend\\models\\market_data.py']

print("MarketData Model Coverage Analysis")
print("=" * 40)
print(f"Overall: {market_data['summary']['covered_lines']}/{market_data['summary']['num_statements']} = {market_data['summary']['percent_covered']:.1f}%")
print()

print("Missing lines:", market_data['missing_lines'])
print()

print("Functions with missing coverage:")
for name, func in market_data['functions'].items():
    if func['missing_lines']:
        print(f"  {name}: {func['missing_lines']}")
print()

print("Classes with missing coverage:")
for name, cls in market_data['classes'].items():
    if cls['missing_lines']:
        print(f"  {name}: {cls['missing_lines']}") 