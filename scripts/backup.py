#!/usr/bin/python

# 
#  backup.py
#  minecraftsite
#
#  Zips up a world directory and uploads it to an S3 bucket.
#  The first run creates a default config file.
#  
#  Created by Jay Roberts on 2010-10-15.
# 

import sys
import os
import ConfigParser
from StringIO import StringIO
from datetime import datetime
import zipfile
import boto

default_config = """
[backup]
world = worldname
mcpath = /path/to/mc
backuppath = /path/to/backups

[aws]
key = YOURKEY
secret = YOURSECRET
bucket = bucketname
"""

def zipdir(path, z):
    for root, dirs, files in os.walk(path):
        for f in files:
            z.write(os.path.join(root, f))
            
def updateprogress(current, total):
    message = "Uploading: %d%%" % int(float(current) * 100 / total)
    sys.stdout.write(message)
    sys.stdout.flush()
    sys.stdout.write("\b" * len(message))
    sys.stdout.flush()


if __name__ == '__main__':
    os.chdir(os.path.dirname(sys.argv[0]))
    
    # Load configuration
    try:
        config = ConfigParser.ConfigParser()
        config.readfp(StringIO(default_config))
    except ConfigParser.Error, cpe:
        print 'load_config(): ' + cpe

    if os.path.isfile('backup.ini'):
        print 'Found configuration, loading...'

        try:
            config.read('backup.ini')
        except ConfigParser.Error, cpe:
            print 'load_config(): ' + cpe
    else:
        try:
            config_file = open('backup.ini', 'w')
            config.write(config_file)
            print 'Default backup.ini created. Please edit and retry backup.'
            exit()
        except Exception, e:
            print 'load_config(): ' + e
        finally:
            config_file.close()

    # Zip up world directory

    # Format: worldname-20101051.zip
    filename = "%s-%s.zip" % (config.get('backup', 'world'), datetime.now().strftime('%Y%m%d-%H%M'))

    worlddir = config.get('backup', 'mcpath') + config.get('backup', 'world')

    print "Archiving %s" % worlddir
    
    z = zipfile.ZipFile(config.get('backup', 'backuppath') + filename, 'w')
    
    zipdir(worlddir, z)

    z.close()    

    print "Created %s" % filename    

    # Upload to S3
    print "Connecting to S3"
    conn = boto.connect_s3(aws_access_key_id=config.get('aws', 'key'), aws_secret_access_key=config.get('aws', 'secret'))

    bucket = conn.get_bucket(config.get('aws', 'bucket'))
    key = bucket.new_key(filename)
   
    print "Saving archive to bucket: %s" % config.get('aws', 'bucket')
    key.set_contents_from_filename(config.get('backup', 'backuppath') + filename, cb=updateprogress)    

    print "Backup complete."
