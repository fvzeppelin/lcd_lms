#! /usr/local/bin/python3

import re
import time
import sys
import logging
import argparse
import configparser
from socket import gethostname
from os.path import basename
import lcd
import lms

MAIN_LOOP_DELAY = 0.3

def config_init():
    global verbose
    verbose = False
    parse_arguments()
    if (verbose == True):
        logging.basicConfig(format='%(levelname)s: %(asctime)s %(message)s', level=logging.DEBUG)
    else:
        logging.basicConfig(format='%(levelname)s: %(asctime)s %(message)s', level=logging.WARNING)
    logging.debug('lmshost:lmsport=' + LMS + ':' + LMSPORT)
    logging.debug('lcdhost:lcdport=' + LCDD + ':' + LCDPORT)
    logging.debug('player=' + PLAYER)
    logging.debug('verbose=' + str(verbose))

def parse_config(configfile):
    global verbose
    global LCDD
    global LCDPORT
    global LMS
    global LMSPORT
    global PLAYER
    global STOP_KEY
    global PAUSE_KEY
    config = configparser.ConfigParser()
    config.read(configfile)
    if (config.has_section('LCD_LMS')):
        if (config.has_option('LCD_LMS','lms')):
            LMS = config['LCD_LMS']['lms'].split(':')[0]
            LMSPORT = config['LCD_LMS']['lms'].split(':')[1]
        if (config.has_option('LCD_LMS','lcd')):
            LCDD = config['LCD_LMS']['lcd'].split(':')[0]
            LCDPORT = config['LCD_LMS']['lcd'].split(':')[1]
        if (config.has_option('LCD_LMS','player')):
            PLAYER = config['LCD_LMS']['player']
        if (config.has_option('LCD_LMS','verbose')):
            verbose = config['LCD_LMS'].getboolean('verbose')
        if (config.has_option('LCD_LMS','verbose')):
            verbose = config['LCD_LMS'].getboolean('verbose')
        if (config.has_option('LCD_LMS','stop key')):
            STOP_KEY = config['LCD_LMS']['stop key']
        if (config.has_option('LCD_LMS','pause key')):
            PAUSE_KEY = config['LCD_LMS']['pause key']

def parse_arguments():
    global verbose
    global LCDD
    global LCDPORT
    global LMS
    global LMSPORT
    global PLAYER
    global STOP_KEY
    global PAUSE_KEY
    STOP_KEY = 'Enter'
    PAUSE_KEY = 'Down'
    parser = argparse.ArgumentParser(description='Glue the Logitech Media Server CLI to LCDd')
    parser.add_argument('-p', '--player', default=gethostname(), help='the client\'s player name')
    parser.add_argument('-d', '--lcdproc', default='localhost:13666', dest='lcdhost:lcdport', help='specify the LCDproc server')
    parser.add_argument('-l', '--lms', default='localhost:9090', dest='lmshost:lmsport', help='specify the LMS server')
    parser.add_argument('-c', '--config', help='specify a config file')
    parser.add_argument('-v', '--verbose', action='store_true', help='output debugging information')
    args = vars(parser.parse_args())
    if (args.get('verbose') == True):
        verbose = True
    LCDD = args.get('lcdhost:lcdport').split(':')[0]
    LCDPORT = args.get('lcdhost:lcdport').split(':')[1]
    LMS = args.get('lmshost:lmsport').split(':')[0]
    LMSPORT = args.get('lmshost:lmsport').split(':')[1]
    PLAYER = args.get('player')
    if (args.get('config') != None):
        parse_config(args.get('config'))

def centre(w, t):
    l = len(t)
    if (l > int(w)):
        return t
    a = int((int(w) - l) / 2)
    b = int(w) - l - a
    return (' ' * a) + t + (' ' * b)

def trim(s):
	s = re.sub('^\s+|\s+$', '', s)
	s = re.sub('"', '', s)
	return s

def set_title(ltitle):
    global title
    title = trim(ltitle)

def set_album(lalbum):
    global album
    album = trim(lalbum)

