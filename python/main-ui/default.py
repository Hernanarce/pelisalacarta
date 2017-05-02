# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta 4
# Copyright 2015 tvalacarta@gmail.com
#
# Distributed under the terms of GNU General Public License v3 (GPLv3)
# http://www.gnu.org/licenses/gpl-3.0.html
#------------------------------------------------------------
# This file is part of pelisalacarta 4.
#
# pelisalacarta 4 is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pelisalacarta 4 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pelisalacarta 4.  If not, see <http://www.gnu.org/licenses/>.
#------------------------------------------------------------

import os

import plugintools
import navigation
from core import updater
from core import config
from core import logger
from core.item import Item

plugintools.application_log_enabled = (plugintools.get_setting("debug")=="true")
plugintools.module_log_enabled = (plugintools.get_setting("debug")=="true")
plugintools.http_debug_log_enabled = (plugintools.get_setting("debug")=="true")

plugintools.log("pelisalacarta.default")

# Check if paths are on a default value, and if directories are created
config.verify_directories_created()

# Check for new updates
if config.get_setting("check_for_plugin_updates") == "true":

    logger.info("pelisalacarta.default Verificar actualizaciones activado")
  
    from core import updater
  
    try:
        new_published_version_tag , number_of_updates = updater.get_available_updates()
        plugintools.log("new_published_version_tag="+repr(new_published_version_tag)+", number_of_updates="+repr(number_of_updates))

        config.set_setting("plugin_updates_available",str(number_of_updates))

        if new_published_version_tag!="":
            import xbmcgui
            yes_pressed = xbmcgui.Dialog().yesno( "Versión "+new_published_version_tag+" disponible" , "¿Quieres instalarla?" )
      
            if yes_pressed:
                item = Item(version=version)
                updater.update(item)
    except:
        import xbmcgui
        advertencia = xbmcgui.Dialog()
        advertencia.ok("No se puede conectar","No ha sido posible comprobar","si hay actualizaciones")
        logger.info("pelisalacarta.default Fallo al verificar la actualización")

else:
    logger.info("pelisalacarta.default Verificar actualizaciones desactivado")

# Get items for main menu
item = Item( channel="navigation", action="mainlist" )
itemlist = navigation.get_next_items( item )

# Open main window
window = navigation.get_window_for_item( item )
window.setParentItem(item)
window.setItemlist(itemlist)
window.doModal()
del window
