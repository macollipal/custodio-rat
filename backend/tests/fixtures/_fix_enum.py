"""Fix script: replace 'borrador' literals with CAST for enum compatibility."""
import re

fp = r'C:\Users\chelo\Desktop\RAT_opencode\backend\tests\fixtures\insert_44_rats.py'

with open(fp, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace 'borrador', with CAST('borrador' AS estadorat),
content = content.replace("'borrador',", "CAST('borrador' AS estadorat),")
# Replace 'borrador') with CAST('borrador' AS estadorat))
content = content.replace("'borrador')", "CAST('borrador' AS estadorat))")

with open(fp, 'w', encoding='utf-8') as f:
    f.write(content)

# Count
n1 = content.count("CAST('borrador' AS estadorat),")
n2 = content.count("CAST('borrador' AS estadorat))")
print(f"Reemplazos: {n1} con coma, {n2} con paren")