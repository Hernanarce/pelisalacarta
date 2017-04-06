# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# pelisalacarta
# modulo para AutoPlay de pelisalacarta
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
# ------------------------------------------------------------

from core import channeltools
from core import filetools
from core import config
from core import logger
from core.item import Item
from platformcode import platformtools


__channel__ = "autoplay"


def context():
    _context = ""
    '''
    configuración para mostrar la configuracion, actualmente sólo se permite en xbmc
    '''
    if config.is_xbmc():
        _context = [{"title": "Configurar AutoPlay",
                     "action": "autoplay_config",
                     "channel": "autoplay"}]
    return _context


context = context()


def autoplay_config(item):
    logger.info()

    logger.debug(item.from_channel)
    return platformtools.show_channel_settings(channelpath=filetools.join(config.get_runtime_path(), "channels",
                                                                          item.from_channel))


def show_option(channel, itemlist):
    logger.info()
    plot_autoplay = 'AutoPlay permite auto reproducir los enlaces directamente, basándose en la configuracion de tus ' \
                    'servidores y calidades preferidas. '
    itemlist.append(
        Item(channel=__channel__, title="[COLOR yellow]Configurar AutoPlay[/COLOR]", action="autoplay_config",
             thumbnail='https://s7.postimg.org/ff7ssxed7/autoplay.png',
             fanart='https://s7.postimg.org/ff7ssxed7/autoplay.png', plot=plot_autoplay, from_channel=channel))
    return itemlist


