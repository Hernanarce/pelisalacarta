# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# Canal (verpeliculasnuevas) por Hernan_Ar_c
# ------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os, sys

from core import logger
from core import config
from core import scrapertools
from core.item import Item
from core import servertools
from core import tmdb
from core import httptools

### Requerido para AutoPlay ###
import xbmc
from platformcode import platformtools
from core import channeltools
from channels import configuracion


host = 'http://verpeliculasnuevas.com'

taudio = {'latino':'[COLOR limegreen]LATINO[/COLOR]','castellano':'[COLOR yellow]ESPAÑOL[/COLOR]','sub':'[COLOR red]ORIGINAL SUBTITULADO[/COLOR]', 'castellanolatinosub':'[COLOR orange]MULTI[/COLOR]','castellanolatino':'[COLOR orange]MULTI[/COLOR]'}

thumbaudio = {'latino':'http://flags.fmcdn.net/data/flags/normal/mx.png', 'castellano':'http://flags.fmcdn.net/data/flags/normal/es.png', 'sub':'https://s32.postimg.org/nzstk8z11/sub.png'}

tcalidad = {'hq':'[COLOR limegreen]HQ[/COLOR]','hd':'[COLOR limegreen]HD[/COLOR]','hd-1080':'[COLOR limegreen]HD-1080[/COLOR]', 'dvd':'[COLOR limegreen]DVD[/COLOR]','cam':'[COLOR red]CAM[/COLOR]', }

thumbcalidad = {'hd-1080':'https://s24.postimg.org/vto15vajp/hd1080.png','dvd':'https://s31.postimg.org/6sksfqarf/dvd.png','cam':'https://s29.postimg.org/c7em44e9j/cam.png','hq':'https://s27.postimg.org/bs0jlpdsz/image.png','hd':'https://s30.postimg.org/6vxtqu9sx/image.png'}

thumbletras = {'0-9':'https://s32.postimg.org/drojt686d/image.png',
    '1':'https://s32.postimg.org/drojt686d/image.png',
    'a':'https://s32.postimg.org/llp5ekfz9/image.png',
    'b':'https://s32.postimg.org/y1qgm1yp1/image.png',
    'c':'https://s32.postimg.org/vlon87gmd/image.png',
    'd':'https://s32.postimg.org/3zlvnix9h/image.png',
    'e':'https://s32.postimg.org/bgv32qmsl/image.png',
    'f':'https://s32.postimg.org/y6u7vq605/image.png',
    'g':'https://s32.postimg.org/9237ib6jp/image.png',
    'h':'https://s32.postimg.org/812yt6pk5/image.png',
    'i':'https://s32.postimg.org/6nbbxvqat/image.png',
    'j':'https://s32.postimg.org/axpztgvdx/image.png',
    'k':'https://s32.postimg.org/976yrzdut/image.png',
    'l':'https://s32.postimg.org/fmal2e9yd/image.png',
    'm':'https://s32.postimg.org/m19lz2go5/image.png',
    'n':'https://s32.postimg.org/b2ycgvs2t/image.png',
    "ñ":"https://s30.postimg.org/ayy8g02xd/image.png",
    'o':'https://s32.postimg.org/c6igsucpx/image.png',
    'p':'https://s32.postimg.org/jnro82291/image.png',
    'q':'https://s32.postimg.org/ve5lpfv1h/image.png',
    'r':'https://s32.postimg.org/nmovqvqw5/image.png',
    's':'https://s32.postimg.org/zd2t89jol/image.png',
    't':'https://s32.postimg.org/wk9lo8jc5/image.png',
    'u':'https://s32.postimg.org/w8s5bh2w5/image.png',
    'v':'https://s32.postimg.org/e7dlrey91/image.png',
    'w':'https://s32.postimg.org/fnp49k15x/image.png',
    'x':'https://s32.postimg.org/dkep1w1d1/image.png',
    'y':'https://s32.postimg.org/um7j3zg85/image.png',
    'z':'https://s32.postimg.org/jb4vfm9d1/image.png'}

tgenero = {    "comedia":"https://s32.postimg.org/q7g2qs90l/comedia.png",
               "suspenso":"https://s31.postimg.org/kb629gscb/suspenso.png",
               "drama":"https://s32.postimg.org/e6z83sqzp/drama.png",
               "accion":"https://s32.postimg.org/4hp7gwh9x/accion.png",
               "aventura":"https://s32.postimg.org/whwh56is5/aventura.png",
               "romance":"https://s31.postimg.org/y7vai8dln/romance.png",
               "thriller":"https://s31.postimg.org/4d7bl25y3/thriller.png",
               "ciencia-ficcion":"https://s32.postimg.org/6hp3tsxsl/ciencia_ficcion.png",
               "terror":"https://s32.postimg.org/ca25xg0ed/terror.png",
               "documental":"https://s32.postimg.org/7opmvc5ut/documental.png",
               "musical":"https://s31.postimg.org/7i32lca7f/musical.png",
               "fantastico":"https://s32.postimg.org/b6xwbui6d/fantastico.png",
               "deporte":"https://s31.postimg.org/pdc8etc0r/deporte.png",
               "infantil":"https://s32.postimg.org/i53zwwgsl/infantil.png",
               "animacion":"https://s32.postimg.org/rbo1kypj9/animacion.png"}

