import random
import config
import datetime
import time
import os
import pyglet
from threading import Thread, Event
import webbrowser as wb
import re
import schedule
import plyer
from sound import Sound


def mp3(variant: int):
	if variant == 2:
		path='music'
		for root,dirs,files in os.walk(path):
			for filename in files:
				if os.path.isfile(os.path.join(root, filename)):
					if filename.endswith(".mp3"):
						yield os.path.join(root, filename)

def run_continuously(interval=1):
    cease_continuous_run = Event()

    class ScheduleThread(Thread):
        @classmethod
        def run(cls):
            while not cease_continuous_run.is_set():
                schedule.run_pending()
                time.sleep(interval)

    continuous_thread = ScheduleThread()
    continuous_thread.start()
    return cease_continuous_run

def music_player(type: int):
	global player
	if type == 0:
		a=[song for song in mp3(2)]
		player = pyglet.media.Player()
		for i in range(len(a)):
			track=random.choice(a)
			song = pyglet.media.load(track)
			player.queue(song)
			print(track)
		player.play()
		pyglet.app.run()

	elif type == 1:
		player = pyglet.media.Player()
		song = pyglet.media.load('music/alarm.mp3')
		player.queue(song)
		player.play()
		pyglet.app.run()

def alarm(hour):
	def greeting():
		#info from modules add
		threadalarm = Thread(target=music_player, args=(1,))
		threadalarm.start()
		now = datetime.datetime.now()
		text = "Доброе утро, сэр. Сейчас в Минске" + num2words(now.hour, lang='ru') + " часов " + num2words(now.minute, lang='ru') + " минут... "
		if weather.chkwthr() == 404:
			tts.va_speak("Ошибка. не могу получить доступ к серверу")
		else:
			weathernow = "Сейчас на улице " + num2words(weather.chkwthr(), lang='ru') + " градусов. "
			if weather.chkwthr() <= 10:
				weathernow += "оденься теплее."
			elif weather.chkwthr() >= 24:
				weathernow += "жарковато."
			else:
				weathernow += "Вполне комфортно."
		phrase = text + weathernow
		tts.va_speak(phrase)
		

	# if int(hour) > 9:
	# 	time = hour + ":00"
	# else:
	# 	time = '0' + hour + ':00'
	print(time)
	schedule.every().day.at(int(hour)).do(greeting)
	global stop_run_continuously
	stop_run_continuously = run_continuously()

def chatGPT_callback(args):
	print(args)


def execute_command(command, args):
	print(command)
	print(args)
	if command == 'time':
		now = datetime.datetime.now()
		text = "Сейчас " + str(now.hour) + ":" + str(now.minute)
		print(text)
		return text

	elif command == 'search':
		print(args["query"])
		firefox = 'C:/Program Files/Mozilla Firefox/firefox.exe %s'
		wb.get(firefox).open("http://www.google.com/search?q=" + args["query"]) #https://yandex.by/search/?text=

	elif command == 'temperature':
		TempLocList = ["дома", "тут", "в квартире", "в комнате"]
		if args["location"] == None or args["location"] not in TempLocList:
			return "*температура на улице*"
		else:
			return "*температура в комнтае*"

	elif command == 'humidity':
		return "*влажность на улице*"

	elif command == 'thanks':
		rates = ['Всегда пожалуйста', 'Буду стараться и дальше', 'взаимно', 'Я польщён, сэр']
		return random.choice(rates)

	elif command == 'sound':
		Sound.mute()

	elif command == 'volume':
		if args["value"] == None:
			if args["direction"] == "down":
				Sound.volume_down()
			else:
				Sound.volume_up()
		else:
			if args["direction"] == "down":
				Sound.volume_down(int(args["value"]))
			else:
				Sound.volume_up(int(args["value"]))

	elif command == 'turn _on':
		if args["object"] == "свет":
			if args["color"] == "синий":
				return "*синий светодиод включён*"
			elif args["color"] == "зелёный":
				return "*зелёный светодиод включён*"
			elif args["color"] == "красный":
				return "*красный светодиод включён*"
		elif args["object"] == "вентилят ##ор":
			return "*вентилятор включён*"
		elif args["object"] == "музыку":
			return "Какой-то праздник, сэр?"
			threadmus = Thread(target=music_player, args=(0,))
			threadmus.start()

	elif command == 'turn_off':
		if args["object"] == "свет":
			weather.light(0)
			return "*светодиод выключен*"
		elif args["object"] == "вентилят ##ор":
			weather.light(5)
			return "*вентилятор выключен*"
		elif args["object"] == "музыку":
			player.delete()
			pyglet.app.exit()
			return "Неужели вечеринка окончена, сэр?"

	elif command == 'alarm':
		threadALARM = Thread(target=alarm, args=(args["time"],))
		threadALARM.start()
		return "Готово, сэр. Сегодня точно не проспите"

	elif command == 'notes':
		if 'добавь' in cmd:
			f = open('notes.txt', 'a')
			for x in list:
				cmd = cmd.replace(x, '').strip()
			cmd += '\n'
			f.write(cmd)
			return 'добавлено в заметки'
			f.close()

		elif ('какие' in cmd) or ('что' in cmd):
			f = open('notes.txt', 'r')
			if os.path.getsize('notes.txt') == 0:
				return 'В заметках ничего нет'
			else:
				return 'В заметках \n'
				for line in f:
					return line.strip() + "\n"
			f.close()

		elif 'очисти' in cmd:
			f = open('notes.txt', 'w')
			return 'Все заметки удалены'
			f.close()

	elif command == 'timer':
		return "Таймер установлен на " + args["duration_num"] + " " + args["duration_unit"]

	elif command == 'news':
		return "*читает новости*"

	if command == 'raspconnect':
		return 'Подключаюсь...'
	
	elif command == 'token':
		return "История очищена"

	elif command == 'work':
		return "*WorkMode*"

	elif command == 'block':
		return "блокирую систему"

	elif command == 'telesend':
		return 'сообщение отправлено'