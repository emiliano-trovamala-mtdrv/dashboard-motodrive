# ═══════════════════════════════════════════════════════════════════
# SCRIPT PARA ACTUALIZAR DATOS DEL DASHBOARD
# ═══════════════════════════════════════════════════════════════════
#
# INSTRUCCIONES:
# 1. Guarda tu archivo Excel como "AVANCE_DIARIO_REV.xlsx" en esta misma carpeta
# 2. Abre la terminal en VS Code (Ctrl + `)
# 3. Ejecuta: python actualizar_datos.py
# 4. Listo, el archivo datos.py se actualiza automáticamente
#
# ═══════════════════════════════════════════════════════════════════

import pandas as pd
from datetime import datetime

print("=" * 60)
print("🔄 ACTUALIZANDO DATOS DEL DASHBOARD")
print("=" * 60)

# Nombre del archivo Excel (puedes cambiarlo si tu archivo se llama diferente)
ARCHIVO_EXCEL = "AVANCE_DIARIO_REV.xlsx"

try:
    # Leer el Excel
    print(f"\n📂 Leyendo archivo: {ARCHIVO_EXCEL}")
    df = pd.read_excel(ARCHIVO_EXCEL, sheet_name='Avance semanal', header=2)
    
    # Renombrar columnas
    df.columns = ['COL0', 'COL1', 'COL2', 'CLIENT_NUM', 'clientName', 'sucursal', 
                  'asesor', 'zona', 'ESTATUS', 'objRefacc', 'objBgo', 'objAcc', 
                  'objTotal', 'resRefacc', 'pctRefacc', 'resBgo', 'pctBgo', 
                  'resAcc', 'pctAcc', 'resTotal', 'pctTotal', 'pedidos']
    
    # Filtrar filas válidas
    df = df[df['CLIENT_NUM'].notna() & df['CLIENT_NUM'].astype(str).str.startswith('C')].copy()
    
    # Convertir a números
    for col in ['objRefacc', 'objBgo', 'objAcc', 'objTotal', 'resRefacc', 'resBgo', 'resAcc', 'resTotal', 'pedidos', 'zona']:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    print(f"✅ {len(df)} sucursales encontradas")
    print(f"✅ {df['clientName'].nunique()} clientes únicos")
    
    # Generar el archivo datos.py
    print(f"\n📝 Generando archivo datos.py...")
    
    lineas = []
    lineas.append("# ═══════════════════════════════════════════════════════════════════")
    lineas.append("# DATOS DEL DASHBOARD - GENERADO AUTOMÁTICAMENTE")
    lineas.append(f"# Última actualización: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    lineas.append(f"# Total sucursales: {len(df)}")
    lineas.append(f"# Total clientes: {df['clientName'].nunique()}")
    lineas.append("# ═══════════════════════════════════════════════════════════════════")
    lineas.append("")
    lineas.append("DATOS = [")
    
    for _, row in df.iterrows():
        linea = "    {"
        linea += f'"clientName": "{row["clientName"]}", '
        linea += f'"sucursal": "{row["sucursal"]}", '
        linea += f'"asesor": "{row["asesor"]}", '
        linea += f'"zona": {int(row["zona"]) if pd.notna(row["zona"]) else 1}, '
        linea += f'"objRefacc": {row["objRefacc"]:.2f}, '
        linea += f'"objBgo": {row["objBgo"]:.2f}, '
        linea += f'"objTotal": {row["objTotal"]:.2f}, '
        linea += f'"resRefacc": {row["resRefacc"]:.2f}, '
        linea += f'"resBgo": {row["resBgo"]:.2f}, '
        linea += f'"resTotal": {row["resTotal"]:.2f}, '
        linea += f'"pedidos": {row["pedidos"]:.2f}'
        linea += "},"
        lineas.append(linea)
    
    lineas.append("]")
    lineas.append("")
    lineas.append("# Lista de clientes únicos")
    lineas.append(f"CLIENTES = {sorted(df['clientName'].unique().tolist())}")
    
    # Guardar archivo
    with open("datos.py", "w", encoding="utf-8") as f:
        f.write("\n".join(lineas))
    
    print(f"✅ Archivo datos.py generado correctamente")
    
    print("\n" + "=" * 60)
    print("🎉 ¡ACTUALIZACIÓN COMPLETADA!")
    print("=" * 60)
    print("\nPróximos pasos:")
    print("1. Ejecuta: streamlit run dashboard.py")
    print("2. O sube los cambios a GitHub para actualizar en internet")
    print("=" * 60)

except FileNotFoundError:
    print(f"\n❌ ERROR: No se encontró el archivo '{ARCHIVO_EXCEL}'")
    print(f"   Asegúrate de que el archivo esté en la misma carpeta que este script.")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
