# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# Canal (seodiv) por Hernan_Ar_c
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

host='http://www.seodiv.com'


def mainlist(item):
    logger.info()

    itemlist = []

    itemlist.append( Item(channel=item.channel, title="Todos", action="todas", url=host,thumbnail='https://s32.postimg.org/544rx8n51/series.png', fanart='https://s32.postimg.org/544rx8n51/series.png', lang='latino'))
   
    plot_autoplay='AutoPlay permite auto reproducir los enlaces directamente, basandose en la configuracion de tus servidores y calidades preferidas.'
    itemlist.append(item.clone (title="[COLOR yellow]Configurar AutoPlay[/COLOR]", action="configuracion", thumbnail='https://s7.postimg.org/ff7ssxed7/autoplay.png', fanart='https://s7.postimg.org/ff7ssxed7/autoplay.png', plot = plot_autoplay))

    return itemlist

def todas(item):

    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r'"|\n|\r|\t|&nbsp;|<br>', "", data)
    logger.debug(data)

    patron ='<\/div><img src=(.*?) style=box.*?title-topic>(.*?)<\/div>.*?topic>(.*?)<\/div>.*?<a href=(.*?) style'
       
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedthumbnail, scrapedtitle, scrapedplot, scrapedurl in matches: 
        url = host+scrapedurl
        title = scrapedtitle.decode('utf-8')
        thumbnail = scrapedthumbnail
        fanart = 'https://s32.postimg.org/gh8lhbkb9/seodiv.png'
        plot = scrapedplot
        itemlist.append( Item(channel=item.channel, action="temporadas" ,title=title , url=url, thumbnail=thumbnail, fanart=fanart, plot= plot, contentSerieName=title, extra='', lang='latino', quality='default'))
           

    return itemlist
        
def temporadas(item):
    logger.info()
    itemlist = []
    templist = []
    data = httptools.downloadpage(item.url).data
    url_base= item.url
    patron = '<a class="collapsed" data-toggle="collapse" data-parent="#accordion" href=.*? aria-expanded="false" aria-controls=.*?>([^<]+)<\/a>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    temp=1
    if 'Temporada'in str(matches):
      	for scrapedtitle in matches:
           url = url_base
           tempo = re.findall(r'\d+',scrapedtitle)
           if tempo:
              title ='Temporada'+' '+ tempo[0]
           else:
              title = scrapedtitle.lower()
           thumbnail = item.thumbnail
           plot = item.plot
           fanart = scrapertools.find_single_match(data,'<img src="([^"]+)"/>.*?</a>')
           itemlist.append( Item(channel=item.channel, action="episodiosxtemp" , title=title , fulltitle=item.title, url=url, thumbnail=thumbnail, plot=plot, fanart = fanart, temp=str(temp),contentSerieName=item.contentSerieName, lang=item.lang, quality=item.quality))
           temp = temp+1
        
        if config.get_library_support() and len(itemlist) > 0:
           itemlist.append(Item(channel=item.channel, title='[COLOR yellow]Añadir esta serie a la biblioteca[/COLOR]', url=item.url,
                             action="add_serie_to_library", extra="episodios", contentSerieName=item.contentSerieName, extra1 = item.extra1, temp=str(temp)))
        return itemlist
    else:
        itemlist=episodiosxtemp(item)
        if config.get_library_support() and len(itemlist) > 0:
           itemlist.append(Item(channel=item.channel, title='[COLOR yellow]Añadir esta serie a la biblioteca[/COLOR]', url=item.url,
                             action="add_serie_to_library", extra="episodios", contentSerieName=item.contentSerieName, extra1 = item.extra1, temp=str(temp)))
        return itemlist

def episodios(item):
    logger.debug('pelisalacarta.channels.seodiv episodios')
    itemlist = []
    templist = temporadas(item)
    for tempitem in templist:
       logger.debug(tempitem)
       itemlist += episodiosxtemp(tempitem) 

    return itemlist

def episodiosxtemp(item):
    
    logger.debug("pelisalacarta.channels.seodiv episodiosxtemp")
    itemlist = []
    data = httptools.downloadpage(item.url).data
    tempo = item.title
    if 'Temporada'in item.title:
        item.title = item.title.replace('Temporada', 'temporada')
        item.title = item.title.strip()
        item.title = item.title.replace(' ','-')
                
    
    patron ='<li><a href="([^"]+)">.*?(Capitulo|Pelicula).*?([\d]+)'
        
    matches = re.compile(patron,re.DOTALL).findall(data)
    idioma = scrapertools.find_single_match(data,' <p><span class="ah-lead-tit">Idioma:</span>&nbsp;<span id="l-vipusk">([^<]+)</span></p>')
    for scrapedurl, scrapedtipo, scrapedtitle in matches:
        url = host+scrapedurl
        title =''
        thumbnail = item.thumbnail
        plot = item.plot
        fanart=''

        if 'temporada' in item.title and item.title in scrapedurl and scrapedtipo =='Capitulo' and item.temp !='':
            title = item.contentSerieName+' '+item.temp+'x'+scrapedtitle+' ('+idioma+')'
            itemlist.append( Item(channel=item.channel, action="findvideos" , title=title, fulltitle=item.fulltitle, url=url, thumbnail=item.thumbnail, plot=plot, lang=item.lang, quality=item.quality))
        
        if 'temporada' not in item.title and item.title not in scrapedurl and scrapedtipo =='Capitulo' and item.temp =='':
            if item.temp == '': temp = '1'
            title = item.contentSerieName+' '+temp+'x'+scrapedtitle+' ('+idioma+')'
            if '#' not in scrapedurl:
               itemlist.append( Item(channel=item.channel, action="findvideos" , title=title, fulltitle=item.fulltitle, url=url, thumbnail=item.thumbnail, plot=plot, lang=item.lang, quality=item.quality))
        
        if 'temporada' not in item.title and item.title not in scrapedurl and scrapedtipo =='Pelicula':
            title = scrapedtipo +' '+scrapedtitle
            itemlist.append( Item(channel=item.channel, action="findvideos" , title=title, fulltitle=item.fulltitle, url=url, thumbnail=item.thumbnail, plot=plot, lang=item.lang, quality=item.quality))

    return itemlist
    
def findvideos(item):
    logger.info()
    itemlist=[]
    video_items = servertools.find_video_items(item)
    
    for videoitem in video_items:
      videoitem.thumbnail = servertools.guess_server_thumbnail(videoitem.server)
      videoitem.lang = item.lang
      videoitem.quality = item.quality
      itemlist.append(videoitem)
    

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
                                 
    


    
