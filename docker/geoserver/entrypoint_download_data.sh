#!/bin/bash

set -e

# Cargar variables de entorno
source /root/.bashrc

INVOKE_LOG_STDOUT=${INVOKE_LOG_STDOUT:-TRUE}
invoke () {
    if [ $INVOKE_LOG_STDOUT = 'true' ] || [ $INVOKE_LOG_STDOUT = 'True' ]
    then
        /usr/local/bin/invoke $@
    else
        /usr/local/bin/invoke $@ > /usr/src/geonode/invoke.log 2>&1
    fi
    echo "$@ tasks done"
}

# Verificar si se debe forzar la reinicialización o si no existe el archivo de bloqueo
if [ "${FORCE_REINIT}" = "true" ] || [ "${FORCE_REINIT}" = "True" ] || [ ! -e "${GEOSERVER_DATA_DIR}/geoserver_init.lock" ]; then
    echo "Forzando reinicialización o no se encontró geoserver_init.lock."
    echo "Ejecutando invoke download_data"
    sh -c "invoke download_data"
else
    echo "Los datos ya están inicializados y geoserver_init.lock está presente."
fi

# Finalizar el script
echo "Ejecución del entrypoint completada."