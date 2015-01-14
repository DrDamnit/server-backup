#!/usr/bin/python
import os
import logging
import re
import getpass

if not getpass.getuser() == 'root':
        sys.exit("You must run this script as root. Quitting.")

logging.basicConfig(level=logging.DEBUG,format='%(asctime)s %(levelname)s %(message)s',filename='/var/log/server-backup.log',filemode='w')
logging.info("Starting up...")

def logit(message):
    print message
    logging.info(message)
    return

def discoverWP(user):
    root = "/home/"+user
    for root,dirs,files in os.walk(root):
        for f in files:
            if f=="wp-config.php":
                configPath = os.path.join(root,f)
                logit("Wordpress Config Found: %s" % configPath)
                getWPSetting(configPath)

#Returns a dictionary of key value paris with the Wordpress database credentials and information
def getWPSetting(path):
    creds = {}
    if not os.path.exists(path):
        logging.warning("Could not parse % the file does not exist?" % path)
        return False

    #Read the file into memory
    f = open(path)
    searchlines = f.readlines();
    f.close()

    vars = ["DB_NAME","DB_USER", "DB_PASSWORD","DB_HOST"]
    for v in vars:
        logit("\nSearching for variable: %s" % v)
        for line in searchlines:
            line = line.rstrip('\n')
            if v in line:
                logit("Found Wordpress Setting. %s=%s" % (v,line))
                #Parse out the value
                #Using Regex: r"define\([ ]{0,1}'DB_NAME',[ ]{0,1}'([a-zA-Z0-9_-]*)'[ ]{0,1}\);"
                pattern = "define\([ ]{0,1}'%s',[ ]{0,1}'([a-zA-Z0-9_-]*)'[ ]{0,1}\);" % v
                logit("Parsing for: %s" % v)
                result = re.search(pattern,line)
                if not result == None:
                    print "Parsed Result: %s" % result.group(1)
                    kv = {v:result.group(1)}
                    creds.append(kv)



root = "/home/"
users=[]
for d in os.listdir(root):
        path = os.path.join(root,d)
        if os.path.isdir(path):
            logit("Adding %s to users list." % d)
            users.append(d)

logging.info("Loading /etc/passwd...")
#Open /etc/passwd so we can verify usernames.
f = open("/etc/passwd","r")
searchlines = f.readlines()
f.close()

for u in users:
    logit("Verifying: %s" % u)
    kill = True
    for i, line in enumerate(searchlines):
        if u in line:
            kill=False
            logit("%s is in /etc/passwd. Keeping them." % u)
    if kill:
        logit("%s was not in /etc/passwd. We're not backing that up." %u)
        users.remove(u)

for u in users:
    discoverWP(u)