def start(itemlist, item):

    logger.info()

    if not config.is_xbmc():
        platformtools.dialog_notification('AutoPlay ERROR', 'Sólo disponible para XBMC/Kodi')
        return itemlist

    url_list_valid = []
    autoplay_list = []
    favorite_servers = []
    favorite_quality = []

    # Guarda la accion del usuario
    user_config_setting = config.get_setting("default_action")
    # Habilita la accion reproducir en calidad alta si el servidor devuelve más de una calidad p.e. gdrive
    config.set_setting("default_action", "2")
    # logger.debug(str(config.get_setting("default_action")))

    platformtools.dialog_notification('AutoPlay Activo', '', sound=False)

    # Obtenemos si tenemos configuración personalizada
    autoplay_settings = config.get_setting("autoplay_settings", item.channel)

    if autoplay_settings:
        # Ordena los enlaces por la prioridad Servidor/Calidad la lista de favoritos 
        favorite_priority = config.get_setting("priority", item.channel)
    else:
        # Si no está activa la personalización, la prioridad se fija en calidad
        favorite_priority = 2

    # Obtiene las listas servidores, calidades e idiomas disponibles esde el xml del canal
    settings_list, actual_settings = channeltools.get_channel_controls_settings(item.channel)

    server_found = False
    quality_found = False

    server_list = []
    quality_list = []
    for setting in settings_list:
        for id_setting, name_setting in setting.items():

            if name_setting == 'server_1':
                # se obtiene los distintos servidores
                # TODO esto hay que revisarlo con la actualización de servertools
                server_list = setting['lvalues']
                server_found = True

            elif name_setting == 'quality_1':
                # se obtiene las distintas calidades
                # TODO esto hay que revisarlo ya que si el canal devuelve calidades se debe hacer en filtertools
                quality_list = setting['lvalues']
                quality_found = True

                if server_found and quality_found:
                    break

        if server_found and quality_found:
            break

    # Se guardan los textos de cada servidor y calidad en listas p.e. favorite_servers = ['openload', 'streamcloud']
    for num in range(1, 4):
        logger.debug('server_list: %s ' % server_list[config.get_setting("server_%s" % num, item.channel)])
        logger.debug('config_get_settings: %s ' % config.get_setting("server_%s" % num, item.channel))
        favorite_servers.append(server_list[config.get_setting("server_%s" % num, item.channel)])
        favorite_quality.append(quality_list[config.get_setting("quality_%s" % num, item.channel)])

    logger.debug (str(favorite_servers))



    # Se filtran los enlaces de itemlist y que se correspondan con los valores de autoplay
    for item in itemlist:
        # Se crea la lista para configuracion personalizada
        if autoplay_settings:

            # si el servidor no se encuentra en la lista de favoritos o la url no es correcta, avanzamos en el bucle
            if item.server not in favorite_servers or item.url in url_list_valid:
                continue
            else:
                url_list_valid.append(item.url)
                is_quality_valid = True

                # si item tiene propiedad quality se obtiene su valor y si está dentro de los favoritos, se valida
                if hasattr(item, 'quality'):
                    if item.quality in favorite_quality:
                        is_quality_valid = True
                    else:
                        is_quality_valid = False

                # la calidad es correcta, tanto si está dentro de los valores permitidos, como si no existe,
                # ya que si no existe el valor no se puede filtrar por él.
                if is_quality_valid:
                    autoplay_list.append(
                        [favorite_servers.index(item.server), item, favorite_quality.index(item.quality), item.quality,
                         item.server])

        else:
            is_quality_valid = True
            if hasattr(item, 'quality'):
                if item.quality in quality_list:
                    is_quality_valid = True
                else:
                    is_quality_valid = False

            # TODO esto hay que revisarlo, no me quedo del todo conforme, aquí filtra por los servidores que existan
            # en el xml y no debería ser así, debería obtener cualquiera es decir la siguiente linea comentada...
            # if is_quality_valid:
            if is_quality_valid and item.server in server_list:
                autoplay_list.append(
                    [server_list.index(item.server), item, quality_list.index(item.quality), item.quality, item.server])

    # Se ordena la lista solo por calidad
    if favorite_priority == 2:
        autoplay_list.sort(key=lambda priority: priority[2])

    # Se ordena la lista solo por servidor
    elif favorite_priority == 1:
        autoplay_list.sort(key=lambda priority: priority[0])

    # Se ordena la lista por servidor y calidad
    elif favorite_priority == 0:
        autoplay_list.sort(key=lambda priority: priority[2])
        ordered_list = sorted(autoplay_list,
                              key=lambda priority: priority[0])
        autoplay_list = ordered_list

        # logger.debug('autoplay_list: '+str(autoplay_list)+' favorite priority: '+str(favorite_priority))

    # Si hay elementos en la lista de autoplay se intenta reproducir cada elemento, hasta encontrar uno funcional
    # o fallen todos
    if autoplay_list:
        import xbmc
        played = False
        # Si se esta reproduciendo algo detiene la reproduccion
        if xbmc.Player().isPlaying():
            xbmc.Player().stop()
        for indice in autoplay_list:
            if not xbmc.Player().isPlaying() and not played:
                videoitem = indice[1]
                lang = " "
                if hasattr(item, 'language') and item.language != "":
                    lang = " '%s' " % item.language

                platformtools.dialog_notification("AutoPlay iniciado en:",
                                                  "%s%s%s" % (videoitem.server.upper(), lang, indice[3].upper()),
                                                  sound=False)

                # Intenta reproducir los enlaces
                # Si el canal tiene metodo play propio lo utiliza
                channel = __import__('channels.%s' % item.channel, None, None, ["channels.%s" % item.channel])
                if hasattr(channel, 'play'):
                    logger.debug('usando play interno')
                    resolved_item = getattr(channel, 'play')(videoitem)
                    videoitem = resolved_item[0]
                # si no directamente reproduce
                logger.debug('usando play externo')
                platformtools.play_video(videoitem)

                try:
                    xbmc.Player().getTotalTime()
                    played = True
                    break
                except:  # TODO evitar el informe de que el conector fallo o el video no se encuentra
                    logger.debug(str(len(autoplay_list)))
    else:
        platformtools.dialog_notification('AutoPlay No Fue Posible', 'No Hubo Coincidencias')

    # devuelve la lista de enlaces para la eleccion manual
    config.set_setting("default_action", user_config_setting)
    # logger.debug(str(config.get_setting("default_action")))
    return itemlist
