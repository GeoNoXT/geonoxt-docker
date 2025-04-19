# -*- coding: utf-8 -*-
#########################################################################
#
# Copyright (C) 2023 OSGeo
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#########################################################################
import os
import logging
import time
import base64
import requests
from pathlib import Path
from invoke import task
import pytz
from subprocess import run, CalledProcessError

logger = logging.getLogger(__name__)


@task
def configure_geoserver(ctx):
    _configure_geoserver_password()
    _initialized(ctx)


def _configure_geoserver_password():
    print(
        "************************configuring Geoserver credentials*****************************"
    )
    GEOSERVER_LB_PORT = os.getenv("GEOSERVER_LB_PORT", 8080)
    GEOSERVER_ADMIN_USER = os.getenv("GEOSERVER_ADMIN_USER", "admin")
    GEOSERVER_ADMIN_PASSWORD = os.getenv("GEOSERVER_ADMIN_PASSWORD", "geoserver")
    GEOSERVER_FACTORY_PASSWORD = os.getenv("GEOSERVER_FACTORY_PASSWORD", "geoserver")
    GEOSERVER_LB_HOST_IP = os.getenv("GEOSERVER_LB_HOST_IP", "localhost")
    GEOSERVER_HTTP_PROTOCOL = os.getenv("GEOSERVER_HTTP_PROTOCOL", "http")
    geoserver_rest_baseurl = f"{GEOSERVER_HTTP_PROTOCOL}://{GEOSERVER_LB_HOST_IP}:{GEOSERVER_LB_PORT}/geoserver/rest"
    basic_auth_credentials = base64.b64encode(
        f"{GEOSERVER_ADMIN_USER}:{GEOSERVER_FACTORY_PASSWORD}".encode()
    ).decode()
    headers = {
        "Content-type": "application/xml",
        "Accept": "application/xml",
        "Authorization": f"Basic {basic_auth_credentials}",
    }
    data = f"""<?xml version="1.0" encoding="UTF-8"?>
    <userPassword>
        <newPassword>{GEOSERVER_ADMIN_PASSWORD}</newPassword>
    </userPassword>"""

    for _cnt in range(1, 29):
        try:
            response = requests.put(
                f"{geoserver_rest_baseurl}/security/self/password",
                data=data,
                headers=headers,
            )
            print(f"Response Code: {response.status_code}")
            if response.status_code == 200:
                print("GeoServer admin password updated SUCCESSFULLY!")
            else:
                logger.warning(
                    f"WARNING: GeoServer admin password *NOT* updated: code [{response.status_code}]"
                )
            break
        except Exception:
            print(f"...waiting for Geoserver to pop-up...{_cnt}")
            time.sleep(2)


def _initialized(ctx):
    print("**************************init file********************************")
    GEOSERVER_DATA_DIR = os.getenv("GEOSERVER_DATA_DIR", "/geoserver_data/data/")
    TIME_ZONE = os.getenv("TIME_ZONE", "UTC")
    geoserver_init_lock = Path(GEOSERVER_DATA_DIR) / "geoserver_init.lock"
    # ctx.run(f"date > {geoserver_init_lock}")

    # Verifica si la zona horaria es válida usando pytz
    try:
        # Intentar obtener la zona horaria
        pytz.timezone(TIME_ZONE)
        print(f"Zona horaria válida: {TIME_ZONE}")
    except pytz.UnknownTimeZoneError:
        # Si la zona horaria no es válida, caerá en UTC
        print(f"Zona horaria no válida: {TIME_ZONE}. Usando UTC por defecto.")
        TIME_ZONE = "UTC"

    # Ejecuta el comando con la zona horaria validada
    try:
        ctx.run(f"TZ={TIME_ZONE} date > {geoserver_init_lock}")
    except CalledProcessError as e:
        print(f"Error al ejecutar el comando: {e}")
