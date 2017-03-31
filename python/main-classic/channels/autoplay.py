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


# Requerido para AutoPlay

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
    plot_autoplay = 'AutoPlay permite auto reproducir los enlaces directamente, basandose en la configuracion de tus ' \
                    'servidores y calidades preferidas. '
    itemlist.append(
        Item(channel=__channel__, title="[COLOR yellow]Configurar AutoPlay[/COLOR]", action="autoplay_config",
             thumbnail='https://s7.postimg.org/ff7ssxed7/autoplay.png',
             fanart='https://s7.postimg.org/ff7ssxed7/autoplay.png', plot=plot_autoplay, from_channel=channel))
    return itemlist


def start(itemlist, item):

    import xbmc

    logger.info()

    channel = __import__('channels.%s' % item.channel, None, None, ["channels.%s" %item.channel])



    if not config.is_xbmc():
        platformtools.dialog_notification('AutoPlay ERROR', 'Sólo disponible para XBMC/Kodi')
        return itemlist

    duplicados = []
    autoplay_list = []
    favorite_servers = []
    favorite_quality = []

    # Guarda la accion del usuario
    user_config_setting = config.get_setting("default_action")
    # Habilita la accion reproducir en calidad alta
    config.set_setting("default_action", "2")
    logger.debug(str(config.get_setting("default_action")))

    platformtools.dialog_notification('AutoPlay Activo', '', sound=False)

    # Verifica el estado de la configuracion automatica ###
    auto_config = config.get_setting("auto_config", item.channel)

    if auto_config:
        # Si esta activa la auto-configuracion la prioridad se fija en calidad
        favorite_priority = 2

    else:
        # Ordena los enlaces por la prioridad Servidor/Calidad la lista de favoritos 
        favorite_priority = config.get_setting("priority", item.channel)

        # Obtiene las listas servidores, calidades e idiomas disponibles esde el xml del canal ###
    settings_list, actual_settings = channeltools.get_channel_controls_settings(item.channel)

    server_found = False
    lang_found = False
    quality_found = False
    for setting in settings_list:
        for id_setting, name_setting in setting.items():

            if name_setting == 'server_1':
                server_list= setting['lvalues']
                server_found = True

            elif name_setting == 'lang':
                lang_list= setting['lvalues']
                lang_found = True

            elif name_setting == 'quality_1':
                quality_list= setting['lvalues']
                quality_found = True

                if server_found and lang_found and quality_found:
                    break

        if server_found and lang_found and quality_found:
            break

    # Se obtienen desde el archivo de configuracion los servidores y calidades favoritos ###
    for num in range(1, 4):
        logger.debug('num: '+str(num))
        logger.debug('server_list: '+str(server_list[config.get_setting("server_" + str(num), item.channel)]))
        logger.debug('config_get_settings: '+str(config.get_setting("server_" + str(num), item.channel)))
        favorite_servers.append(server_list[config.get_setting("server_" + str(num), item.channel)])
        favorite_quality.append(quality_list[config.get_setting("quality_" + str(num), item.channel)])

    # Se obtiene el idioma favorito
    lang = lang_list[(config.get_setting("lang", item.channel))]

    # Se crea la lista de enlaces que cumplen los requisitos de los favoritos y no esten repetidos ###
    for item in itemlist:
        # Se crea la lista para configuracion automatica
        if auto_config:
            for quality in quality_list:
                if item.quality == quality and item.language == lang and item.server in server_list:
                    autoplay_list.append(
                        [server_list.index(item.server), item, quality_list.index(quality), item.quality, item.server])

        else:
            # Se crea la lista de enlaces que cumplen los requisitos de los favoritos ###
            for favorite in favorite_servers:
                if item.server == favorite and item.language == lang and item.quality in favorite_quality \
                        and item.url not in duplicados:
                    autoplay_list.append(
                        [favorite_servers.index(favorite), item, favorite_quality.index(item.quality), item.quality,
                         item.server])
                    duplicados.append(item.url)

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
        played = False
        # Si se esta reproduciendo algo detiene la reproduccion
        if xbmc.Player().isPlaying():
            xbmc.Player().stop()
        for indice in autoplay_list:
            if not xbmc.Player().isPlaying() and not played:
                videoitem = indice[1]
                platformtools.dialog_notification('AutoPlay iniciado en:',
                                                  videoitem.server.upper() + ' ' + lang + ' ' + str(indice[3]).upper(),
                                                  sound=False)

                # Esto es solo estetico, si tiene infolabels utiliza el thumbnail desde ahi durante la reproduccion

                # Intenta reproducir los enlaces

                # Si el canal tiene metodo play propio lo utiliza
                if hasattr(channel, 'play'):
                    logger.debug('usando play interno')
                    resolved_item = getattr(channel,'play')(videoitem)
                    videoitem = resolved_item[0]
                # si no directamente reproduce
                logger.debug('usando play externo')
                platformtools.play_video(videoitem)

                try:
                    total_time = xbmc.Player().getTotalTime()
                    played = True

                except:  # TODO evitar el informe de que el conector fallo o el video no se encuentra
                    logger.debug(str(len(autoplay_list)))
    else:
        info_dialog = platformtools.dialog_notification('AutoPlay No Fue Posible', 'No Hubo Coincidencias')

    ### devuelve la lista de enlaces para la eleccion manual ###
    config.set_setting("default_action", user_config_setting)
    logger.debug(str(config.get_setting("default_action")))
    return itemlist
