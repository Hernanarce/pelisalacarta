# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# pelisalacarta 4
# Copyright 2015 tvalacarta@gmail.com
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#
# Distributed under the terms of GNU General Public License v3 (GPLv3)
# http://www.gnu.org/licenses/gpl-3.0.html
# ------------------------------------------------------------
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
# --------------------------------------------------------------------------------
# filter_tools - se encarga de filtrar resultados
# ------------------------------------------------------------

from core import config
from core import filetools
from core import logger
from core.item import Item
from platformcode import platformtools

TAG_TVSHOW_FILTER = "TVSHOW_FILTER"
TAG_NAME = "name"
TAG_ACTIVE = "active"
TAG_LANGUAGE = "language"
TAG_QUALITY_NOT_ALLOWED = "quality_not_allowed"

COLOR = {"parent_item": "yellow", "error": "red", "striped_even_active": "blue",
         "striped_even_inactive": "0xff00bfff", "striped_odd_active": "0xff008000",
         "striped_odd_inactive": "0xff00fa9a", "selected": "blue"
         }

filter_global = None

__channel__ = "filtertools"
# TODO echar un ojo a https://pyformat.info/, se puede formatear el estilo y hacer referencias directamente a elementos


class ResultFilter:
    def __init__(self, dict_filter):
        self.active = dict_filter[TAG_ACTIVE]
        self.language = dict_filter[TAG_LANGUAGE]
        self.quality_not_allowed = dict_filter[TAG_QUALITY_NOT_ALLOWED]

    def __str__(self):
        return "{active: '%s', language: '%s', quality_not_allowed: '%s'}" % \
               (self.active, self.language, self.quality_not_allowed)


class Filter:

    def __init__(self, item, global_filter_lang_id):
        self.result = None
        self.__get_data(item, global_filter_lang_id)

    def __get_data(self, item, global_filter_lang_id):

        dict_filtered_shows = filetools.get_node_from_data_json(item.channel, TAG_TVSHOW_FILTER)
        tvshow = item.show.lower().strip()

        global_filter_language = config.get_setting(global_filter_lang_id, item.channel)

        if tvshow in dict_filtered_shows.keys():

            self.result = ResultFilter({TAG_ACTIVE: dict_filtered_shows[tvshow][TAG_ACTIVE],
                                        TAG_LANGUAGE: dict_filtered_shows[tvshow][TAG_LANGUAGE],
                                        TAG_QUALITY_NOT_ALLOWED: dict_filtered_shows[tvshow][TAG_QUALITY_NOT_ALLOWED]})

        # opcion general "no filtrar"
        elif global_filter_language != 0:
            from core import channeltools
            list_controls, dict_settings = channeltools.get_channel_controls_settings(item.channel)

            for control in list_controls:
                if control["id"] == global_filter_lang_id:

                    try:
                        language = control["lvalues"][global_filter_language]
                        # logger.debug("language %s" % language)
                    except:
                        logger.error("No se ha encontrado el valor asociado al codigo '%s': %s" %
                                     (global_filter_lang_id, global_filter_language))
                        break

                    self.result = ResultFilter({TAG_ACTIVE: True, TAG_LANGUAGE: language, TAG_QUALITY_NOT_ALLOWED: []})
                    break

    def __str__(self):
        return "{'%s'}" % self.result


def access():
    """
    Devuelve si se puede usar o no filtertools
    """
    allow = False
    if config.is_xbmc() or config.get_platform() == "mediaserver":
        allow = True

    return allow


