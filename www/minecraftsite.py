# 
#  minecraftsite.py
#  minecraftsite
#  
#  Created by Jay Roberts on 2010-08-25.
#  Copyright 2010 GloryFish.org. All rights reserved.
# 

import bottle
from bottle import route
import telnetlib

bottle.debug(True)

@route('/')
@route('/index.html')
@view('home')
def index():
    try:
        tel = telnetlib.Telnet('minecraft.gloryfish.org', 25565)
        server_status = True
    except:
        server_status = False

    return dict(status=server_status)

@route('/images/:filename')
def static_image(filename):
    bottle.send_file(filename, root='/var/www/minecraft.gloryfish.org/www/')