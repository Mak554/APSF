import ast
import json

try:
    with open('pse_service.py', encoding='utf-8') as f:
        src = f.read()
    
    # Check syntax
    ast.parse(src)
    print("Syntax OK")
    
    # Check template keys
    # Simple regex search is too prone to errors, let's just parse the python file and extract the keys
    
    import importlib.util
    import sys
    spec = importlib.util.spec_from_file_location("pse_service", "pse_service.py")
    pse_service = importlib.util.module_from_spec(spec)
    sys.modules["pse_service"] = pse_service
    spec.loader.exec_module(pse_service)
    
    templates = pse_service.TEMPLATES
    print("Templates loaded successfully!")
    print(f"Total templates: {len(templates)}")
    
    for k, v in templates.items():
        print(f" - {k}: {v.get('name')}")
        
except SyntaxError as e:
    print(f"SYNTAX ERROR at line {e.lineno}, offset {e.offset}: {e.text}")
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {str(e)}")