def context(item, list_language=None, list_quality=None, exist=False):
    """
    Para xbmc/kodi y mediaserver ya que pueden mostrar el menú contextual, se añade un menu para configuración
    la opción de filtro, sólo si es para series.
    Dependiendo del lugar y si existe filtro se añadirán más opciones a mostrar.
    El contexto -solo se muestra para series-.

    @param item: elemento para obtener la información y ver que contexto añadir
    @type item: item
    param list_language: listado de idiomas posibles
    @type list_language: list[str]
    @param list_quality: listado de calidades posibles
    @type list_quality: list[str]
    @param exist: si existe el filtro
    @type exist: bool
    @return: lista de opciones a mostrar en el menú contextual
    @rtype: list
    """
    _context = []
    # TODO hay que mirar si el contexto ya tiene valores para no eliminar las anteriores opciones

    if access() and item.show != "":
        dict_data = {"title": "FILTRO: Configurar", "action": "config_item", "channel": "filtertools"}
        if list_language:
            dict_data["list_language"] = list_language
        if list_quality:
            dict_data["list_quality"] = list_quality

        _context.append(dict_data)

        if item.action == "play":
            if not exist:
                _context.append({"title": "FILTRO: Añadir '%s'" % item.language, "action": "save_from_context",
                                 "channel": "filtertools", "from_channel": item.channel})
            else:
                _context.append({"title": "FILTRO: Borrar '%s'" % item.language, "action": "delete_from_context",
                                 "channel": "filtertools", "from_channel": item.channel})

    return _context


def show_option(itemlist, channel, list_language, list_quality):

    if access():
        itemlist.append(Item(channel=__channel__, title="[COLOR {0}]Configurar filtro para series...[/COLOR]".
                             format(COLOR.get("parent_item", "auto")), action="load", list_language=list_language,
                             list_quality=list_quality, from_channel=channel))

    return itemlist


def load(item):
    return mainlist(channel=item.from_channel, list_language=item.list_language, list_quality=item.list_quality)


def check_conditions(_filter, list_item, item, list_language, list_quality, quality_count=0, language_count=0):

    is_language_valid = True
    if _filter.language:

        # viene de episodios
        if isinstance(item.language, list):
            if _filter.language in item.language:
                language_count += 1
            else:
                is_language_valid = False
        # viene de findvideos
        else:
            if item.language.lower() == _filter.language.lower():
                language_count += 1
            else:
                is_language_valid = False

        is_quality_valid = True
        quality = ""

        if _filter.quality_not_allowed:
            # if hasattr(item, 'quality'): # esta validación no hace falta por que SIEMPRE se devuelve el atributo vacío
            if item.quality.lower() not in _filter.quality_not_allowed:
                quality = item.quality.lower()
                quality_count += 1
            else:
                is_quality_valid = False

        if is_language_valid and is_quality_valid:
            item.list_language = list_language
            if list_quality:
                item.list_quality = list_quality
            item.context = context(item, exist=True)
            list_item.append(item)
            # logger.debug("{0} | context: {1}".format(item.title, item.context))
            # logger.debug(" -Enlace añadido")

        logger.debug(" idioma valido?: {0}, item.language: {1}, filter.language: {2}"
                     .format(is_language_valid, item.language, _filter.language))
        logger.debug(" calidad valida?: {0}, item.quality: {1}, filter.quality_not_allowed: {2}"
                     .format(is_quality_valid, quality, _filter.quality_not_allowed))

    return list_item, quality_count, language_count


def get_link(list_item, item, list_language, list_quality=None, global_filter_lang_id="filter_languages"):
    """
    Devuelve una lista de enlaces, si el item está filtrado correctamente se agrega a la lista recibida.

    @param list_item: lista de enlaces
    @type list_item: list[Item]
    @param item: elemento a filtrar
    @type item: Item
    @param list_language: listado de idiomas posibles
    @type list_language: list[str]
    @param list_quality: listado de calidades posibles
    @type list_quality: list[str]
    @param global_filter_lang_id: id de la variable de filtrado por idioma que está en settings
    @type global_filter_lang_id: str
    @return: lista de Item
    @rtype: list[Item]
    """
    logger.info()
    logger.debug("total de items : {0}".format(len(list_item)))

    global filter_global

    if not filter_global:
        filter_global = Filter(item, global_filter_lang_id).result
    logger.debug("filter: '{0}' datos: '{1}'".format(item.show, filter_global))

    if filter_global and filter_global.active:
        list_item, quality_count, language_count = \
            check_conditions(filter_global, list_item, item, list_language, list_quality)
    else:
        item.context = context(item)
        list_item.append(item)

    return list_item


