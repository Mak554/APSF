with open('pse_service.py', encoding='utf-8') as f:
    lines = f.readlines()
for i in range(380, len(lines)):
    if '"""' in lines[i] and i != 381:  # ignore the opening quote on 382 (index 381)
        print(f"Line {i+1}: {repr(lines[i])}")
        break
