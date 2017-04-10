# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# Canal (seodiv) por Hernan_Ar_c
# ------------------------------------------------------------

<<<<<<< Temporary merge branch 1
import urlparse, urllib2, urllib, re
import os, sys

from core import logger
=======
import re

>>>>>>> Temporary merge branch 2
from core import config
from core import httptools
from core import logger
from core import servertools
from core import scrapertools
from core.item import Item
from core import servertools
from core import httptools
from channels import autoplay
from channels import filtertools

IDIOMAS = {'latino': 'Latino'}
list_languages = IDIOMAS.values()

host = 'http://www.seodiv.com'


def mainlist(item):
    logger.info()

    itemlist = []

    itemlist.append(
            Item(channel=item.channel,
                 title="Todos",
                 action="todas",
                 url=host,
                 thumbnail='https://s32.postimg.org/544rx8n51/series.png',
                 fanart='https://s32.postimg.org/544rx8n51/series.png',
                 language='latino'
                 ))
    return itemlist


def todas(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r'"|\n|\r|\t|&nbsp;|<br>|\s{2,}', "", data)
    logger.debug(data)
    patron = '<div class=shortf><div><div class=shortf-img><a href=(.*?)><img src=(.*?) alt=.*?quality>(' \
             '.*?)<.*?series transition>(.*?) <\/span>'

    matches = re.compile(patron, re.DOTALL).findall(data)
    for scrapedurl, scrapedthumbnail, scrapedcalidad, scrapedtitle in matches:
        url = host + scrapedurl
        calidad = scrapedcalidad
        title = scrapedtitle.decode('utf-8')
        thumbnail = scrapedthumbnail
        fanart = 'https://s32.postimg.org/gh8lhbkb9/seodiv.png'

        itemlist.append(
                Item(channel=item.channel,
                     action="temporadas",
                     title=title, url=url,
                     thumbnail=thumbnail,
                     fanart=fanart,
                     contentSerieName=title,
                     extra='',
                     language=item.language,
                     quality='default'
                     ))

    return itemlist


