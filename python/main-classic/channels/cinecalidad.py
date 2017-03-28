# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# Canal (cinecalidad) por Hernan_Ar_c
# ------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os, sys

from core import logger
from core import config
from core import scrapertools
from core.item import Item
from core import servertools
from core import httptools
from core import tmdb
from core import jsontools

### Requerido para AutoPlay ###
import xbmc
from platformcode import platformtools
from core import channeltools



host='http://www.cinecalidad.to'
thumbmx='http://flags.fmcdn.net/data/flags/normal/mx.png'
thumbes='http://flags.fmcdn.net/data/flags/normal/es.png'
thumbbr='http://flags.fmcdn.net/data/flags/normal/br.png'

def mainlist(item):
    idioma2 ="destacadas" 
    logger.info()
    itemlist = []

    itemlist.append(item.clone (title="Audio Latino", action="submenu",host="http://cinecalidad.com/",thumbnail=thumbmx, extra = "peliculas", lang='latino'))
    
    itemlist.append(item.clone (title="Audio Castellano", action="submenu",host="http://cinecalidad.com/espana/",thumbnail=thumbes, extra = "peliculas", lang='castellano'))
    
    itemlist.append(item.clone (title="Audio Portugues", action="submenu",host="http://cinemaqualidade.com/",thumbnail=thumbbr, extra ="filmes", lang = 'portugues'))

    plot_autoplay='AutoPlay permite auto reproducir los enlaces directamente, basandose en la configuracion de tus servidores y calidades preferidas.'
    itemlist.append(item.clone (title="[COLOR yellow]Configurar AutoPlay[/COLOR]", action="configuracion", thumbnail='https://s7.postimg.org/ff7ssxed7/autoplay.png', fanart='https://s7.postimg.org/ff7ssxed7/autoplay.png', plot = plot_autoplay))
    
    return itemlist


def submenu(item):
    idioma='peliculas'
    idioma2 ="destacada"
    host = item.host
    if item.host == "http://cinemaqualidade.com/" : 
       idioma = "filmes"
       idioma2 = "destacado"
    logger.info("pelisalacarta.channels.cinecalidad submenu")
    itemlist = []
    itemlist.append( Item(channel=item.channel, title=idioma.capitalize(), action="peliculas", url=host,thumbnail='https://s31.postimg.org/4g4lytrqj/peliculas.png', fanart='https://s31.postimg.org/4g4lytrqj/peliculas.png', lang=item.lang))
    itemlist.append( Item(channel=item.channel, title="Destacadas", action="peliculas", url=host+"/genero-"+idioma+"/"+idioma2+"/", thumbnail='https://s32.postimg.org/wzyinepsl/destacadas.png', fanart='https://s32.postimg.org/wzyinepsl/destacadas.png',lang=item.lang))
    itemlist.append( Item(channel=item.channel, title="Generos", action="generos", url=host+"/genero-"+idioma, thumbnail='https://s31.postimg.org/szbr0gmkb/generos.png',fanart='https://s31.postimg.org/szbr0gmkb/generos.png',lang=item.lang))   
    itemlist.append( Item(channel=item.channel, title="Por Año", action="anyos", url=host+"/"+idioma+"-por-ano", thumbnail='https://s31.postimg.org/iyl5fvzqz/pora_o.png', fanart='https://s31.postimg.org/iyl5fvzqz/pora_o.png',lang=item.lang))
    itemlist.append( Item(channel=item.channel, title="Buscar", action="search", thumbnail='https://s31.postimg.org/qose4p13f/Buscar.png', url =host+'/apiseries/seriebyword/', fanart='https://s31.postimg.org/qose4p13f/Buscar.png', host = item.host,lang=item.lang))
    
    return itemlist



