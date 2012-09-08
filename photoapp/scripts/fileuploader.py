import sys
import os
import getpass
import datetime

import requests

def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage:%s <url> <folder>\n' % cmd)

    sys.exit(1)


def getmtime(filename):
    return datetime.datetime.fromtimestamp(os.path.getmtime(filename))

def upload_files(url, auth, base_dir):
    
    logfile = os.path.expanduser(os.path.join("~", ".photoapp"))

    try:
        filenames = open(logfile).read().splitlines()
        logfile_last_modified = getmtime(logfile)
    except IOError:
        filenames = []
        logfile_last_modified = datetime.datetime.now()

    for path, dirs, files in os.walk(base_dir):

        for filename in files:
            if filename.lower().endswith(".jpg"):
                filename = os.path.basename(filename)
                name, ext = os.path.splitext(filename)
                rel_path = path[len(base_dir):]
                tags = rel_path.replace(os.path.sep, " ")

                full_path = os.path.join(path, filename)

                if full_path in filenames and getmtime(
                        full_path) < logfile_last_modified:
                    continue

                data = {'title' : name, 'tags' : tags}
                files = {"uploaded_file" : open(full_path, "rb")}

                resp = requests.put(url, data, files=files, auth=auth)
                print(full_path)
                filenames.append(full_path)

    open(logfile, "w").writelines("%s\n" % n for n in filenames)


def main(argv=sys.argv):

    if len(argv) != 3:
        usage(argv)

    url, base_dir = argv[1:]

    email = raw_input("Email address:").strip()
    if not email:
        usage(argv)

    password = getpass.getpass("Password:").strip()
    if not password:
        usage(argv)

    auth = requests.auth.HTTPBasicAuth(email, password)

    url = url + "/api/upload"

    upload_files(url, auth, base_dir)


