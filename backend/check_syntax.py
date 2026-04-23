import ast
with open('pse_service.py', encoding='utf-8') as f:
    text = f.read()

try:
    ast.parse(text)
    print("Syntax OK")
except SyntaxError as e:
    print("SyntaxError:", e.msg)
    print("Line:", e.lineno)
    print("Offset:", e.offset)
    print("Text:", repr(e.text))
    # Print the 5 lines before the error line
    lines = text.splitlines()
    for i in range(max(0, e.lineno - 5), min(len(lines), e.lineno + 2)):
        prefix = "--> " if i == e.lineno - 1 else "    "
        print(f"{prefix}{i+1}: {repr(lines[i])}")
