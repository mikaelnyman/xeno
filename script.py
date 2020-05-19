#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 19 10:39:04 2020

@author: mikael
"""

import pandas as pd
import requests
from functools import cmp_to_key
import time
from subprocess import call, DEVNULL
from pydub import AudioSegment, exceptions
import os.path
from multiprocessing import Pool

def createMp3(text, i=0):
    call(f'espeak --stdout -v fi -a 150 -s 120 "{text}" | ffmpeg -i - -ar 44100 -ac 2 -ab 192k -f mp3 temp{i}.mp3', shell=True, stderr=DEVNULL)
    a = AudioSegment.from_mp3(f'temp{i}.mp3')
    call(f'rm temp{i}.mp3', shell=True)
    return a

def downloadMp3(url, i):
    res = requests.get(url)
    if res.ok:
        with open(f'temp{i}.mp3', 'wb') as f:
            f.write(res.content)
        try:
            return AudioSegment.from_mp3(f'temp{i}.mp3')
        except exceptions.CouldntDecodeError:
            print(f'Failed to decode sound {i} from {url}')
        finally:
            call(f'rm temp{i}.mp3', shell=True)
    else:
        print(f'Failed to get sound {i} from {url}')

def compare(a, b):
    try:
        lenTarget = time.mktime(time.strptime('01:00', '%M:%S'))
        t1 = abs(time.mktime(time.strptime(a['length'], '%M:%S')) - lenTarget)
        t2 = abs(time.mktime(time.strptime(b['length'], '%M:%S')) - lenTarget)
        return t1 - t2
    except ValueError:
        return 0

def create(i, sp):
    if not os.path.isfile(f'{i}_{data["lyh"][i]}.mp3'):
        mp3 = AudioSegment.empty()
        res = requests.get(f'https://www.xeno-canto.org/api/2/recordings?query={sp.replace(" ", "+")}+q:A')
        if res.ok:
            js = res.json()
            s = sorted(js['recordings'], key=cmp_to_key(compare))
            song = None
            songMp3 = None
            callD = None
            callMp3 = None
            try:
                song = next(x for x in s if 'song' in x['type'] and not x['file'] == "")
                songMp3 = downloadMp3(f'https:{song["file"]}', i)
            except StopIteration:
                print(f'No sound for {data["fi"][i]}!')
            try:
                callD = next(x for x in s if 'call' in x['type'] and (song == None or x['id'] != song['id']) and not x['file'] == "")
                callMp3 = downloadMp3(f'https:{callD["file"]}', i)
            except StopIteration:
                print(f'No call for {data["fi"][i]}!')
            if songMp3 != None or callMp3 != None:
                name = createMp3(data["fi"][i], i)
                mp3 += createMp3(sp, i)
                if songMp3 != None:
                    mp3 += name
                    mp3 += laulu
                    mp3 += songMp3
                if callMp3 != None:
                    mp3 += name
                    mp3 += kutsu
                    mp3 += callMp3
                mp3.export(f'{i}_{data["lyh"][i]}.mp3', format='mp3')
                print(f'Done with {data["fi"][i]}')
        else:
            print(f'Failed to get recordings for {data["fi"][i]}!')

data = pd.read_csv("lajit.csv", sep='\t')
laulu = createMp3('Laulu')
kutsu = createMp3('Kutsuääni')
with Pool(20) as p:
    p.starmap(create, enumerate(data['sci']))

print("Done!")
