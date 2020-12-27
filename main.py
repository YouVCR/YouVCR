#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from google.oauth2.credentials import Credentials
import yaml
import json
import sys
import pathlib
import time
from multiprocessing import Process
import youtube_dl


def get_credential():
    credential = None
    if os.path.exists('credential.json'):
        with open('credential.json', 'r') as cred_file:
            saved_credential = json.load(cred_file)
            credential = Credentials(saved_credential['token'],
                refresh_token = saved_credential['refresh_token'],
                token_uri = saved_credential['token_uri'],
                client_id = saved_credential['client_id'],
                client_secret = saved_credential['client_secret'],
                scopes = saved_credential['scopes'])
    else:
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            "client_secret.json",
            ["https://www.googleapis.com/auth/youtube.readonly"])
        credential = flow.run_console()
        with open('credential.json', 'w') as cred_file:
            cred_file.write(credential.to_json())
    return credential

def get_config():
    with open('config.yaml', 'r') as stream:
        try:
            config = yaml.safe_load(stream)
            interval = config.get('interval')
            if interval is None or type(interval) != int:
                return None, '`interval` must be a positive integer'
            channels = config.get('channels', [])
            if type(channels) != list:
                return None, '`channels` must be a list'
            for c in channels:
                if type(c.get('id')) != str:
                    return None, '`chennels[].id must be a string'
                save_to = c.get('save_to')
                if type(save_to) == str:
                    try:
                        pathlib.Path(save_to).mkdir(parents=True, exist_ok=True)
                    except:
                        return None, '`channels[].save_to must be a writable directory path'
                else:
                    return None, '`channels[].save_to must be a writable directory path'
            return config, None
        except yaml.YAMLError as exc:
            return None, 'Cannot load config.yaml'

def record_live_stream(video_id, save_to, title):
    url = f'https://www.youtube.com/watch?v={video_id}'
    print(f'[INFO] start recording {title}: {url}')
    os.chdir(os.path.join(os.getcwd(), save_to))
    with youtube_dl.YoutubeDL() as ytb_dl:
        ytb_dl.download([url])

def main():
    config, err = get_config()
    if err is not None:
        print(f'[ERROR] {err}')
        sys.exit(1)
    print(config)
    credential = get_credential()
    youtube = googleapiclient.discovery.build('youtube', 'v3',
        credentials=credential)
    recorders = {}

    while True:
        for c in config['channels']:            
            request = youtube.search().list(
                part='snippet',
                channelId=c['id'],
                eventType='live',
                type='video',
                forMine=True,
            )
            response = request.execute()
            items = response.get('items', [])
            for item in items:
                video_id = item['id']['videoId']
                if recorders.get(video_id) is None:
                    recorders[video_id] = True
                    p = Process(target=record_live_stream, 
                        args=(video_id, c['save_to'], item['snippet']['title']))
                    p.start()
        time.sleep(config['interval'])
        new_config, err = get_config()
        if err is not None:
            print(err)
        else:
            config = new_config

if __name__ == "__main__":
    main()