patrones =['','<span class="clms">Sinopsis:<\/span>([^<]+)<div class="info_movie">']

### Requerido para AutoPlay ###



def mainlist(item):
    logger.info()

    itemlist = []

    itemlist.append( item.clone (title="Todas", action="lista",thumbnail='https://s12.postimg.org/iygbg8ip9/todas.png', fanart='https://s12.postimg.org/iygbg8ip9/todas.png', extra='peliculas/', url = host))
    
    itemlist.append( itemlist[-1].clone (title="Generos", action="menuseccion", thumbnail='https://s31.postimg.org/szbr0gmkb/generos.png', fanart='https://s31.postimg.org/szbr0gmkb/generos.png',url = host, extra='/genero'))

    itemlist.append( itemlist[-1].clone (title="Alfabetico", action="menuseccion", thumbnail='https://s31.postimg.org/c3bm9cnl7/a_z.png', fanart='https://s31.postimg.org/c3bm9cnl7/a_z.png',url = host, extra='/tag'))

    itemlist.append( itemlist[-1].clone (title="Audio", action="menuseccion",thumbnail='https://s24.postimg.org/qmvqz4uxx/audio.png', fanart='https://s24.postimg.org/qmvqz4uxx/audio.png', url = host, extra= '/audio'))
        
    itemlist.append( itemlist[-1].clone (title="Calidad", action="menuseccion",thumbnail='https://s23.postimg.org/ui42030wb/calidad.png', fanart='https://s23.postimg.org/ui42030wb/calidad.png', extra='/calidad'))

    itemlist.append( itemlist[-1].clone (title="Año", action="menuseccion", thumbnail='https://s31.postimg.org/iyl5fvzqz/pora_o.png', fanart='https://s31.postimg.org/iyl5fvzqz/pora_o.png',url = host, extra='/fecha-estreno'))

    itemlist.append( itemlist[-1].clone (title="Buscar", action="search", url=host+'?s=', thumbnail='https://s31.postimg.org/qose4p13f/Buscar.png', fanart='https://s31.postimg.org/qose4p13f/Buscar.png'))

    plot_autoplay='AutoPlay permite auto reproducir los enlaces directamente, basandose en la configuracion de tus servidores y calidades preferidas.'
    itemlist.append(item.clone (title="[COLOR yellow]Configurar AutoPlay[/COLOR]", action="configuracion", thumbnail='https://s7.postimg.org/ff7ssxed7/autoplay.png', fanart='https://s7.postimg.org/ff7ssxed7/autoplay.png', plot = plot_autoplay))

    return itemlist
    

def menuseccion(item):
    logger.info()
    itemlist = []
    seccion = item.extra
    data = httptools.downloadpage(item.url).data

    if seccion == '/audio':
        patron = "<a href='\/audio([^']+)' title='lista de películas en.*?'>(?:Español|Latino|Subtitulado)<\/a>"
    elif seccion == '/calidad':
    	patron = "<a href='\/calidad([^']+)' title='lista de películas en.*?'>(?:HD-1080|HD-Real|DvD|HQ|CAM)<\/a>"
    elif seccion == '/fecha-estreno':
    	patron = "<a href='\/fecha-estreno([^']+)' title='lista de películas del.*?'>.*?<\/a>"
    elif seccion == '/genero':
    	patron = '<a href="\/genero([^"]+)">.*?<\/a><\/li>'
    else:
    	patron = "<a href='\/tag([^']+)' title='lista de películas.*?'>.*?<\/a>"

    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl in matches:
    	
    	url =host+seccion+scrapedurl
    	titulo = scrapedurl.replace('/','')
    	
    	if seccion == '/audio':
    	   title = taudio[titulo.lower()]
    	   thumbnail = thumbaudio[titulo]
    	elif seccion == '/calidad':
    	   title = tcalidad[titulo.lower()]
    	   thumbnail = thumbcalidad[titulo]
    	elif seccion == '/tag':
    	   title = titulo.upper()
    	   if titulo in thumbletras:
    	      thumbnail = thumbletras[titulo]
    	   else:
    	   	  thumbnail = ''
    	else:
    		title = titulo.upper()
    		if titulo in tgenero:
    		  thumbnail = tgenero[titulo]
    		else:
    		  thumbnail = ''

        itemlist.append( Item(channel=item.channel, action='lista' , title=title , url=url, thumbnail = thumbnail))

    return itemlist


