import sys
import os
import bridge
import channelselector
from core import config
from core.item import Item
from core import channeltools
from core import servertools
from DumbTools import DumbKeyboard

#Añadimos "lib" al path
sys.path.append (os.path.join( config.get_runtime_path(), 'lib' ))

# Passing log and config to an external library
# Credits to https://gist.github.com/mikew/5011984
bridge.init(Log,Prefs,Locale)


###################################################################################################

PLUGIN_TITLE     = "pelisalacarta"
ART_DEFAULT      = "art-default.jpg"
ICON_DEFAULT     = "icon-default.png"

###################################################################################################
def Start():
    Plugin.AddPrefixHandler("/video/pelisalacarta", mainlist, PLUGIN_TITLE, ICON_DEFAULT, ART_DEFAULT)

    '''
    ViewModes = {"List": 65586, "InfoList": 65592, "MediaPreview": 458803, "Showcase": 458810, "Coverflow": 65591,
                 "PanelStream": 131124, "WallStream": 131125, "Songs": 65593, "Seasons": 65593, "Albums": 131123,
                 "Episodes": 65590,"ImageStream":458809,"Pictures":131123}
    '''
    Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")
    Plugin.AddViewGroup("List", viewMode="List", mediaType="items")
    Plugin.AddViewGroup("MediaPreview", viewMode="MediaPreview", mediaType="items")
    Plugin.AddViewGroup("Showcase", viewMode="Showcase", mediaType="items")
    Plugin.AddViewGroup("Coverflow", viewMode="Coverflow", mediaType="items")
    Plugin.AddViewGroup("PanelStream", viewMode="PanelStream", mediaType="items")
    Plugin.AddViewGroup("WallStream", viewMode="WallStream", mediaType="items")

    ObjectContainer.art        = R(ART_DEFAULT)
    ObjectContainer.title1     = PLUGIN_TITLE
    ObjectContainer.view_group = "InfoList"
    DirectoryObject.thumb      = R(ICON_DEFAULT)

    HTTP.CacheTime = CACHE_1DAY
    HTTP.Headers['User-Agent'] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:10.0.2) Gecko/20100101 Firefox/10.0.2"

####################################################################################################
@handler('/video/pelisalacarta', 'Pelisalacarta', art=ART_DEFAULT, thumb=ICON_DEFAULT)
def mainlist():
    oc = ObjectContainer(view_group="PanelStream")

    # TODO: Comprueba actualizaciones (hacer genérico core/updater.py)
    HTTP.Request("http://blog.tvalacarta.info/descargas/pelisalacarta-version.xml")

    # TODO: Menú completo (da un error extraño al leer el de channelselector.py)
    '''
    itemlist = channelselector.getmainlist()

    for item in itemlist:
        Log.Info("item="+repr(item))
        if item.channel=="configuracion":
            oc.add(PrefsObject(title=item.title,thumb=item.thumbnail))
        elif item.channel=="buscador":
            #oc.add(InputDirectoryObject(key=Callback(buscador),title=item.title,thumb=item.thumbnail,prompt = "Titulo del video"))
        else:
            oc.add(DirectoryObject(key=Callback(canal, channel_name=item.channel, action="mainlist"), title=item.title, thumb="http://pelisalacarta.mimediacenter.info/squares/"+item.channel+".png"))
    '''
    oc.add(DirectoryObject(key=Callback(canal, channel_name="novedades", action="mainlist"), title="Novedades", thumb="http://media.tvalacarta.info/pelisalacarta/squares/thumb_novedades.png"))
    oc.add(DirectoryObject(key=Callback(channels_list), title="Canales", thumb="http://media.tvalacarta.info/pelisalacarta/squares/thumb_canales.png"))
    oc.add(DirectoryObject(key=Callback(canal, channel_name="buscador", action="mainlist"), title='Buscador global', thumb="http://media.tvalacarta.info/pelisalacarta/squares/thumb_buscar.png"))
    oc.add(PrefsObject(title="Configuracion...",thumb="http://media.tvalacarta.info/pelisalacarta/squares/thumb_configuracion.png"))
    oc.add(DirectoryObject(key=Callback(canal, channel_name="ayuda", action="mainlist"), title="Ayuda", thumb="http://media.tvalacarta.info/pelisalacarta/squares/thumb_ayuda.png"))

    return oc

####################################################################################################
@route('/video/pelisalacarta/channels_list')
def channels_list():
    oc = ObjectContainer(view_group="PanelStream")

    '''
    oc.add(DirectoryObject(key=Callback(FrontPageList, name="Canales (Todos los idiomas)"), title="Canales (Todos los idiomas)", thumb="http://pelisalacarta.mimediacenter.info/squares/channelselector.png"))
    oc.add(DirectoryObject(key=Callback(FrontPageList, name="Buscador"), title="Buscador", thumb="http://pelisalacarta.mimediacenter.info/squares/buscador.png"))
    oc.add(DirectoryObject(key=Callback(ThemeList, name="Favoritos"), title="Favoritos"))
    oc.add(DirectoryObject(key=Callback(ThemeList, name="Descargas"), title="Descargas"))
    oc.add(DirectoryObject(key=Callback(ThemeList, name="Configuración"), title="Configuración"))
    oc.add(DirectoryObject(key=Callback(TagsList, name="Ayuda"), title="Ayuda t"))
    '''

    itemlist = channelselector.filterchannels(category="all")
    for item in itemlist:
        Log.Info("item="+repr(item))
        if item.channel not in ['tengourl']:
            oc.add(DirectoryObject(key=Callback(canal, channel_name=item.channel, action="mainlist", caller_item_serialized = item.tourl()), title=item.title, thumb=item.thumbnail))

    return oc