def multiline(s):
    t = ''
    l = ''
    length = 0
    for w in s.split():
        n = len(w)
        if (n + length < int(width)):
            if (length > 0):
                l = l + ' ' + w
                length += n + 1
            else:
                l = w
                length = n
        else:
            t = t + centre(width, l)
            l = w
            length = n
    return (t + centre(width, l))

def two_lines(l1, l2):
    myLcd.send_receive('widget_set ' + PLAYER + ' album 1 3 ' + width + ' 3 h 3 \"\"')
    if (len(l1) >= int(width) and len(l2) >= int(width)):
        s = multiline(l1 + ' ' + l2)
        myLcd.send_receive('widget_set ' + PLAYER + ' artist 1 2 ' + width + ' 2 h 3 \"\"')
        myLcd.send_receive('widget_set ' + PLAYER + ' title 1 1 ' + width + ' 3 v 8 \"' + s + '\"')
        return 1
    if (len(l1) >= int(width) and len(l2) == 0):
        t = multiline(l1)
        myLcd.send_receive('widget_set ' + PLAYER + ' artist 1 2 ' + width + ' 2 h 3 \"\"')
        myLcd.send_receive('widget_set ' + PLAYER + ' title 1 1 ' + width + ' 3 v 8 \"' + t + '\"')
        return 1
    if (len(l1) >= int(width)):
        t = multiline(l1)
        myLcd.send_receive('widget_set ' + PLAYER + ' title 1 1 ' + width + ' 2 v 8 \"' + t + '\"')
        a = centre(width, l2)
        myLcd.send_receive('widget_set ' + PLAYER + ' artist 1 3 ' + width + ' 3 h 3 \"' + a + '\"')
        return 1
    if (len(l2) >= int(width)):
        t = centre(width, l1)
        myLcd.send_receive('widget_set ' + PLAYER + ' title 1 1 ' + width + ' 1 h 3 \"' + t + '\"')
        a = multiline(l2)
        myLcd.send_receive('widget_set ' + PLAYER + ' artist 1 2 ' + width + ' 3 v 8 \"' + a + '\"')
        return 1
    return 0

def set_artist(artist):
    artist = trim(artist)
    if (title == '' and two_lines(album, artist)):
        return
    if (artist == '' and two_lines(title, album)):
        return
    if (album == '' and two_lines(title, artist)):
        return
    t = centre(width, title)
    a = centre(width, artist)
    l = centre(width, album)
    myLcd.send_receive('widget_set ' + PLAYER + ' title 1 1 ' + width + ' 1 h 3 \"' + t + '\"')
    myLcd.send_receive('widget_set ' + PLAYER + ' artist 1 2 ' + width + ' 2 h 3 \"' + a + '\"')
    myLcd.send_receive('widget_set ' + PLAYER + ' album 1 3 ' + width + ' 3 h 3 \"' + l + '\"')

def set_status(status):
	state = centre(10, status)
	myLcd.send_receive('widget_set ' + PLAYER + ' status 6 4 \"' + state + '\"')

def set_progress(current_track_id, total_tracks):
	p = ''
	if (total_tracks > 0):
		p = str(current_track_id + 1) + '/' + str(total_tracks)
		p = p[:6]
	myLcd.send_receive('widget_set ' + PLAYER + ' progress 15 4 \"' + p + '\"')

def set_elapsed_time():
	# duration is unknown for radio stream so just show elapsed time
    remain = current_duration - elapsed_time
    if (remain < 0):
        remain = -remain
    rh = int(remain / 3600)
    rm = int((remain - 3600 * rh) / 60)
    rs = int(remain % 60)
    t = ''
    if (rh > 0):
        t = str(rh) + ':' + str(rm).zfill(2) + ':' + str(rs).zfill(2) 
    else:
        t = str(rm) + ':' + str(rs).zfill(2)
    set_status(t)

def set_time():
    global start_time
    start_time = time.time() - int(float(elapsed_time))
    set_elapsed_time()

