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
			text = "*температура на улице*"
		else:
			text = "*температура в комнтае*"
		return text

	elif command == 'humidity':
		text = "*влажность на улице*"
		return text

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
				text = "*синий светодиод включён*"
				print(text)
				return text
			elif args["color"] == "зелёный":
				text = "*зелёный светодиод включён*"
				return text
			elif args["color"] == "красный":
				text = "*красный светодиод включён*"
				return text
		elif args["object"] == "вентилят ##ор":
			text = "*вентилятор включён*"
			return text
		elif args["object"] == "музыку":
			text = "Какой-то праздник, сэр?"
			return text
			threadmus = Thread(target=music_player, args=(0,))
			threadmus.start()

	elif command == 'turn_off':
		if args["object"] == "свет":
			text = "*светодиод выключен*"
			return text
		elif args["object"] == "вентилят ##ор":
			text = "*вентилятор выключен*"
			return text
		elif args["object"] == "музыку":
			player.delete()
			pyglet.app.exit()
			text = "Неужели вечеринка окончена, сэр?"
			return text

	elif command == 'alarm':
		threadALARM = Thread(target=alarm, args=(args["time"],))
		threadALARM.start()
		text = "Готово, сэр. Сегодня точно не проспите"
		return text

	# elif command == 'notes':
	# 	if 'добавь' in cmd:
	# 		f = open('notes.txt', 'a')
	# 		for x in list:
	# 			cmd = cmd.replace(x, '').strip()
	# 		cmd += '\n'
	# 		f.write(cmd)
	# 		text = 'добавлено в заметки'
	# 		return text
	# 		f.close()

	# 	elif ('какие' in cmd) or ('что' in cmd):
	# 		f = open('notes.txt', 'r')
	# 		if os.path.getsize('notes.txt') == 0:
	# 			text = 'В заметках ничего нет'
	# 			return text
	# 		else:
	# 			text = 'В заметках \n'
	# 			for line in f:
	# 				return text + line.strip() + "\n"
	# 		f.close()

	# 	elif 'очисти' in cmd:
	# 		f = open('notes.txt', 'w')
	# 		text = 'Все заметки удалены'
	# 		return text
	# 		f.close()

	elif command == 'timer':
		text = "Таймер установлен на " + args["duration_num"] + " " + args["duration_unit"]
		return text

	elif command == 'news':
		text = "*читает новости*"
		return text

	if command == 'raspconnect':
		text = 'Подключаюсь...'
		return text
	
	elif command == 'token':
		text = "История очищена"
		return text

	elif command == 'work':
		text = "*WorkMode*"
		return text

	elif command == 'block':
		text = "блокирую систему"
		return text

	elif command == 'telesend':
		text = 'сообщение отправлено'
		return text