def get_links(list_item, item, list_language, list_quality=None, global_filter_lang_id="filter_languages"):
    """
    Devuelve una lista de enlaces filtrados.

    @param list_item: lista de enlaces
    @type list_item: list[Item]
    @param item: elemento a filtrar
    @type item: item
    @param list_language: listado de idiomas posibles
    @type list_language: list[str]
    @param list_quality: listado de calidades posibles
    @type list_quality: list[str]
    @param global_filter_lang_id: id de la variable de filtrado por idioma que está en settings
    @type global_filter_lang_id: str
    @return: lista de Item
    @rtype: list[Item]
    """
    logger.info()

    # si list_item está vacío volvemos, no se añade validación de plataforma para que Plex pueda hacer filtro global
    if len(list_item) == 0:
        return list_item

    logger.debug("total de items : {0}".format(len(list_item)))

    new_itemlist = []
    quality_count = 0
    language_count = 0

    _filter = Filter(item, global_filter_lang_id).result
    logger.debug("filter: '{0}' datos: '{1}'".format(item.show, _filter))

    if _filter and _filter.active:

        for item in list_item:
            new_itemlist, quality_count, language_count = check_conditions(_filter, new_itemlist, item, list_language,
                                                                           list_quality, quality_count, language_count)

        logger.info("ITEMS FILTRADOS: {0}/{1}, idioma[{2}]: {3}, calidad_no_permitida{4}: {5}"
                    .format(len(new_itemlist), len(list_item), _filter.language, language_count,
                            _filter.quality_not_allowed, quality_count))

        if len(new_itemlist) == 0:
            list_item_all = []
            for i in list_item:
                list_item_all.append(i.tourl())

            _context = [{"title": "FILTRO: Borrar '%s'" % _filter.language, "action": "delete_from_context",
                         "channel": "filtertools", "to_channel": "seriesdanko"}]

            if _filter.quality_not_allowed:
                msg_quality_not_allowed = " y calidad distinta {0}".format(_filter.quality_not_allowed)
            else:
                msg_quality_not_allowed = ""

            new_itemlist.append(Item(channel=__channel__, action="no_filter", list_item_all=list_item_all,
                                     show=item.show,
                                     title="[COLOR {0}]No hay elementos con idioma '{1}'{2}, pulsa para mostrar "
                                           "sin filtro[/COLOR]"
                                     .format(COLOR.get("error", "auto"), _filter.language, msg_quality_not_allowed),
                                     context=_context))

    else:
        for item in list_item:
            item.list_language = list_language
            if list_quality:
                item.list_quality = list_quality
            item.context = context(item)
        new_itemlist = list_item

    return new_itemlist


def no_filter(item):
    """
    Muestra los enlaces sin filtrar

    @param item: item
    @type item: Item
    @return: lista de enlaces
    @rtype: list[Item]
    """
    logger.info()

    itemlist = []
    for i in item.list_item_all:
        itemlist.append(Item().fromurl(i))

    return itemlist


def mainlist(channel, list_language, list_quality):
    """
    Muestra una lista de las series filtradas

    @param channel: nombre del canal para obtener las series filtradas
    @type channel: str
    @param list_language: lista de idiomas del canal
    @type list_language: list[str]
    @param list_quality: lista de calidades del canal
    @type list_quality: list[str]
    @return: lista de Item
    @rtype: list[Item]
    """
    logger.info()
    itemlist = []
    dict_series = filetools.get_node_from_data_json(channel, TAG_TVSHOW_FILTER)

    idx = 0
    for tvshow in sorted(dict_series):

        if idx % 2 == 0:
            if dict_series[tvshow][TAG_ACTIVE]:
                tag_color = COLOR.get("striped_even_active", "auto")
            else:
                tag_color = COLOR.get("striped_even_inactive", "auto")
        else:
            if dict_series[tvshow][TAG_ACTIVE]:
                tag_color = COLOR.get("striped_odd_active", "auto")
            else:
                tag_color = COLOR.get("striped_odd_inactive", "auto")

        idx += 1
        name = dict_series.get(tvshow, {}).get(TAG_NAME, tvshow)
        activo = " (desactivado)"
        if dict_series[tvshow][TAG_ACTIVE]:
            activo = ""
        title = "Configurar [COLOR {0}][{1}][/COLOR]{2}".format(tag_color, name, activo)

        itemlist.append(Item(channel=__channel__, action="config_item", title=title, show=name,
                             list_language=list_language, list_quality=list_quality, from_channel=channel))

    if len(itemlist) == 0:
        itemlist.append(Item(channel=channel, action="mainlist", title="No existen filtros, busca una serie y "
                                                                       "pulsa en menú contextual 'FILTRO: Configurar'"))

    return itemlist