def set_volume(vol):
	if (vol == '100'):
		vol = '99'
	myLcd.send_receive('widget_set ' + PLAYER + ' volume 1 4 ' + vol.zfill(2))

def set_playing(lplaying):
    global elapsed_time
    global start_time
    global current_duration
    global playing
    playing = lplaying
    if (playing):
        start_time = time.time()
        myLcd.send_receive('screen_set ' + PLAYER + ' priority foreground backlight on')
        myLms.send_player('playlist tracks ?', player_id)
        myLms.send_player('playlist index ?', player_id)
    else:
        myLcd.send_receive('screen_set ' + PLAYER + ' priority background backlight off')
        if (current_duration > 0):
            current_duration -= elapsed_time
            elapsed_time = 0

def set_stopped():
	set_title('')
	set_album('')
	set_artist('')
	set_status('stop')
	set_playing(False)

def playlist(s):
    cmd = s[0]
    if (cmd == 'clear'):
        set_stopped()
        set_progress(-1, 0)
    elif (cmd == 'stop'):
        set_stopped()
    elif (cmd == 'pause'):
        if (s[-1] == '0'):
            set_playing(True)
        else:
            set_playing(False)
    elif (cmd == 'tracks'):
        set_progress(current_track_id, int(s[1]))
    elif (cmd == 'index'):
        set_progress(int(s[1]), total_tracks)
    elif (cmd == 'loadtracks'):
        myLms.send_player('playlist tracks ?', player_id)
    elif (cmd == 'addtracks'):
        myLms.send_player('playlist tracks ?', player_id)
    elif (cmd == 'load_done'):
        myLms.send_player('playlist tracks ?', player_id)
    elif (cmd == 'delete'):
        myLms.send_player('playlist tracks ?', player_id)
        myLms.send_player('playlist index ?', player_id)
    elif (cmd == 'newsong'):
        try:
            id = int(s[-1])
            if (playing and (id == current_track_id)):
                return
            myLms.send_player('duration ?', player_id)
            myLms.send_player('album ?', player_id)
            set_progress(id, total_tracks)
        except Exception as e:
            set_album('')
        set_playing(True)
        myLms.send_player('title ?', player_id)
        myLms.send_player('artist ?', player_id)

def mixer(cmd, vol):
    if (cmd == 'volume'):
        c = vol[0:1]
        if (c == '-' or c == '+'):
            myLms.send_player('mixer volume ?', player_id)
        else:
            set_volume(vol)

def mode(cmd):
    if (cmd == 'stop'):
        set_playing(False)
        set_status(cmd)
    elif (cmd == 'pause'):
        set_playing(False)
        set_status(cmd)
    elif (cmd == 'play'):
        set_playing(True)
        set_status(cmd)
        myLms.send_player('playlist tracks ?', player_id)

def lms_response(response):
    global current_duration
    global elapsed_time
    if (re.match(player_id + ' (.+)', response) != None):
        response = re.search(player_id + ' (.+)', response).group(1)
        s = response.split()
        if (s[0] == 'playlist'):
            del s[0]
            playlist(s)
        elif (s[0] == 'mixer'):
            del s[0]
            mixer(s[0], s[1])
        elif (s[0] == 'mode'):
            mode(s[1])
        elif (s[0] == 'time'):
            elapsed_time = int(float(s[1]))
            set_time()
        elif (s[0] == 'pause'):
            set_playing(False)
        elif (s[0] == 'play'):
            set_playing(True)
        elif (s[0] == 'artist'):
            del s[0]
            set_artist(' '.join(s))
        elif (s[0] == 'album'):
            del s[0]
            set_album(' '.join(s))
        elif (s[0] == 'title'):
            del s[0]
            set_title(' '.join(s))
        elif (s[0] == 'duration'):
            current_duration = int(float(s[1]))
            set_elapsed_time()

def set_clock_widget(w, l, s):
    s = centre(width, s)
    myLcd.send_receive('widget_set CLOCK ' + w + ' 1 ' + str(l) + ' \"' + s + '\"')