def lista (item):
    logger.info()
	
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r'"|\n|\r|\t|&nbsp;|<br>', "", data)

    patron = "peli><a href=([^ ]+) title=(.*?)><img src=([^ ]+) alt=.*?><div class=([^>]+)>.*?<p>.*?<\/p>.*?flags ([^']+)'"
    matches = re.compile(patron,re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle, scrapedthumbnail,  scrapedcalidad, scrapedidioma in matches:
        year = scrapertools.find_single_match(scrapedtitle,'.*?\((\d{4})\)')
        scrapedtitle = scrapertools.find_single_match(scrapedtitle,'(.*?)\(\.*?')
        url = scrapedurl
        thumbnail = scrapedthumbnail
        scrapedcalidad = scrapedcalidad.replace("'","")
        scrapedcalidad = scrapedcalidad.lower()
        
        if scrapedcalidad in tcalidad:
        	scrapedcalidad = tcalidad[scrapedcalidad]
        else:
        	scrapedcalidad = '[COLOR orange]MULTI[/COLOR]'

        if scrapedidioma in taudio:
        	scrapedidioma = taudio[scrapedidioma]
        else:
        	scrapedidioma = '[COLOR orange]MULTI[/COLOR]'        
        
        title = scrapedtitle+' | '+scrapedcalidad+' | '+scrapedidioma+ ' | '
        fanart =''

        #plot= scrapertools.find_single_match(dataplot, '<span class="clms">Sinopsis:<\/span>([^<]+)<div class="info_movie">')
        plot =''
        
        itemlist.append( Item(channel=item.channel, action='findvideos' , title=title , url=url, thumbnail=thumbnail, plot=plot, fanart=fanart, contentTitle = scrapedtitle, extra = item.extra, infoLabels ={'year':year}))
       
# #Paginacion
    tmdb.set_infoLabels_itemlist(itemlist, seekTmdb=True)
    itemlist = fail_tmdb(itemlist)
    if itemlist !=[]:
        actual_page_url = item.url
        next_page = scrapertools.find_single_match(data,"class=previouspostslink' href='([^']+)'>Siguiente &rsaquo;<\/a>")
        import inspect
        if next_page !='':
           itemlist.append(Item(channel = item.channel, action = "lista", title = 'Siguiente >>>', url = next_page, thumbnail='https://s32.postimg.org/4zppxf5j9/siguiente.png',extra=item.extra))
    
    return itemlist

def fail_tmdb(itemlist):
    logger.info()
    realplot=''
    for item in itemlist:
        if item.infoLabels['plot'] =='':
            data = httptools.downloadpage(item.url).data
            if item.thumbnail == '':
                item.thumbnail= scrapertools.find_single_match(data,patrones[0])
            realplot = scrapertools.find_single_match(data, patrones[1])
            item.plot = scrapertools.remove_htmltags(realplot)
    return itemlist


def search(item,texto):
    logger.info()
    texto = texto.replace(" ","+")
    item.url = item.url+texto

    if texto!='':
        return lista(item)
    else:
        return []    

def findvideos(item):
    logger.info()
    itemlist=[]
    

    data=httptools.downloadpage(item.url).data
    data = re.sub(r"'|\n|\r|\t|&nbsp;|<br>", "", data)

    patron = 'class="servidor" alt=""> ([^<]+)<\/span><span style="width: 40px;">([^<]+)<\/span><a class="verLink" rel="nofollow" href="([^"]+)" target="_blank"> <img title="Ver online gratis"'
    matches = matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedidioma, scrapedcalidad, scrapedurl in matches:

    	scrapedidioma = scrapertools.decodeHtmlentities(scrapedidioma)
    	
    	scrapedcalidad = scrapertools.decodeHtmlentities(scrapedcalidad)
    	if scrapedidioma.lower() == 'español':
    	   scrapedidioma = 'castellano'
    	scrapedidioma = scrapedidioma.lower()
    	idioma = taudio[scrapedidioma.lower()]
    	calidad = tcalidad[scrapedcalidad.lower()]
    	url = scrapedurl
    	itemlist.append( Item(channel=item.channel, action='play' , idioma=idioma, calidad=calidad, url=url, lang = scrapedidioma, quality=scrapedcalidad.lower()))

    for videoitem in itemlist:
        videoitem.infoLabels=item.infoLabels
        videoitem.channel = item.channel
        videoitem.folder = False
        videoitem.thumbnail = servertools.guess_server_thumbnail(videoitem.url)
        videoitem.fulltitle = item.title
        videoitem.server = servertools.get_server_from_url(videoitem.url)
        videoitem.title = item.contentTitle+' | '+videoitem.calidad+' | '+videoitem.idioma+' ('+videoitem.server+')'

       

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

    user_config_setting = config.get_setting("default_action")  ### Guarda la accion del usuario ###
    config.set_setting("default_action", "2")                   ### Habilita la accion reproducir en calidad alta ###
    
    logger.debug (str(config.get_setting("default_action")))
    
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
    config.set_setting("default_action", user_config_setting)
    logger.debug (str(config.get_setting("default_action")))
    return itemlist


def newest(categoria):
    logger.info()
    itemlist = []
    item = Item()
    #categoria='peliculas'
    try:
        if categoria == 'peliculas':
            item.url = host
        elif categoria == 'infantiles':
            item.url = host+'/genero/infantil/'
        itemlist = lista(item)
        if itemlist[-1].title == 'Siguiente >>>':
                itemlist.pop()
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist

