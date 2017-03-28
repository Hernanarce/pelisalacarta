# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# Canal (doomtv) por Hernan_Ar_c
# ------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os, sys

from core import logger
from core import config
from core import scrapertools
from core import httptools
from core.item import Item
from core import servertools
from core import tmdb


### Requerido para AutoPlay ###
import xbmc
from platformcode import platformtools
from core import channeltools


host = 'http://doomtv.net/'
headers = [['User-Agent', 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0'],
          ['Referer', host]]

tgenero = {"Comedia":"https://s32.postimg.org/q7g2qs90l/comedia.png",
               "Suspenso":"https://s31.postimg.org/kb629gscb/suspenso.png",
               "Drama":"https://s32.postimg.org/e6z83sqzp/drama.png",
               "Acción":"https://s32.postimg.org/4hp7gwh9x/accion.png",
               "Aventura":"https://s32.postimg.org/whwh56is5/aventura.png",
               "Romance":"https://s31.postimg.org/y7vai8dln/romance.png",
               "Animación":"https://s32.postimg.org/rbo1kypj9/animacion.png",
               "Ciencia Ficción":"https://s32.postimg.org/6hp3tsxsl/ciencia_ficcion.png",
               "Terror":"https://s32.postimg.org/ca25xg0ed/terror.png",
               "Documentales":"https://s32.postimg.org/7opmvc5ut/documental.png",
               "Musical":"https://s31.postimg.org/7i32lca7f/musical.png",
               "Fantasía":"https://s32.postimg.org/pklrf01id/fantasia.png",
               "Bélico Guerra":"https://s32.postimg.org/kjbko3xhx/belica.png",
               "Misterio":"https://s4.postimg.org/kd48bcxe5/misterio.png",
               "Crimen":"https://s14.postimg.org/5lez1j1gx/crimen.png",
               "Biográfia":"https://s23.postimg.org/u49p87o3f/biografia.png",
               "Familia":"https://s28.postimg.org/4wwzkt2f1/familiar.png",
               "Familiar":"https://s28.postimg.org/4wwzkt2f1/familiar.png",
               "Intriga":"https://s32.postimg.org/xc2ovcqfp/intriga.png",
               "Thriller":"https://s31.postimg.org/4d7bl25y3/thriller.png",
               "Guerra":"https://s29.postimg.org/vqgjmozzr/guerra.png",
               "Estrenos":"https://s12.postimg.org/4zj0rbun1/estrenos.png",
               "Peleas":"https://s14.postimg.org/53qrbqy5d/peleas.png",
               "Policiales":"https://s15.postimg.org/ctz76qrwb/policial.png",
               "Uncategorized":"https://s16.postimg.org/fssbi4nlh/otros.png",
               "LGBT":"https://s16.postimg.org/fssbi4nlh/otros.png"}

def mainlist(item):
    logger.info()

    itemlist = []
    
    itemlist.append( item.clone (title="Todas", action="lista",thumbnail='https://s12.postimg.org/iygbg8ip9/todas.png', fanart='https://s12.postimg.org/iygbg8ip9/todas.png', url = host))

    itemlist.append( item.clone (title="Generos", action="seccion", thumbnail='https://s31.postimg.org/szbr0gmkb/generos.png', fanart='https://s31.postimg.org/szbr0gmkb/generos.png',url = host, extra ='generos'))

    itemlist.append( item.clone (title="Mas vistas", action="seccion", thumbnail='https://s32.postimg.org/466gt3ipx/vistas.png', fanart='https://s32.postimg.org/466gt3ipx/vistas.png',url = host, extra ='masvistas'))

    itemlist.append( item.clone (title="Recomendadas", action="lista",thumbnail='https://s31.postimg.org/4bsjyc4iz/recomendadas.png', fanart='https://s31.postimg.org/4bsjyc4iz/recomendadas.png', url = host, extra = 'recomendadas'))

    itemlist.append( item.clone (title="Por año", action="seccion", thumbnail='https://s31.postimg.org/iyl5fvzqz/pora_o.png', fanart='https://s31.postimg.org/iyl5fvzqz/pora_o.png',url = host, extra ='poraño'))

    itemlist.append( item.clone (title="Buscar", action="search", url='http://doomtv.net/?s=', thumbnail='https://s31.postimg.org/qose4p13f/Buscar.png', fanart='https://s31.postimg.org/qose4p13f/Buscar.png'))

    plot_autoplay='AutoPlay permite auto reproducir los enlaces directamente, basandose en la configuracion de tus servidores y calidades preferidas.'
    itemlist.append(item.clone (title="[COLOR yellow]Configurar AutoPlay[/COLOR]", action="configuracion", thumbnail='https://s7.postimg.org/ff7ssxed7/autoplay.png', fanart='https://s7.postimg.org/ff7ssxed7/autoplay.png', plot = plot_autoplay))

    return itemlist

def lista (item):
    logger.info()
	
    itemlist = []
    max_items = 20
    next_page_url = ''

    data = httptools.downloadpage(item.url).data
    

    if item.extra == 'recomendadas':
        patron = '<a href="(.*?)">.*?'
        patron +='<div class="imgss">.*?'
        patron +='<img src="(.*?)" alt="(.*?)(?:–.*?|\(.*?|&#8211;|").*?'
        patron +='<div class="imdb">.*?'
        patron +='<\/a>.*?'
        patron +='<span class="ttps">.*?<\/span>.*?'
        patron +='<span class="ytps">(.*?)<\/span><\/div>'
        
    else:
        patron = '<div class="imagen">.*?'
        patron +='<img src="(.*?)" alt="(.*?)(?:–.*?|\(.*?|&#8211;|").*?'
        patron +='<a href="([^"]+)"><(?:span) class="player"><\/span><\/a>.*?'
        patron +='h2>\s*.*?(?:year)">(.*?)<\/span>.*?<\/div>'
    matches = re.compile(patron,re.DOTALL).findall(data)

    if item.next_page != 'b':
      if len(matches) > max_items:
        next_page_url = item.url
        matches = matches [:max_items]
        next_page = 'b'
    else:
      matches = matches[max_items:]
      next_page = 'a'
      patron_next_page = '<div class="siguiente"><a href="(.*?)"|\/\?'
      matches_next_page = re.compile(patron_next_page, re.DOTALL).findall(data)
      if len(matches_next_page) > 0:
        next_page_url = urlparse.urljoin(item.url, matches_next_page[0])

    for scrapedthumbnail, scrapedtitle, scrapedurl, scrapedyear in matches:
        if item.extra == 'recomendadas':
            url = scrapedthumbnail
            title = scrapedurl
            thumbnail = scrapedtitle
        else:
            url = scrapedurl
            thumbnail = scrapedthumbnail
            title = scrapedtitle
        year = scrapedyear
        fanart =''
        plot= ''
                       
        if 'serie' not in url:
            itemlist.append( Item(channel=item.channel, action='findvideos' , title=title , url=url, thumbnail=thumbnail, plot=plot, fanart=fanart, contentTitle = title, infoLabels={'year':year}))
    
    tmdb.set_infoLabels_itemlist(itemlist, seekTmdb = True)
    #Paginacion
    if next_page_url !='':
      itemlist.append(Item(channel = item.channel, action = "lista", title = 'Siguiente >>>', url = next_page_url, thumbnail='https://s32.postimg.org/4zppxf5j9/siguiente.png',extra=item.extra, next_page = next_page))
    return itemlist


def seccion(item):
    logger.info()
    
    itemlist = []
    duplicado = []
    data = httptools.downloadpage(item.url).data

    if item.extra == 'generos':
      data = re.sub(r"\n|\r|\t|&nbsp;|<br>", "", data)
    accion ='lista'
    if item.extra == 'masvistas':
        patron = '<b>\d*<\/b>\s*<a href="(.*?)">(.*?<\/a>\s*<span>.*?<\/span>\s*<i>.*?<\/i><\/li>)'
        accion = 'findvideos'
    elif item.extra == 'poraño':
        patron = '<li><a class="ito" HREF="(.*?)">(.*?)<\/a><\/li>'
    else:
        patron ='<li class="cat-item cat-item-.*?"><a href="(.*?)">(.*?)<\/i><\/li>'

    matches = re.compile(patron,re.DOTALL).findall(data)

    for scrapedurl,scrapedtitle in matches:
        url = scrapedurl
        title = scrapedtitle
        thumbnail = ''
        fanart =''
        plot= ''
        year=''
        contentTitle=''
        if item.extra == 'masvistas':
          year = re.findall(r'\b\d{4}\b',scrapedtitle)
          title = re.sub(r'<\/a>\s*<span>.*?<\/span>\s*<i>.*?<\/i><\/li>','',scrapedtitle)
          contentTitle = title
          title = title+' ('+year[0]+')'

        elif item.extra == 'generos':
          title = re.sub(r'<\/a> <i>\d+','',scrapedtitle)
          cantidad = re.findall(r'.*?<\/a> <i>(\d+)',scrapedtitle)
          logger.debug('scrapedtitle: '+scrapedtitle)
          logger.debug('cantidad: '+str(cantidad))
          th_title = title
          title = title+' ('+cantidad[0]+')'
          thumbnail = tgenero[th_title]
          fanart = thumbnail

        if url not in duplicado:
          itemlist.append( Item(channel=item.channel, action=accion , title=title , url=url, thumbnail=thumbnail, plot=plot, fanart=fanart, contentTitle=contentTitle, infoLabels={'year':year}))
          duplicado.append(url)
    tmdb.set_infoLabels_itemlist(itemlist, seekTmdb = True)
    return itemlist

def unpack(packed):
    p,c,k = re.search("}\('(.*)', *\d+, *(\d+), *'(.*)'\.", packed, re.DOTALL).groups()
    for c in reversed(range(int(c))):
        if k.split('|')[c]: p = re.sub(r'(\b%s\b)' % c, k.split('|')[c], p)
        p = p.replace('\\','')
        p = p.decode('string_escape')
    return p

def getinfo(page_url):
    info =()
    logger.info()
    data = httptools.downloadpage(page_url).data
    thumbnail = scrapertools.find_single_match(data,'<div class="cover" style="background-image: url\((.*?)\);')
    plot = scrapertools.find_single_match(data,'<h2>Synopsis<\/h2>\s*<p>(.*?)<\/p>')
    info = (plot,thumbnail)

    return info

def search(item,texto):
    logger.info()
    texto = texto.replace(" ","+")
    item.url = item.url+texto
    if texto!='':
       return lista(item)

def newest(categoria):
    logger.info()
    itemlist = []
    item = Item()
    #categoria='peliculas'
    try:
        if categoria == 'peliculas':
            item.url = host
        elif categoria == 'infantiles':
            item.url = host+'category/animacion/'
        itemlist = lista(item)
        if itemlist[-1].title == 'Siguiente >>>':
                itemlist.pop()
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist

def get_url(item):
    logger.info()
    itemlist=[]
    duplicado =[]
    patrones =["{'label':(.*?),.*?'file':'(.*?)'}","{file:'(.*?redirector.*?),label:'(.*?)'}"]
    data = httptools.downloadpage(item.url, headers=headers, cookies=False).data
    
    url = scrapertools.find_single_match(data,'class="player-content"><iframe src="(.*?)"')
    url= 'http:/'+url.replace('//','/')
    data = httptools.downloadpage(url, headers= headers, cookies=False).data
    packed = scrapertools.find_single_match(data, "<script type='text\/javascript'>(eval.*?)\s*jwplayer\(\)")

    if packed:
      unpacked=unpack(packed)
      num_patron = 0
      patron = "{'label':(.*?),.*?'file':'(.*?)'}"
      matches = re.compile(patron,re.DOTALL).findall(unpacked)
      if not matches:
       patron = "{file:'(.*?redirector.*?),label:'(.*?)'}"
       matches = re.compile(patron,re.DOTALL).findall(unpacked)
    
      for dato_a, dato_b in matches:
        if 'http' in dato_a:
          url = dato_a
          calidad = dato_b
        else:
          url = dato_b
          calidad = dato_a
        title = item.contentTitle+' ('+calidad+')'
        if url not in duplicado:
          itemlist.append( Item(channel=item.channel, action='play' , title=title , url=url, thumbnail=item.thumbnail, plot=item.plot, fanart=item.fanart, contentTitle = item.contentTitle, lang= 'latino', server='directo', quality=calidad))
          duplicado.append(url)

      return itemlist

def findvideos (item):
    logger.info()
    itemlist =[]
    itemlist = get_url(item)
    if config.get_library_support() and len(itemlist) > 0 and item.extra !='findvideos' :
        itemlist.append(Item(channel=item.channel, title='[COLOR yellow]Añadir esta pelicula a la biblioteca[/COLOR]', url=item.url,
                             action="add_pelicula_to_library", extra="findvideos", contentTitle = item.contentTitle))
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