def lms_init():
    global myLms
    global player_id
    myLms = lms.Lms(LMS, LMSPORT)
    player_id = ''
    pcount = int(myLms.send_receive('player count'))
    for i in range(pcount):
        p = myLms.send_receive('player name ' + str(i))
        if (p == PLAYER):
            player_id = myLms.send_receive('player id ' + str(i))
            break
    if (player_id == ''):
        sys.exit('unable to find player ' + PLAYER)
    logging.info('player_id: ' + player_id)
    sub = "subscribe playlist,mixer,time,mode,play,pause,title,album,artist"
    if (listen):
        sub = "listen 1"
    myLms.send_receive(sub, True)
    myLms.send_player('mixer volume ?', player_id)
    myLms.send_player('mode ?', player_id)
    myLms.send_player('time ?', player_id)
    myLms.send_player('duration ?', player_id)
    myLms.send_player('playlist index ?', player_id)
    myLms.send_player('title ?', player_id)
    myLms.send_player('album ?', player_id)
    myLms.send_player('artist ?', player_id)

def lcd_init():
    global myLcd
    global width
    global lines
    myLcd = lcd.Lcd(LCDD, LCDPORT)
    lcdresponse = myLcd.send_receive('hello')
    width = re.search('wid\s+(\d+)', lcdresponse).group()[4:]
    lines = re.search('hgt\s+(\d+)', lcdresponse).group()[4:]
    myLcd.send_receive('client_set name ' + basename(sys.argv[0]))
    myLcd.send_receive('screen_add ' + PLAYER)
    myLcd.send_receive('screen_set ' + PLAYER + ' priority foreground name playback heartbeat off')
    myLcd.send_receive('widget_add ' + PLAYER + ' title scroller')
    myLcd.send_receive('widget_add ' + PLAYER + ' album scroller')
    myLcd.send_receive('widget_add ' + PLAYER + ' artist scroller')
    myLcd.send_receive('widget_add ' + PLAYER + ' volume string')
    myLcd.send_receive('widget_add ' + PLAYER + ' status string')
    myLcd.send_receive('widget_add ' + PLAYER + ' progress string')
    myLcd.send_receive('client_add_key ' + STOP_KEY)
    myLcd.send_receive('client_add_key ' + PAUSE_KEY)
    myLcd.send_receive('screen_add CLOCK')
    myLcd.send_receive('screen_set CLOCK priority info heartbeat off backlight off duration 1000')
    myLcd.send_receive('widget_add CLOCK time string')
    myLcd.send_receive('widget_add CLOCK day string')
    myLcd.send_receive('widget_add CLOCK date string')

start_time = time.time()
total_tracks = 0
current_track_id = -1
elapsed_time = 0
current_duration = 0
title = ''
artist = ''
album = ''
playing = False
listen = False
config_init()
lms_init()
lcd_init()

while True:
    loop_start = time.time_ns()
    response = myLms.check_queue()
    if (response != None):
        response = response.split("\n")
        for r in response:
            lms_response(r)
    response = myLcd.check_queue()
    if (response != None):
        if (response == 'key ' + STOP_KEY + '\n'):
            if (playing):
                myLms.send_player('playlist index +1', player_id)
            else:
                myLms.send_player('playlist clear', player_id)
        elif (response == 'key ' + PAUSE_KEY + '\n'):
            p = 0
            if (playing):
                p = 1
            myLms.send_player('pause ' + p, player_id)
    if (playing):
        elapsed_time = time.time() - start_time
        set_elapsed_time()
    set_clock_widget('day', 1, time.strftime('%A', time.localtime()))
    set_clock_widget('time', 2, time.strftime('%R', time.localtime()))
    set_clock_widget('date', 3, time.strftime('%d', time.localtime()) + ' ' + time.strftime('%b', time.localtime()) + ' ' + time.strftime('%Y', time.localtime()))
    delta = float(int(loop_start - time.time_ns())) / 1000000000.0 + MAIN_LOOP_DELAY
    logging.debug('main loop remaining time (delta in s): ' + str(delta))
    if (delta > 0):
        time.sleep(delta)