def anyos(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    patron = '<a href="([^"]+)">([^<]+)</a> '
    matches = re.compile(patron,re.DOTALL).findall(data)

    for scrapedurl,scrapedtitle in matches:
        url = urlparse.urljoin(item.url,scrapedurl)
        title = scrapedtitle
        thumbnail = item.thumbnail
        plot = item.plot
        itemlist.append( Item(channel=item.channel, action="peliculas" , title=title , url=url, thumbnail=thumbnail, plot=plot, fanart=item.thumbnail, lang=item.lang))

    return itemlist

def generos(item):
    tgenero = {"Comedia":"https://s32.postimg.org/q7g2qs90l/comedia.png",
               "Suspenso":"https://s31.postimg.org/kb629gscb/suspenso.png",
               "Drama":"https://s32.postimg.org/e6z83sqzp/drama.png",
               "Acción":"https://s32.postimg.org/4hp7gwh9x/accion.png",
               "Aventura":"https://s32.postimg.org/whwh56is5/aventura.png",
               "Romance":"https://s31.postimg.org/y7vai8dln/romance.png",
               "Fantas\xc3\xada":"https://s32.postimg.org/pklrf01id/fantasia.png",
               "Infantil":"https://s32.postimg.org/i53zwwgsl/infantil.png",
               "Ciencia ficción":"https://s32.postimg.org/6hp3tsxsl/ciencia_ficcion.png",
               "Terror":"https://s32.postimg.org/ca25xg0ed/terror.png",
               "Com\xc3\xa9dia":"https://s32.postimg.org/q7g2qs90l/comedia.png",
               "Suspense":"https://s31.postimg.org/kb629gscb/suspenso.png",
               "A\xc3\xa7\xc3\xa3o":"https://s32.postimg.org/4hp7gwh9x/accion.png",
               "Fantasia":"https://s32.postimg.org/pklrf01id/fantasia.png",
               "Fic\xc3\xa7\xc3\xa3o cient\xc3\xadfica":"https://s32.postimg.org/6hp3tsxsl/ciencia_ficcion.png"}
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    patron = '<li id="menu-item-.*?" class="menu-item menu-item-type-taxonomy menu-item-object-category menu-item-.*?"><a href="([^"]+)">([^<]+)<\/a></li>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedtitle in matches:
        url = urlparse.urljoin(item.url,scrapedurl)
        title = scrapedtitle
        thumbnail = tgenero[scrapedtitle]
        plot = item.plot
        itemlist.append( Item(channel=item.channel, action="peliculas" , title=title , url=url, thumbnail=thumbnail, plot=plot, fanart=item.thumbnail, lang=item.lang))

    return itemlist

def peliculas(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
   
    patron = '<div class="home_post_cont.*? post_box">.*?<a href="([^"]+)".*?src="([^"]+)".*?title="(.*?) \((.*?)\)".*?p&gt;([^&]+)&lt;'
    matches = re.compile(patron,re.DOTALL).findall(data)

    for scrapedurl,scrapedthumbnail,scrapedtitle, scrapedyear, scrapedplot  in matches:
        url = urlparse.urljoin(item.url,scrapedurl)
        contentTitle = scrapedtitle
        title = scrapedtitle+' ('+scrapedyear+')'
        thumbnail = scrapedthumbnail
        plot = scrapedplot
        year = scrapedyear
        itemlist.append( Item(channel=item.channel, action="findvideos" , title=title , url=url, thumbnail=thumbnail, plot=plot, fanart='https://s31.postimg.org/puxmvsi7v/cinecalidad.png', contentTitle = contentTitle, infoLabels={'year':year}, lang=item.lang ))
    
    try:     
        patron  = "<link rel='next' href='([^']+)' />" 
        next_page = re.compile(patron,re.DOTALL).findall(data)
        itemlist.append( Item(channel=item.channel, action="peliculas", title="Página siguiente >>" , url=next_page[0], fanart='https://s31.postimg.org/puxmvsi7v/cinecalidad.png', lang=item.lang) )

    except: pass
    tmdb.set_infoLabels_itemlist(itemlist, seekTmdb = True)
    return itemlist


def dec(item):
        link=[]
        val= item.split(' ')
        link = map(int, val)
        for i in range(len(link)):
            link[i] = link[i]-7
            real=''.join(map(chr, link))
        return (real)


def findvideos(item):
    servidor = {"http://uptobox.com/":"uptobox","http://userscloud.com/":"userscloud","https://my.pcloud.com/publink/show?code=":"pcloud","http://thevideos.tv/":"thevideos","http://ul.to/":"uploadedto","http://turbobit.net/":"turbobit","http://www.cinecalidad.com/protect/v.html?i=":"cinecalidad","http://www.mediafire.com/download/":"mediafire","https://www.youtube.com/watch?v=":"youtube","http://thevideos.tv/embed-":"thevideos","//www.youtube.com/embed/":"youtube","http://ok.ru/video/":"okru","http://ok.ru/videoembed/":"okru","http://www.cinemaqualidade.com/protect/v.html?i=":"cinemaqualidade.com","http://usersfiles.com/":"usersfiles","https://depositfiles.com/files/":"depositfiles","http://www.nowvideo.sx/video/":"nowvideo","http://vidbull.com/":"vidbull","http://filescdn.com/":"filescdn","https://www.yourupload.com/watch/":"yourupload"}
    logger.info()
    itemlist=[]
    duplicados=[]
    data = httptools.downloadpage(item.url).data
    
    patron = 'dec\("([^"]+)"\)\+dec\("([^"]+)"\)'
    matches = re.compile(patron,re.DOTALL).findall(data)
    recomendados = ["uptobox","thevideos","nowvideo","pcloud"]
    for scrapedurl,scrapedtitle in matches:
        if dec(scrapedurl) in servidor:
          server=servidor[dec(scrapedurl)]
          title = "Ver "+item.contentTitle+" en "+servidor[dec(scrapedurl)].upper()
          if 'yourupload' in dec(scrapedurl):
            url = dec(scrapedurl).replace('watch','embed')+dec(scrapedtitle)
          else:

            if 'youtube' in dec(scrapedurl):
                title='[COLOR orange]Trailer en Youtube[/COLOR]'
            url = dec(scrapedurl)+dec(scrapedtitle)

          
          if (servidor[dec(scrapedurl)]) in recomendados:
            title=title+"[COLOR limegreen] [I] (Recomedado) [/I] [/COLOR]"
          thumbnail = servertools.guess_server_thumbnail(servidor[dec(scrapedurl)])
          plot = ""
          if title not in duplicados:
            itemlist.append( Item(channel=item.channel, action="play" , title=title ,fulltitle = item.title, url=url, thumbnail=thumbnail, plot=plot,extra=item.thumbnail, lang=item.lang, quality='default', server=server))
          duplicados.append(title)
    if config.get_library_support() and len(itemlist) > 0 and item.extra !='findvideos' :
        itemlist.append(Item(channel=item.channel, title='[COLOR yellow]Añadir esta pelicula a la biblioteca[/COLOR]', url=item.url,
                             action="add_pelicula_to_library", extra="findvideos", contentTitle = item.contentTitle))
    
    ### Requerido para AutoPlay ###

    autoplay_enabled = config.get_setting("autoplay", item.channel)
    if autoplay_enabled:
        autoplay(itemlist, item)

    return itemlist

def play(item):
    
    logger.info()

    itemlist = servertools.find_video_items(data=item.url)

            
    for videoitem in itemlist:
        videoitem.title = item.fulltitle
        videoitem.fulltitle = item.fulltitle
        videoitem.thumbnail = item.extra
        videochannel=item.channel
    return itemlist

def newest(categoria):
    logger.info()
    itemlist = []
    item = Item()
    try:
        if categoria == 'peliculas':
            item.url = 'http://www.cinecalidad.to'
        elif categoria == 'infantiles':
            item.url ='http://www.cinecalidad.to/genero-peliculas/infantil/'
        itemlist = peliculas(item)
        if itemlist[-1].title == 'Página siguiente >>':
                itemlist.pop()
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist

def busqueda(item):
    logger.info()
    itemlist = []

    # Descarga la página
    data = httptools.downloadpage(item.url).data

    from core import jsontools
    data = jsontools.load_json(data)

    for entry in data["results"]:
        title = entry["richSnippet"]["metatags"]["ogTitle"]
        url = entry["url"]
        plot = entry["content"]
        plot = scrapertools.htmlclean(plot)
        thumbnail = entry["richSnippet"]["metatags"]["ogImage"]
        title = scrapertools.find_single_match(title,'(.*?) \(.*?\)')
        year = re.sub(r'.*?\((\d{4})\)','', title)
        title = year
        fulltitle = title
        logger.debug(plot)
        
        new_item = item.clone(action="findvideos", title=title, fulltitle=fulltitle,
                              url=url, thumbnail=thumbnail, contentTitle=title, contentType="movie", plot= plot, infoLabels = {'year':year, 'sinopsis':plot})
        itemlist.append(new_item)
    
    tmdb.set_infoLabels_itemlist(itemlist, seekTmdb=True)

    actualpage = int(scrapertools.find_single_match(item.url, 'start=(\d+)'))
    totalresults = int(data["cursor"]["resultCount"])
    if actualpage + 20 <= totalresults:
        url_next = item.url.replace("start="+str(actualpage), "start="+str(actualpage+20))
        itemlist.append(Item(channel=item.channel, action="busqueda", title=">> Página Siguiente", url=url_next))

    return itemlist

def search(item, texto):
    logger.info()
    
    data = httptools.downloadpage(host).data
    cx = scrapertools.find_single_match(data, 'name="cx" value="(.*?)"')
    texto = texto.replace(" ", "%20")
    item.url = "https://www.googleapis.com/customsearch/v1element?key=AIzaSyCVAXiUzRYsML1Pv6RwSG1gunmMikTzQqY&rsz=filtered_cse&num=20&hl=es&sig=0c3990ce7a056ed50667fe0c3873c9b6&cx=%s&q=%s&sort=&googlehost=www.google.com&start=0" % (cx, texto)

    try:
        return busqueda(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


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