def config_item(item):
    """
    muestra una serie filtrada para su configuración

    @param item: item
    @type item: Item
    """
    logger.info()
    logger.info("item {0}".format(item.tostring()))

    # OBTENEMOS LOS DATOS DEL JSON
    dict_series = filetools.get_node_from_data_json(item.from_channel, TAG_TVSHOW_FILTER)

    tvshow = item.show.lower().strip()

    lang_selected = dict_series.get(tvshow, {}).get(TAG_LANGUAGE, 'Español')
    list_quality = dict_series.get(tvshow, {}).get(TAG_QUALITY_NOT_ALLOWED, "")
    # logger.info("lang selected {}".format(lang_selected))
    # logger.info("list quality {}".format(list_quality))

    active = True
    custom_button = {'visible': False}
    allow_option = False
    if item.show.lower().strip() in dict_series:
        allow_option = True
        active = dict_series.get(item.show.lower().strip(), {}).get(TAG_ACTIVE, False)
        custom_button = {'label': 'Borrar', 'function': 'delete', 'visible': True, 'close': True}

    list_controls = []

    if allow_option:
        active_control = {
            "id": "active",
            "type": "bool",
            "label": "¿Activar/Desactivar filtro?",
            "color": "",
            "default": active,
            "enabled": allow_option,
            "visible": allow_option,
        }
        list_controls.append(active_control)

    logger.debug('lang_selected: '+lang_selected)
    logger.debug('list_language: ' + str(item.list_language))
    language_option = {
        "id": "language",
        "type": "list",
        "label": "Idioma",
        "color": "0xFFee66CC",
        "default": item.list_language.index(lang_selected),
        "enabled": True,
        "visible": True,
        "lvalues": item.list_language
    }
    list_controls.append(language_option)

    if item.list_quality:
        list_controls_calidad = [
            {
                "id": "textoCalidad",
                "type": "label",
                "label": "Calidad NO permitida",
                "color": "0xffC6C384",
                "enabled": True,
                "visible": True,
            },
        ]
        for element in sorted(item.list_quality, key=str.lower):
            list_controls_calidad.append({
                "id": element,
                "type": "bool",
                "label": element,
                "default": (False, True)[element.lower() in list_quality],
                "enabled": True,
                "visible": True,
            })

        # concatenamos list_controls con list_controls_calidad
        list_controls.extend(list_controls_calidad)

    title = "Filtrado de enlaces para: [COLOR {0}]{1}[/COLOR]".format(COLOR.get("selected", "auto"), item.show)

    platformtools.show_channel_settings(list_controls=list_controls, callback='save', item=item,
                                        caption=title, custom_button=custom_button)


def delete(item):
    logger.info()

    if item:
        dict_series = filetools.get_node_from_data_json(item.from_channel, TAG_TVSHOW_FILTER)
        tvshow = item.show.strip().lower()

        heading = "¿Está seguro que desea eliminar el filtro?"
        line1 = "Pulse 'Si' para eliminar el filtro de [COLOR {0}]{1}[/COLOR], pulse 'No' o cierre la ventana para " \
                "no hacer nada.".format(COLOR.get("selected", "auto"), item.show.strip())

        if platformtools.dialog_yesno(heading, line1) == 1:
            lang_selected = dict_series.get(tvshow, {}).get(TAG_LANGUAGE, "")
            dict_series.pop(tvshow, None)

            fname, json_data = filetools.update_json_data(dict_series, item.from_channel, TAG_TVSHOW_FILTER)
            result = filetools.write(fname, json_data)

            sound = False
            if result:
                message = "FILTRO ELIMINADO"
            else:
                message = "Error al guardar en disco"
                sound = True

            heading = "{0} [{1}]".format(item.show.strip(), lang_selected)
            platformtools.dialog_notification(heading, message, sound=sound)

            if item.action in ["findvideos", "play"]:
                platformtools.itemlist_refresh()