#
@route('/video/pelisalacarta/trailers')
def trailers(query=""):
    oc = ObjectContainer(view_group="List")
    oc.add(DirectoryObject(key=Callback(channels_list), title=Locale.LocalString("30033"), thumb="http://media.tvalacarta.info/pelisalacarta/squares/thumb_canales.png"))
    return oc

####################################################################################################
#/{channel_name}/{action}/{caller_item_serialized}
@route('/video/pelisalacarta/canal')
def canal(channel_name="",action="",caller_item_serialized=None, itemlist=""):
    oc = ObjectContainer(view_group="List")

    try:
        if caller_item_serialized is None:
            Log.Info("caller_item_serialized=None")
            caller_item = Item()
        else:
            Log.Info("caller_item_serialized="+caller_item_serialized)
            caller_item = Item()
            caller_item.fromurl(caller_item_serialized)
        Log.Info("caller_item="+str(caller_item))

        Log.Info("Importando...")
        channelmodule = servertools.get_channel_module(channel_name)
        Log.Info("Importado")

        Log.Info("Antes de hasattr")
        if hasattr(channelmodule, action):
            Log.Info("El módulo "+caller_item.channel+" tiene una funcion "+action)
            
            itemlist = getattr(channelmodule, action)(caller_item)

            if action=="play" and len(itemlist)>0 and isinstance(itemlist[0], Item):
                itemlist=play_video(itemlist[0])
            if action=="play" and len(itemlist)>0 and isinstance(itemlist[0], list):
                item.video_urls = itemlist
                itemlist=play_video(item)

        else:
            Log.Info("El módulo "+caller_item.channel+" *NO* tiene una funcion "+action)

            if action=="findvideos":
                Log.Info("Llamando a la funcion findvideos comun")
                itemlist=findvideos(caller_item)
            elif action=="play":
                itemlist=play_video(caller_item)
            elif action=="menu_principal":
                return mainlist()
             
        Log.Info("Tengo un itemlist con %d elementos" % len(itemlist))

        for item in itemlist:
            if item.action == "search"  and item.thumbnail == "":
              item.thumbnail = "http://media.tvalacarta.info/pelisalacarta/squares/thumb_buscar.png"
             
            try:
                Log.Info("item="+unicode( item.tostring(), "utf-8" , errors="replace" ))
            except:
                pass
            
            if action!="play":
                #if "type" in item and item.type == "input":
                if item.action == "control_text_click" or item.action == "search":
                    Log.Info("Canal: item tipo input")
                    if 'value' in item:
                        value = item.value
                    else:
                        value = ""
                        
                    if Client.Product in DumbKeyboard.clients:
                        DumbKeyboard("/video/pelisalacarta", oc, get_input,
                                dktitle = unicode( item.title, "utf-8" , errors="replace" ),
                                dkitem = item,
                                dkplaceholder = value,
                                dkthumb = item.thumbnail
                            )
                    else:
                        dkitem = item.tourl()
                        oc.add(InputDirectoryObject(
                                key    = Callback(get_input, dkitem = dkitem),
                                title  = unicode( item.title, "utf-8" , errors="replace" ),
                                prompt = value,
                                thumb = item.thumbnail
                            ))
                else:
                    oc.add(DirectoryObject(key=Callback(canal, channel_name=item.channel, action=item.action, caller_item_serialized=item.tourl()), title=unicode( item.title, "utf-8" , errors="replace" ), thumb=item.thumbnail))
            else:
                Log.Info("Llamando a la funcion play comun")
                videoClipObject = VideoClipObject(title=unicode( item.title, "utf-8" , errors="replace" ),thumb=item.thumbnail, url="pelisalacarta://"+item.url )
                oc.add(videoClipObject)

    except:
        Log.Info("Excepcion al ejecutar "+channel_name+"."+action)
        import traceback
        Log.Info("Detalles: "+traceback.format_exc())

    return oc

def resuelve(url):
    return Redirect(url)

def play_video(item):
    if item.video_urls:
      video_urls = item.video_urls
    else:
      video_urls = servertools.get_video_urls(item.server,item.url)
      
    itemlist = []
    for video_url in video_urls:
        itemlist.append( Item(channel=item.channel, action="play" , title="Ver el video "+video_url[0] , url=video_url[1], thumbnail=item.thumbnail, plot=item.plot, server=""))

    return itemlist

def findvideos(item):
    return servertools.find_video_items(item=item, channel=item.channel)

@route('/video/pelisalacarta/get_input')
def get_input(query, dkitem):
    Log.Info(query)
    if type(dkitem) == str:
        caller_item_serialized = dkitem
        dkitem = Item()
        dkitem.fromurl(caller_item_serialized)
    Log.Info("#########################################################")
    Log.Info(dkitem.tostring())
    
    if '.' in dkitem.channel:
        pack,modulo = dkitem.channel.split('.') #ejemplo: platformcode.platformtools
        channelmodule = channeltools.get_channel_module(modulo,pack)
    else:
        channelmodule = channeltools.get_channel_module(dkitem.channel)
    itemlist = getattr(channelmodule, dkitem.action)(dkitem, query)
    
    return canal(channel_name = dkitem.channel, action= "", itemlist = itemlist )

    
#return MessageContainer("Empty", "There aren't any speakers whose name starts with " + char)
#return ObjectContainer(header="Empty", message="There aren't any items")
#oc.add(SearchDirectoryObject(identifier='com.plexapp.plugins.amt', title='Search Trailers', prompt='Search for movie trailer', term=L('Trailers')))