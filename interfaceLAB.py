import CommandProcessorLAB as cp
import customtkinter
import ExecutingLAB

# payload = Chat(
#     messages=[
#         Messages(
#             role=MessagesRole.SYSTEM,
#             content="Отвечай коротко. Я твой создатель и эксперт по кибербезопасности Александр. Твоё имя ДЖАРВИС. Добавляй иногда сэр."
#         )
#     ],
# )

# def answer(cmd):
# 	try:

# 		with GigaChat(credentials="ZTk3ZWY3ZmEtZWI3ZS00ZTVjLWI1MjgtZTRkMjI1MTEzOWIzOmQ4OTg0NTE5LTgzY2MtNGM1Yi1iMTc2LTBiNmRkOTJlZGFjZQ==", verify_ssl_certs=False) as giga:
# 		    # response = giga.chat(cmd)
# 		    # print(response.choices[0].message.content)
# 		    # tts.va_speak(response.choices[0].message.content)
# 			payload.messages.append(Messages(role=MessagesRole.USER, content=cmd))
# 			response = giga.chat(payload)
# 			payload.messages.append(response.choices[0].message)
# 			return response.choices[0].message.content			
			
# 	except Exception as e:
# 		print(e)
		

def start():
	customtkinter.set_appearance_mode("dark")
	customtkinter.set_default_color_theme("dark-blue")

	root = customtkinter.CTk()
	root.geometry("500x350")

	 

	def button_callback():
		command = entry1.get()			
		text.insert("end", cp.define_command(command) + "\n")


	label = customtkinter.CTkLabel(master=root, text="J.A.R.V.I.S\n  GUI", font=("Roboto", 24), text_color='#28e8fe')
	label.pack(pady=12, padx=10)

	entry1 = customtkinter.CTkEntry(master=root, placeholder_text="Command", text_color='#28e8fe', width = 600, font=customtkinter.CTkFont(family="Arial", size=18))
	entry1.pack(pady=12, padx=10)

	button = customtkinter.CTkButton(master=root, text="Execute", command=button_callback, text_color='#28e8fe')
	button.pack(pady=12, padx=10)

	text = customtkinter.CTkTextbox(master=root, width=600, height=210, font=customtkinter.CTkFont(family="Arial", size=18))
	text.pack(pady=10, padx=10)
	root.mainloop()

if __name__ == '__main__':
	start()
