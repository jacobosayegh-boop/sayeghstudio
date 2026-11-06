#!/usr/bin/env bash
# Copia las salidas del hilo B2 a la bóveda y corre la auditoría.
# Uso (desde la raíz del repo): bash tools/pines_crecimiento/publicar_en_boveda.sh
set -euo pipefail
RAIZ="$(cd "$(dirname "$0")/../.." && pwd)"
BOV="/mnt/project-files/06_Growth_SEO_Copy/pinterest/crecimiento_2026-11-07/"
SAL="$RAIZ/tools/pines_crecimiento/salida"

python3 "$RAIZ/tools/pines_crecimiento/construir.py" csv
python3 "$RAIZ/tools/pines_crecimiento/documentos.py" "$SAL"

mkdir -p "${BOV}imagenes/"
for f in AUDITORIA.md PINES_crecimiento_carga.csv PINES_tableros_nuevos_carga.csv PINES_crecimiento_detalle.csv \
         PINES_crecimiento_copy.md CALENDARIO_30_dias.md CALENDARIO_30_dias.csv; do
  cp "$SAL/$f" "$BOV$f"
done
cp "$SAL/CALENDARIO_pines.csv" "/mnt/project-files/06_Growth_SEO_Copy/pinterest/CALENDARIO_pines.csv"
python3 - "$RAIZ" "$BOV" <<'EOF'
import os, shutil, sys
sys.path.insert(0, os.path.join(sys.argv[1], 'tools', 'pines_crecimiento'))
import contenido as C
for p in C.PINES + C.SEMILLAS:
    src = os.path.join(sys.argv[1], 'assets', 'pinterest', 'crecimiento', p['slug'] + '.jpg')
    shutil.copyfile(src, os.path.join(sys.argv[2], 'imagenes', p['slug'] + '.jpg'))
print('imágenes copiadas:', len(C.PINES + C.SEMILLAS))
EOF
python3 "$RAIZ/tools/pines_crecimiento/auditar.py" "$BOV"