def save(item, dict_data_saved):
    """
    Guarda los valores configurados en la ventana

    @param item: item
    @type item: Item
    @param dict_data_saved: diccionario con los datos salvados
    @type dict_data_saved: dict
    """
    logger.info()

    if item and dict_data_saved:
        logger.debug('item: {0}\ndatos: {1}'.format(item.tostring(), dict_data_saved))

        if item.from_channel == "biblioteca":
            item.from_channel = item.contentChannel
        dict_series = filetools.get_node_from_data_json(item.from_channel, TAG_TVSHOW_FILTER)
        tvshow = item.show.strip().lower()

        logger.info("Se actualiza los datos")

        list_quality = []
        for _id, value in dict_data_saved.items():
            if _id in item.list_quality and value:
                    list_quality.append(_id.lower())

        lang_selected = item.list_language[dict_data_saved[TAG_LANGUAGE]]
        dict_filter = {TAG_NAME: item.show, TAG_ACTIVE: dict_data_saved.get(TAG_ACTIVE, True),
                       TAG_LANGUAGE: lang_selected, TAG_QUALITY_NOT_ALLOWED: list_quality}
        dict_series[tvshow] = dict_filter

        fname, json_data = filetools.update_json_data(dict_series, item.from_channel, TAG_TVSHOW_FILTER)
        result = filetools.write(fname, json_data)

        sound = False
        if result:
            message = "FILTRO GUARDADO"
        else:
            message = "Error al guardar en disco"
            sound = True

        heading = "{0} [{1}]".format(item.show.strip(), lang_selected)
        platformtools.dialog_notification(heading, message, sound=sound)

        if item.from_action in ["findvideos", "play"]:
            platformtools.itemlist_refresh()


def save_from_context(item):
    """
    Salva el filtro a través del menú contextual

    @param item: item
    @type item: item
    """
    logger.info()

    dict_series = filetools.get_node_from_data_json(item.from_channel, TAG_TVSHOW_FILTER)
    tvshow = item.show.strip().lower()

    dict_filter = {TAG_NAME: item.show, TAG_ACTIVE: True, TAG_LANGUAGE: item.language, TAG_QUALITY_NOT_ALLOWED: []}
    dict_series[tvshow] = dict_filter

    fname, json_data = filetools.update_json_data(dict_series, item.from_channel, TAG_TVSHOW_FILTER)
    result = filetools.write(fname, json_data)

    sound = False
    if result:
        message = "FILTRO GUARDADO"
    else:
        message = "Error al guardar en disco"
        sound = True

    heading = "{0} [{1}]".format(item.show.strip(), item.language)
    platformtools.dialog_notification(heading, message, sound=sound)

    if item.from_action in ["findvideos", "play"]:
        platformtools.itemlist_refresh()


def delete_from_context(item):
    """
    Elimina el filtro a través del menú contextual

    @param item: item
    @type item: item
    """
    logger.info()

    # venimos desde get_links y no se ha obtenido ningún resultado, en menu contextual y damos a borrar
    if item.to_channel != "":
        item.from_channel = item.to_channel

    dict_series = filetools.get_node_from_data_json(item.from_channel, TAG_TVSHOW_FILTER)
    tvshow = item.show.strip().lower()

    lang_selected = dict_series.get(tvshow, {}).get(TAG_LANGUAGE, "")
    dict_series.pop(tvshow, None)

    fname, json_data = filetools.update_json_data(dict_series, item.from_channel, TAG_TVSHOW_FILTER)
    result = filetools.write(fname, json_data)

    sound = False
    if result:
        message = "FILTRO ELIMINADO"
    else:
        message = "Error al guardar en disco"
        sound = True

    heading = "{0} [{1}]".format(item.show.strip(), lang_selected)
    platformtools.dialog_notification(heading, message, sound=sound)

    if item.from_action in ["findvideos", "play", "no_filter"]:  # 'no_filter' es el mismo caso que L#601
        platformtools.itemlist_refresh()
