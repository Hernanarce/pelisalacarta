# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Logger
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------
import bridge

def get_caller(message=None):
    import inspect
    module = "pelisalacarta."  + inspect.getmodule(inspect.currentframe().f_back.f_back).__name__
    #function = inspect.currentframe().f_code.co_name
    function = inspect.currentframe().f_back.f_back.f_code.co_name
    #bridge.log_info(module)
    if message:
        if module not in message:
            if function == "<module>":
                return module + " " + message
            else:
                return module + " [" + function + "] " + message
        else:
            return message

    else:
        if function == "<module>":
            return module
        else:
            return module + "." + function


def info(texto=""):
    try:
        bridge.log_info(get_caller(texto))
    except:
        pass
    
def debug(texto=""):
    try:
        bridge.log_info("######## DEBUG #########",'Debug')
        bridge.log_info(get_caller(texto),'Debug')
    except:
        pass

def error(texto=""):
    try:
        bridge.log_info("######## ERROR #########",'Error')
        bridge.log_info(get_caller(texto),'Error')
    except:
        pass
