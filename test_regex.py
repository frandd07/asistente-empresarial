import re

# Simular el contenido del historial con dos clientes
contenido = """# Historial de Clientes

---

## Presupuestado - Manolo el Loco (10/12/2025 16:17)

**Cliente:** Manolo el Loco
**NIF/CIF:** 65789876Q
**Email:** No especificado
**Dirección:** calle solera 44

**Detalles del trabajo:**
- Área: 333.0 m²
- Tipo de trabajo: fachada
- Tipo de pintura: plástica
- Zona: Interior

**Total con IVA:** €6215.29
**Estado actual:** Presupuestado

---

## Presupuestado - Pepe Tornado (10/12/2025 16:30)

**Cliente:** Pepe Tornado
**NIF/CIF:** 76598765Q
**Email:** No especificado
**Dirección:** Calle iu 33

**Detalles del trabajo:**
- Área: 765.0 m²
- Tipo de trabajo: fachada
- Tipo de pintura: plástica
- Zona: Interior

**Total con IVA:** €14152.8
**Estado actual:** Presupuestado

---
"""

# Probar el patrón para Manolo
nombre1 = "Manolo el Loco"
nif1 = "65789876Q"
patron1 = rf"## .*? - {re.escape(nombre1)} \(.*?\).*?\*\*NIF/CIF:\*\* {re.escape(nif1)}.*?---"
match1 = re.search(patron1, contenido, re.DOTALL)

# Probar el patrón para Pepe
nombre2 = "Pepe Tornado"
nif2 = "76598765Q"
patron2 = rf"## .*? - {re.escape(nombre2)} \(.*?\).*?\*\*NIF/CIF:\*\* {re.escape(nif2)}.*?---"
match2 = re.search(patron2, contenido, re.DOTALL)

print("=" * 50)
print("PRUEBA DE PATRONES REGEX")
print("=" * 50)

print(f"\n1. Buscando a {nombre1} (NIF: {nif1}):")
if match1:
    print(f"   ✅ Encontrado")
    print(f"   Texto capturado ({len(match1.group(0))} caracteres):")
    print(f"   {match1.group(0)[:100]}...")
else:
    print(f"   ❌ NO encontrado")

print(f"\n2. Buscando a {nombre2} (NIF: {nif2}):")
if match2:
    print(f"   ✅ Encontrado")
    print(f"   Texto capturado ({len(match2.group(0))} caracteres):")
    print(f"   {match2.group(0)[:100]}...")
else:
    print(f"   ❌ NO encontrado")

# Probar si ambos patrones coinciden con TODO el contenido
print("\n" + "=" * 50)
print("VERIFICACIÓN DE DUPLICADOS")
print("=" * 50)

all_matches1 = list(re.finditer(patron1, contenido, re.DOTALL))
all_matches2 = list(re.finditer(patron2, contenido, re.DOTALL))

print(f"\nCoincidencias para {nombre1}: {len(all_matches1)}")
print(f"Coincidencias para {nombre2}: {len(all_matches2)}")
