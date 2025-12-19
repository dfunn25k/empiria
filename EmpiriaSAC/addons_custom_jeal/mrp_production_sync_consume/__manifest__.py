# -*- coding: utf-8 -*-
{
    "name": "Sincronización Consumo de Producción",
    "summary": "Añade la capacidad de sincronizar y forzar el consumo de materiales en órdenes de producción.",
    "description": """
        Este módulo extiende la gestión de órdenes de producción (MRP) para permitir una sincronización
        más granular del consumo de materiales. Introduce un campo para visualizar el estado de consumo
        de los componentes y un botón para forzar el registro del consumo, descontando el stock del almacén.

        Características principales:
        - Muestra el estado de cada componente en la lista de materiales de la orden de producción.
        - Permite forzar el consumo de materiales directamente desde la orden de producción.
        - Facilita la corrección y el ajuste del consumo de materiales en escenarios específicos.
    """,
    "author": "JEAL",
    "website": "https://www.jeal.com",
    "category": "Manufacturing",
    "version": "16.0.0.2.5",
    "license": "AGPL-3",
    "depends": [
        "mrp",
    ],
    "data": [
        "views/mrp_production_inh_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
