# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# Canal (MetaSerie) por Hernan_Ar_c
# ------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os, sys

from core import logger
from core import config
from core import scrapertools
from core.item import Item
from core import servertools
from core import httptools

### Requerido para AutoPlay ###
import xbmc
from platformcode import platformtools
from core import channeltools


def mainlist(item):
    logger.info()

    itemlist = []
    
    itemlist.append( item.clone(title="Series", action="todas", url="http://metaserie.com/series-agregadas", thumbnail='https://s32.postimg.org/544rx8n51/series.png', fanart='https://s32.postimg.org/544rx8n51/series.png'))
    
    itemlist.append( item.clone(title="Anime", action="todas", url="http://metaserie.com/animes-agregados",thumbnail='https://s31.postimg.org/lppob54d7/anime.png', fanart='https://s31.postimg.org/lppob54d7/anime.png'))
    
    itemlist.append( item.clone(title="Buscar", action="search", url="http://www.metaserie.com/?s=", thumbnail='https://s31.postimg.org/qose4p13f/Buscar.png', fanart='https://s31.postimg.org/qose4p13f/Buscar.png'))
    
    plot_autoplay='AutoPlay permite auto reproducir los enlaces directamente, basandose en la configuracion de tus servidores y calidades preferidas.'
    itemlist.append(item.clone (title="[COLOR yellow]Configurar AutoPlay[/COLOR]", action="configuracion", thumbnail='https://s7.postimg.org/ff7ssxed7/autoplay.png', fanart='https://s7.postimg.org/ff7ssxed7/autoplay.png', plot = plot_autoplay))
    
    return itemlist

