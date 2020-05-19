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
from subprocess import call
from pydub import AudioSegment

def createMp3(text):
    call(f'espeak --stdout -v fi -s 120 "{text}" | ffmpeg -i - -ar 44100 -ac 2 -ab 192k -f mp3 temp.mp3', shell=True)
    a = AudioSegment.from_mp3('temp.mp3')
    call('rm temp.mp3', shell=True)
    return a

def downloadMp3(url):
    res = requests.get(url)
    if res.ok:
        with open('temp.mp3', 'wb') as f:
            f.write(res.content)
        mp3 = AudioSegment.from_mp3('temp.mp3')
        call('rm temp.mp3', shell=True)
        return mp3
    else:
        print(f'Failed to get sound from {url}')

def compare(a, b):
    lenTarget = time.mktime(time.strptime('01:00', '%M:%S'))
    t1 = abs(time.mktime(time.strptime(a['length'], '%M:%S')) - lenTarget)
    t2 = abs(time.mktime(time.strptime(b['length'], '%M:%S')) - lenTarget)
    if t1 >  0 and t2 > 0:
        return t1 - t2
    else:
        return 0

data = pd.read_csv("lajit.csv", sep='\t')
for i, sp in enumerate(data['sci']):
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
            song = next(x for x in s if 'song' in x['type'])
            songMp3 = downloadMp3(f'https:{song["file"]}')
        except StopIteration:
            print(f'No sound for {data["fi"][i]}!')
        try:
            callD = next(x for x in s if 'call' in x['type'] and (song == None or x['id'] != song['id']))
            callMp3 = downloadMp3(f'https:{callD["file"]}')
        except StopIteration:
            print(f'No call for {data["fi"][i]}!')
        if songMp3 != None or callMp3 != None:
            mp3 += createMp3(data["fi"][i])
            mp3 += createMp3(sp)
            if songMp3 != None:
                mp3 += createMp3('Laulu')
                mp3 += songMp3
            if callMp3 != None:
                mp3 += createMp3('Kutsuääni')
                mp3 += callMp3
            mp3.export(f'{i}_{data["lyh"][i]}.mp3', format='mp3')
        print(f'Done with {data["fi"][i]}')
    else:
        print(f'Failed to get recordings for {data["fi"][i]}!')

print("Done!")
