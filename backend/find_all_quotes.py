with open('pse_service.py', encoding='utf-8') as f:
    for i, line in enumerate(f):
        if '"""' in line:
            print(f"Line {i+1}: {line.strip()}")
