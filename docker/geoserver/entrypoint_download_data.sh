#!/bin/bash
set -euo pipefail
set -x  # Debug: muestra cada comando ejecutado

# Variables por defecto si no están definidas
GEOSERVER_DATA_DIR=${GEOSERVER_DATA_DIR:-/geoserver_data/data}
FORCE_REINIT=${FORCE_REINIT:-false}
INVOKE_LOG_STDOUT=${INVOKE_LOG_STDOUT:-TRUE}

# Cargar variables de entorno si existe .bashrc
if [ -f /root/.bashrc ] && [[ $- == *i* ]]; then
  source /root/.bashrc
fi

echo "Entrypoint iniciado"
echo "GEOSERVER_DATA_DIR: $GEOSERVER_DATA_DIR"
echo "FORCE_REINIT: $FORCE_REINIT"

# Mostrar entorno y archivos para asegurar que tasks.py está presente
echo "PWD: $(pwd)"
ls -la

# Verificar que el archivo tasks.py existe
if [ ! -f "tasks.py" ]; then
    echo "ERROR: No se encontró el archivo tasks.py en $(pwd)"
    exit 1
fi

# Mostrar las tareas disponibles para confirmar que download_data está registrada
echo "Verificando tareas disponibles..."
invoke --list || {
    echo "ERROR: No se pudieron listar las tareas con invoke."
    exit 1
}

# Función para ejecutar invoke
invoke_wrapper () {
    if [[ "${INVOKE_LOG_STDOUT,,}" == "true" ]]; then
        /usr/local/bin/invoke "$@"
    else
        /usr/local/bin/invoke "$@" > /tmp/invoke.log 2>&1
    fi
    echo "$@ tasks done"
}

# Ejecutar tarea si corresponde
if [[ "${FORCE_REINIT,,}" == "true" ]] || [[ ! -e "${GEOSERVER_DATA_DIR}/geoserver_init.lock" ]]; then
    echo "Reinicialización forzada o archivo de bloqueo no encontrado."
    echo "Ejecutando tarea download_data..."
    if invoke_wrapper download_data; then
        echo "Tarea download_data ejecutada con éxito."
    else
        echo "ERROR: Falló la ejecución de download_data. Mostrando logs:"
        cat /tmp/invoke.log || echo "No hay log disponible."
        exit 1
    fi
else
    echo "Los datos ya están inicializados y el archivo geoserver_init.lock está presente."
fi

echo "Entrypoint completado."