def temporadas(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    logger.debug(data)
    url_base = item.url
    patron = '<a class="collapsed" data-toggle="collapse" data-parent="#accordion" href=.*? aria-expanded="false" ' \
             'aria-controls=.*?>([^<]+)<\/a>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    temp = 1
    if 'Temporada' in str(matches):
        for scrapedtitle in matches:
            url = url_base
            tempo = re.findall(r'\d+', scrapedtitle)
            if tempo:
                title = 'Temporada' + ' ' + tempo[0]
            else:
                title = scrapedtitle.lower()
            thumbnail = item.thumbnail
            plot = item.plot
            fanart = scrapertools.find_single_match(data, '<img src="([^"]+)"/>.*?</a>')
            itemlist.append(
                    Item(channel=item.channel,
                         action="episodiosxtemp",
                         title=title,
                         fulltitle=item.title,
                         url=url,
                         thumbnail=thumbnail,
                         plot=plot, fanart=fanart,
                         temp=str(temp),
                         contentSerieName=item.contentSerieName,
                         language=item.language,
                         quality=item.quality
                         ))
            temp = temp + 1

        if config.get_library_support() and len(itemlist) > 0:
            itemlist.append(
                    Item(channel=item.channel,
                         title='[COLOR yellow]Añadir esta serie a la biblioteca[/COLOR]',
                         url=item.url,
                         action="add_serie_to_library",
                         extra="episodios",
                         contentSerieName=item.contentSerieName,
                         extra1=item.extra1,
                         temp=str(temp)
                         ))
        return itemlist
    else:
        itemlist = episodiosxtemp(item)
        if config.get_library_support() and len(itemlist) > 0:
            itemlist.append(
                    Item(channel=item.channel,
                         title='[COLOR yellow]Añadir esta serie a la biblioteca[/COLOR]',
                         url=item.url,
                         action="add_serie_to_library",
                         extra="episodios",
                         contentSerieName=item.contentSerieName,
                         extra1=item.extra1,
                         temp=str(temp)
                         ))
        return itemlist


def episodios(item):
    logger.info()
    itemlist = []
    templist = temporadas(item)
    for tempitem in templist:
        logger.debug(tempitem)
        itemlist += episodiosxtemp(tempitem)

    return itemlist


def episodiosxtemp(item):
<<<<<<< Temporary merge branch 1
    logger.debug("pelisalacarta.channels.seodiv episodiosxtemp")
=======
    
    logger.info()
>>>>>>> Temporary merge branch 2
    itemlist = []
    data = httptools.downloadpage(item.url).data
    tempo = item.title
    if 'Temporada' in item.title:
        item.title = item.title.replace('Temporada', 'temporada')
        item.title = item.title.strip()
        item.title = item.title.replace(' ', '-')

    patron = '<li><a href="([^"]+)">.*?(Capitulo|Pelicula).*?([\d]+)'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtipo, scrapedtitle in matches:
        url = host + scrapedurl
        plot = item.plot

        if 'temporada' in item.title and item.title in scrapedurl and scrapedtipo == 'Capitulo' and item.temp != '':
            title = item.contentSerieName + ' ' + item.temp + 'x' + scrapedtitle
            itemlist.append(
                    Item(channel=item.channel,
                         action="findvideos",
                         title=title,
                         fulltitle=item.fulltitle,
                         url=url,
                         thumbnail=item.thumbnail,
                         plot=plot,
                         language=item.language,
                         quality=item.quality,
                         contentSerieName=item.contentSerieName,
                         idioma=idioma
                         ))

        if 'temporada' not in item.title and item.title not in scrapedurl and scrapedtipo == 'Capitulo' and item.temp\
                == '':
            if item.temp == '': temp = '1'
            title = item.contentSerieName + ' ' + temp + 'x' + scrapedtitle
            if '#' not in scrapedurl:
                itemlist.append(
                    Item(channel=item.channel,
                         action="findvideos",
                         title=title,
                         fulltitle=item.fulltitle,
                         url=url,
                         thumbnail=item.thumbnail,
                         plot=plot,
                         language=item.language,
                         quality=item.quality,
                         contentSerieName=item.contentSerieName
                         ))

        if 'temporada' not in item.title and item.title not in scrapedurl and scrapedtipo == 'Pelicula':
            title = scrapedtipo + ' ' + scrapedtitle
            itemlist.append(
                    Item(channel=item.channel,
                         action="findvideos",
                         title=title,
                         fulltitle=item.fulltitle,
                         url=url,
                         thumbnail=item.thumbnail,
                         plot=plot,
                         language=item.language,
                         list_languages=list_languages,
                         context=autoplay.context,
                         contentSerieName=item.contentSerieName
                         ))

    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    logger.debug(data)
    video_items = servertools.find_video_items(item)

    for videoitem in video_items:
        videoitem.thumbnail = servertools.guess_server_thumbnail(videoitem.server)
        videoitem.language = scrapertools.find_single_match(data, '<span class="f-info-title">Idioma:<\/span>\s*<span '
                                                                  'class="f-info-text">(.*?)<\/span>')
        videoitem.title = item.contentSerieName + ' (' + videoitem.server + ') (' + videoitem.language + ')'
        videoitem.quality = 'default'
        videoitem.context = autoplay.context
        itemlist.append(videoitem)

    # Requerido para FilterTools

    if len(itemlist) > 0 and filtertools.context:
        itemlist = filtertools.get_links(itemlist, item.channel)

    # Requerido para AutoPlay

    if config.get_setting("autoplay", item.channel) and autoplay.context:
        autoplay.start(itemlist, item)

    return itemlist

import urlparse, urllib2, urllib, re
import os, sys

from core import logger
    logger.debug("pelisalacarta.channels.seodiv episodiosxtemp")