def todas(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    
    patron = '<div class="poster">[^<]'
    patron +='<a href="([^"]+)" title="([^"]+)">[^<]'
    patron +='<div class="poster_efecto"><span>([^<]+)<.*?div>[^<]'
    patron +='<img.*?src="([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)

    for scrapedurl,scrapedtitle,scrapedplot, scrapedthumbnail in matches:
        url = urlparse.urljoin(item.url,scrapedurl)
        title = scrapertools.decodeHtmlentities(scrapedtitle)
        #title = scrapedtitle.replace("&#8217;","'")
        thumbnail = scrapedthumbnail
        plot = scrapedplot
        fanart = 'https://s32.postimg.org/7g50yo39h/metaserie.png'
        itemlist.append( Item(channel=item.channel, action="temporadas" , title=title , url=url, thumbnail=thumbnail, plot=plot, fanart=fanart, contentSerieName=title))
    
    #Paginacion

    patron  = '<li><a class="next page-numbers local-link" href="([^"]+)">&raquo;.*?li>'
    next_page_url = scrapertools.find_single_match(data,'<li><a class="next page-numbers local-link" href="([^"]+)">&raquo;.*?li>')
    if next_page_url!="":
        import inspect
        itemlist.append(
            Item(
                channel = item.channel,
                action = "todas",
                title = ">> Página siguiente",
                url = next_page_url, thumbnail='https://s32.postimg.org/4zppxf5j9/siguiente.png'
            )
        )
    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []
    templist = []
    
    data = httptools.downloadpage(item.url).data
    patron = '<li class=".*?="([^"]+)".*?>([^<]+)</a>'
    matches = re.compile(patron,re.DOTALL).findall(data)

    for scrapedurl,scrapedtitle in matches:
        url = scrapedurl
        contentSeasonNumber = re.findall (r'.*?temporada-([^-]+)-',url)
        title = scrapedtitle
        title = title.replace("&","x");
        thumbnail = item.thumbnail
        plot = item.plot
        fanart = scrapertools.find_single_match(data,'<img src="([^"]+)"/>.*?</a>')
        itemlist.append( Item(channel=item.channel, action= 'episodiosxtemp' , title=title ,fulltitle = item.contentSerieName, url=url, thumbnail=thumbnail, plot=plot, fanart = fanart, contentSerieName=item.contentSerieName, contentSeasonNumber = contentSeasonNumber))
              
    if config.get_library_support() and len(itemlist) > 0:
       itemlist.append(Item(channel=item.channel, title='[COLOR yellow]Añadir esta serie a la biblioteca[/COLOR]', url=item.url,
                             action="add_serie_to_library", extra='episodios', contentSerieName=item.contentSerieName))
    
    return itemlist
    
     

def episodios(item):
    logger.info()
    itemlist = []
    templist = temporadas(item)
    for tempitem in templist:
       itemlist += episodiosxtemp(tempitem) 

    return itemlist
    
     
    

def episodiosxtemp(item):
    logger.info()
    itemlist =[]               
    data = httptools.downloadpage(item.url).data
    patron = '<td><h3 class=".*?href="([^"]+)".*?">([^<]+).*?td>'
    matches = re.compile(patron,re.DOTALL).findall(data)

    for scrapedurl,scrapedtitle in matches:
        url = scrapedurl
        contentEpisodeNumber = re.findall(r'.*?x([^\/]+)\/',url)
        title = scrapedtitle
        title = title.replace ("&#215;","x")
        title = title.replace ("×","x")
        thumbnail = item.thumbnail
        plot = item.plot
        fanart=item.fanart
        itemlist.append( Item(channel=item.channel, action="findvideos" , title=title, fulltitle=item.fulltitle, url=url, thumbnail=item.thumbnail, plot=plot, contentSerieName=item.contentSerieName, contentSeasonNumber = item.contentSeasonNumber, contentEpisodeNumber = contentEpisodeNumber))
    
    return itemlist

def search(item,texto):
    logger.info()
    texto = texto.replace(" ","+")
    item.url = item.url+texto
    itemlist = []
    if texto!='':
             try:
                 data = httptools.downloadpage(item.url).data
                 patron = '<a href="([^\"]+)" rel="bookmark" class="local-link">([^<]+)<.*?'
                 matches = re.compile(patron,re.DOTALL).findall(data)
                 scrapertools.printMatches(matches)
                 for scrapedurl,scrapedtitle in matches:
                     url = scrapedurl
                     title = scrapertools.decodeHtmlentities(scrapedtitle)
                     thumbnail = ''
                     plot = ''
                     itemlist.append( Item(channel=item.channel, action="temporadas" , title=title , fulltitle=title, url=url, thumbnail=thumbnail, plot=plot, folder =True, contentSerieName=title ))

                 return itemlist
             except:
                import sys
                for line in sys.exc_info():
                    logger.error( "%s" % line )
             return []

   

def findvideos(item):
    logger.info()
    itemlist=[]
    audio = {'la':'[COLOR limegreen]LATINO[/COLOR]','es':'[COLOR yellow]ESPAÑOL[/COLOR]','sub':'[COLOR red]ORIGINAL SUBTITULADO[/COLOR]'}
    data=httptools.downloadpage(item.url).data
    patron ='<td><img src="http:\/\/metaserie\.com\/wp-content\/themes\/mstheme\/gt\/assets\/img\/([^\.]+).png" width="20".*?<\/td>.*?<td><img src="http:\/\/www\.google\.com\/s2\/favicons\?domain=([^"]+)" \/>&nbsp;([^<]+)<\/td>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    
    anterior = scrapertools.find_single_match(data,'<th scope="col"><a href="([^"]+)" rel="prev" class="local-link">Anterior</a></th>')
    siguiente = scrapertools.find_single_match(data,'<th scope="col"><a href="([^"]+)" rel="next" class="local-link">Siguiente</a></th>')
    
    for scrapedid, scrapedurl, scrapedserv in matches:
        url = scrapedurl
        server = servertools.get_server_from_url(url).lower()
        title = item.title+' audio '+audio[scrapedid]+' en '+server
        extra = item.thumbnail
        thumbnail = servertools.guess_server_thumbnail(server)
        
        itemlist.append( Item(channel=item.channel, action="play" , title=title, fulltitle=item.contentSerieName, url=url, thumbnail=thumbnail, extra=extra, lang=scrapedid, quality='default', server=server))
    if item.extra1 != 'capitulos':
        if anterior !='':
            itemlist.append( Item(channel=item.channel, action="findvideos" , title='Capitulo Anterior' , url=anterior, thumbnail='https://s31.postimg.org/k5kpwyrgb/anterior.png'))
        if siguiente !='':
            itemlist.append( Item(channel=item.channel, action="findvideos" , title='Capitulo Siguiente' , url=siguiente, thumbnail='https://s32.postimg.org/4zppxf5j9/siguiente.png'))
    

    ### Requerido para AutoPlay ###

    autoplay_enabled = config.get_setting("autoplay", item.channel)
    if autoplay_enabled:
        autoplay(itemlist, item)

    return itemlist

### Requerido para AutoPlay ###

def configuracion(item):
    ret = platformtools.show_channel_settings()
    platformtools.itemlist_refresh()
    return ret

def autoplay (itemlist, item):
    logger.info()

    duplicados=[] 
    autoplay_list = []
    favorite_servers=[]
    favorite_quality=[]
    servidores = []
    lang=[]

    info_dialog = platformtools.dialog_notification('AutoPlay Activo','', sound=False)

### Verifica el estado de la configuracion automatica ###

    auto_config = config.get_setting("auto_config", item.channel)

    if auto_config:
        favorite_priority = 2                                           ### Si esta activa la auto-configuracion la prioridad se fija en calidad ###

    else:

        favorite_priority = config.get_setting("priority",item.channel) ### Ordena los enlaces por la prioridad Servidor/Calidad la lista de favoritos ###

### Obtiene las listas servidores, calidades e idiomas disponibles esde el xml del canal ###

    settings_list, actual_settings = channeltools.get_channel_controls_settings(item.channel)
    
    for setting in settings_list:
        for id_setting, name_setting in setting.items():

            if name_setting == 'server_1':
                server_list = setting['lvalues']
            
            elif name_setting == 'lang':
                lang_list = setting['lvalues']
            
            elif name_setting == 'quality_1':
                quality_list = setting['lvalues']


    
### Se obtienen desde el archivo de configuracion los servidores y calidades favoritos ###

    for num in range (1,4):
        favorite_servers.append(server_list[config.get_setting("server_"+str(num),item.channel)])
        favorite_quality.append(quality_list[config.get_setting("quality_"+str(num),item.channel)])

    lang = lang_list[(config.get_setting("lang", item.channel))]                                # Se obtiene el idioma favorito ###

### Se crea la lista de enlaces que cumplen los requisitos de los favoritos y no esten repetidos ###

    
    for item in itemlist:
        ### Se crea la lista para configuracion automatica
        if auto_config:     
            for quality in quality_list:
                if item.quality == quality and item.lang == lang and item.server in server_list:
                    autoplay_list.append([server_list.index(item.server), item, quality_list.index(quality),item.quality, item.server])
            
        
        else:
        ### Se crea la lista de enlaces que cumplen los requisitos de los favoritos ###

            for favorite in favorite_servers:
                if item.server == favorite and item.lang == lang and item.quality in favorite_quality and item.url not in duplicados:
                    autoplay_list.append([favorite_servers.index(favorite), item, favorite_quality.index(item.quality),item.quality, item.server])
                    duplicados.append(item.url)

    if favorite_priority == 2: 
        autoplay_list.sort(key=lambda priority: priority[2])            ### Se ordena la lista solo por calidad ###
    
    elif favorite_priority == 1: 
        autoplay_list.sort(key=lambda priority: priority[0])            ### Se ordena la lista solo por servidor ###
    
    elif favorite_priority == 0:
        autoplay_list.sort(key=lambda priority: priority[2])
        ordered_list = sorted(autoplay_list, key=lambda priority:priority[0])  ### Se ordena la lista por servidor y calidad
        autoplay_list = ordered_list
    
    #logger.debug('autoplay_list: '+str(autoplay_list)+' favorite priority: '+str(favorite_priority))
    
### Si hay elementos en la lista de autoplay se intenta reproducir cada elemento, hasta encontrar uno funcional o fallen todos  ###

    if autoplay_list:
        played = False
        
        for indice in autoplay_list:
            if not xbmc.Player().isPlaying() and not played:
                info_dialog = platformtools.dialog_notification('AutoPlay iniciado en:',indice[1].server.upper()+' '+lang+' '+str(indice[3]).upper(), sound=False)
                platformtools.play_video(indice[1])
                try:
                    total_time = xbmc.Player().getTotalTime()
                    played = True
                    
                except:                                         ### TODO evitar el informe de que el conector fallo o el video no se encuentra ###
                    logger.debug(str(len(autoplay_list)))
    else:
        info_dialog = platformtools.dialog_notification('AutoPlay No Fue Posible','No Hubo Coincidencias')

### devuelve la lista de enlaces para la eleccion manual ###

    return itemlist

def play(item):
    logger.info()
    itemlist =[]
    from core import servertools
    itemlist.extend(servertools.find_video_items(data=item.url))
    for videoitem in itemlist:
        video = item.channel
        videoitem.title = item.fulltitle
        videoitem.folder = False
        videoitem.thumbnail = item.extra
        videoitem.fulltitle = item.fulltitle
    return itemlist
   

    
