#!/usr/bin/python
import os
import logging
import re
import getpass
import time
import datetime
import shutil

mysqlrootpass=[CHANGETHIS]
sitename=[CHANGETHIS]
servername=[CHANGETHIS]
remoteserver=[CHANGETHIS]

if not getpass.getuser() == 'root':
        sys.exit("You must run this script as root. Quitting.")

logging.basicConfig(level=logging.DEBUG,format='%(asctime)s %(levelname)s %(message)s',filename='/var/log/server-backup.log',filemode='w')
logging.info("Starting up...")

def logit(message):
    print message
    logging.info(message)
    return

def dumpDB(Credentials,user):
    filename = time.strftime("%Y-%m-%d_%H-%M-%S.sql",time.gmtime())
    backupdir = "/home/%s/%s/" % (user,'backup')
    backupfile = os.path.join(backupdir,filename)
    if not os.path.exists(backupdir):
        logit("Backup directory %s does not exist. Creating it." % backupdir)
        os.makedirs(backupdir)
        if os.path.exists(backupdir):
            logit("Backup directory %s was created, and exists... changing ownership to: %s:%s" % (backupdir,user,user))
            cmd = "chown -R %s:%s %s" % (user,user,backupdir)
            os.system(cmd)
    #Clean out the previous backups.
    for f in os.listdir(backupdir):
        if f.endswith(".sql"):
            logit("Removing old sql backup: %s" % os.path.join(backupdir,f))
            os.remove(os.path.join(backupdir,f))

    cmd = "mysqldump --databases %s -u%s -p%s > %s" % (Credentials['DB_NAME'], Credentials['DB_USER'], Credentials['DB_PASSWORD'],backupfile)
    logit("Dumping with command: %s" % cmd)
    os.system(cmd)

def discoverWP(user):
    root = "/home/"+user
    for root,dirs,files in os.walk(root):
        for f in files:
            if f=="wp-config.php":
                configPath = os.path.join(root,f)
                logit("Wordpress Config Found: %s" % configPath)
                Credentials = getWPSetting(configPath)
                logit("------------------------------")
                logit("User: %s" % Credentials['DB_USER'])
                logit("Pass: %s" % Credentials['DB_PASSWORD'])
                logit("Server: %s" % Credentials['DB_HOST'])
                logit("Database: %s" % Credentials['DB_NAME'])
                logit("------------------------------")
                dumpDB(Credentials,user)



#Returns a dictionary of key value paris with the Wordpress database credentials and information
def getWPSetting(path):
    creds = []
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
                    logit("Parsed Result: %s" % result.group(1))
                    creds.append((v,result.group(1)))
    Credentials=dict(creds)
    return Credentials



root = "/home/"
backupdir = '/root/tmp/'
if not os.path.exists(backupdir):
    os.makedirs(backupdir)
else:
    #Clean up old files
    for f in os.listdir(backupdir):
        x = os.path.join(backupdir,f)
        print "Removing: %s" % x
        os.remove(x)

#Set Backup Timesta
ts = time.strftime("%Y-%m-%d_%H-%M-%S",time.gmtime())

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

#Dump the Wordpress Databases
for u in users:
    discoverWP(u)

    #Tar up all the user profiles to a specified location.
    cmd = "tar -zcvf /root/tmp/%s-%s.tar.gz /home/%s " % (u,ts,u)
    #cmd = "tar -zcvf /home/%s /root/tmp/%s-%s.tar.gz" % (u,u,ts)
    print "Executing: %s" % cmd
    os.system(cmd)


#Do a full database dump to the same location
cmd = "mysqldump --all-databases -uroot -p%s > /root/tmp/fulldump-%s.sql" % (mysqlrootpass,ts)
os.system(cmd)

#Transfer offsite for safe keeping
cmd = "rsync -Pravdtze ssh /root/tmp/* %s:/mnt/raid/backups/%s/%s-%s" % (remoteserver,sitename,servername,ts)
print "Running command: %s" % cmd
os.system(cmd)

#cleanup
#shutil.rmtree('/root/tmp/')
