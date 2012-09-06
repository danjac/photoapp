import sys
import os
import getpass

import requests

def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage:%s <url> <folder>\n' % cmd)

    sys.exit(1)


def upload_files(url, auth, base_dir):
    
    for path, dirs, files in os.walk(base_dir):

        for filename in files:
            if filename.lower().endswith(".jpg"):
                filename = os.path.basename(filename)
                name, ext = os.path.splitext(filename)
                rel_path = path[len(base_dir):]
                tags = rel_path.replace(os.path.sep, " ")

                full_path = os.path.join(path, filename)
                print(full_path)

                data = {'title' : name, 'tags' : tags}
                files = {"uploaded_file" : open(full_path, "rb")}

                resp = requests.post(url, data, files=files, auth=auth)


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


