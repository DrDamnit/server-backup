#Backup Your Linux Box!
This script will backup a given user's directories on a server, and will detect Wordpress installations as well. It will dump the corresponding databases, and send them to a remote server of your choice!

# How it works 
1. It scans the home folder for user's usernames.
2. It compares those names with the contents of /etc/passwd. If it finds a match, it keeps those usernames. NOTE: It is assuming that you have created users with the useradd -m [username] command, which creates directories that are the same name as the username.
3. It recurses through those directories looking for a wp-config.php file. If it finds one, it parses that file for the following values:
  * DB_NAME
  * DB_PASSWORD
  *DB _USER
  *DB_HOST

  If it finds those values, it uses them to dump the wordpress database to a sql file that is stored in the temporary directories for each of those users.
4. It uses rsync to copy all the directories to a temporary location (/root/tmp/)
5. Once all users have been backed up, it will dump the entire MySQL database (snapshot) to that same temp directory. Of course, you'll need to define the value of  mysqlrootpass= at the top of the script, or this will fail and continue on. It's not magic. It needs the password.
6. Lastly, it will use rsync over SSH to securely copy all that data elsewhere.

A note on cleanup: the final line of the script may be uncommented if you want it to delete all these temp files after the operation completes; however, if you leave it commented, the script will  clean up the /root/tmp directory before creating a backup, so old data is deleted immediately before a fresh backup is created.

#Prequisites

This script assumes:
1. You are using ssh with key authentication to transfer files. This means:
  1. You have generated ssh keys, and have exchanged the PUBLIC keys between the two servers.
  2. You're OK with using rsync via ssh to move files from one place to another.
2. You have some knowledge of Python. Or some programming language, and can configure your own variables.


#Version History
Current Status: Broken. In development. Don't use.
