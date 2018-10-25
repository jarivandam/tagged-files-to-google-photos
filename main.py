#!/bin/python3
import os
import sys
import requests
import json
import csv

import google.oauth2.credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow


INFOLDER = sys.argv[1]
DESCRIPTION = sys.argv[2]
OUTFILE = sys.argv[3]


API_SERVICE_NAME = 'photoslibrary'
API_VERSION = 'v1'


def getToken():
    flow = InstalledAppFlow.from_client_secrets_file(
        'client_secret.json',
        scopes=['https://www.googleapis.com/auth/photoslibrary.appendonly', 'https://www.googleapis.com/auth/photoslibrary.sharing'])

    credentials = flow.run_local_server(host='localhost',
                                        port=8080,
                                        authorization_prompt_message='Please visit this URL: {url}',
                                        success_message='The auth flow is complete; you may close this window.',
                                        open_browser=True)
    return credentials.token


def files(path):
    for file in os.listdir(path):
        if os.path.isfile(os.path.join(path, file)):
            yield file


def findtagsandfiles(infolder):
    data = dict()
    for file in files(infolder):
        tag = file.split('-')[1]
        if tag in data:
            data[tag].append(file)
        else:
            data[tag] = [file]
    return data


def makealbum(token, name):
    data = {
        "album": {
            "title": name
        }
    }
    url = 'https://photoslibrary.googleapis.com/v1/albums'
    headers = {
        'Authorization': "Bearer " + token,
        'Content-Type': 'application/octet-stream',
    }

    r = requests.post(url, data=json.dumps(data), headers=headers)
    return r.content


def uploadfile(token, file):
    f = open(file, 'rb').read()

    url = 'https://photoslibrary.googleapis.com/v1/uploads'
    headers = {
        'Authorization': "Bearer " + token,
        'Content-Type': 'application/octet-stream',
        'X-Goog-Upload-File-Name': file,
        'X-Goog-Upload-Protocol': "raw",
    }

    r = requests.post(url, data=f, headers=headers)
    return r.content


def addToAlbum(token, album, upload_tokens):
    mediaItems = []
    for item in upload_tokens:
        mediaItem = {
            "description": DESCRIPTION,
            "simpleMediaItem": {
                "uploadToken": item
            }
        }
        mediaItems.append(mediaItem)

    data = {
        "albumId": album['id'],
        "newMediaItems": mediaItems
    }

    url = 'https://photoslibrary.googleapis.com/v1/mediaItems:batchCreate'
    headers = {
        'Authorization': "Bearer " + token,
        'Content-Type': 'application/octet-stream',
    }

    r = requests.post(url, data=json.dumps(data), headers=headers)
    return r.content


def shareAlbum(token, album):
    data = {
        "sharedAlbumOptions": {
            "isCollaborative": "true",
            "isCommentable": "true"
        }
    }

    url = 'https://photoslibrary.googleapis.com/v1/albums/' + \
        album['id']+':share'
    headers = {
        'Authorization': "Bearer " + token,
        'Content-Type': 'application/octet-stream',
    }

    r = requests.post(url, data=json.dumps(data), headers=headers)

    response = bytestodict(r.content)
    url = response['shareInfo']['shareableUrl']

    return url


def bytestodict(bytes):
    string = bytes.decode("utf-8")
    return json.loads(string)


def writetocsv(data):
    with open(OUTFILE, 'w', newline='') as csvfile:
        fieldnames = ['tag', 'url']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)


def main():
    data_dict = findtagsandfiles(INFOLDER)
    token = getToken()
    tagsandurls = []
    for tag in data_dict:
        album = bytestodict(makealbum(token, tag))
        uploads = []
        for photo in data_dict[tag]:
            res = uploadfile(token, INFOLDER + '/'+photo)
            uploads.append(res.decode("utf-8"))
        addToAlbum(token, album, uploads)
        url = shareAlbum(token, album)
        tagsandurls.append({'tag': tag, 'url': url})
    writetocsv(tagsandurls)
    print("Done")


if __name__ == '__main__':
    main()
