import os
import subprocess
import customtkinter
import threading
from tkinter import filedialog

empty_file = True
file_for_save_test_device_id = "test_device.txt"
app_versions_in_device = "app_versions_in_device.txt"

# функция записи в файл test_device.txt всех подключенных к adb устройств
def scan_devices_id_and_safe_to_file():
    # Выполняем команду в Adb devices и записываем в файл test_device.txt
    result = os.popen("adb devices").read().split('\n')
    with open(file_for_save_test_device_id, "w") as file:
        # выбираем только те данные в Adb в которых есть строки с device id
        for device in result[1:-2]:
            if device.strip():
                # записываем в файл только 
                file.write(device.split()[0] + "\n")

# функция для того что бы проверить есть ли файл apk_to_unitall.txt, что он не пустой и создаем его если его нет. 
# В файле всегда прописываются изначально ru.letu.preprod и ru.letu
def check_and_update_apk_file():
    try:
        # Открываем файл на чтение как переменную apk_file
        with open("apk_to_unitall.txt", "r") as apk_file:
            # Если при чтении видим что файл пустой то пишем в него ru.letu.preprod и ru.letu
            if apk_file.read().strip() == "":
                with open("apk_to_unitall.txt", "w") as new_apk_file:
                    new_apk_file.write("ru.letu.preprod\nru.letu")
    # Если файл не найден то создаем его и записываем в него ru.letu.preprod и ru.letu
    except FileNotFoundError:
        with open("apk_to_unitall.txt", "w") as new_apk_file:
            new_apk_file.write("ru.letu.preprod\nru.letu")

def get_app_versions(file_for_save_test_device_id, app_versions_in_device):
    # Открываем файл test_device.txt на чтение
    with open(file_for_save_test_device_id, "r") as file:
        # Записываем данные построчно в переменную devices
        devices = file.read().splitlines()
        
    # Открываем файл apk_to_unitall.txt на чтение
    with open("apk_to_unitall.txt", "r") as apk_file:
        app_names = apk_file.read().splitlines()
    
    # Открываем файл app_versions_in_device.txt для записи
    with open(app_versions_in_device, "w") as output:
        # для каждого device_id из списка devices
        for device_id in devices:
            # создаю пустой словарь
            output_data = {}

            for app_name_adb_list_test_letu in app_names:
                result = os.popen(f"adb -s {device_id} shell dumpsys package {app_name_adb_list_test_letu}").read()
                version_line = [line.strip() for line in result.split('\n') if 'versionName=' in line]
                if version_line:
                    version_name = version_line[0].split("=")[1]
                    output_data[app_name_adb_list_test_letu] = version_name
                else:
                    output_data[app_name_adb_list_test_letu] = "N/A"
            
            output.write(f"{device_id}\n")
            for app_name, version in output_data.items():
                output.write(f"{app_name} : {version}\n")

def uninstall_app_to_all_devices():
    with open('apk_to_unitall.txt', 'r') as file:
        for app_name_adb_list_test_letu in file:
            app_name_adb_list_test_letu = app_name_adb_list_test_letu.strip()
            with open(file_for_save_test_device_id, 'r') as device_file:
                for line in device_file:
                    dev_id = line.strip()
                    result = subprocess.run(['adb', '-s', dev_id, 'shell', 'pm', 'list', 'packages', '-3'], stdout=subprocess.PIPE)
                    output = result.stdout.decode('utf-8')
                    lines = output.splitlines()
                    for line in lines:
                        if app_name_adb_list_test_letu in line:
                            package_name = line.split(':')[-1].strip()
                            subprocess.run(['adb', '-s', dev_id, 'uninstall', package_name], stdout=subprocess.PIPE)

def install_apk_on_all_device():
    with open(file_for_save_test_device_id, "r") as file:
        devices = file.read().splitlines()
    with open("user_apk_file.txt", "r") as apk_file:
        apk_folder_path = apk_file.readline().strip()
    for device_id in devices:
        result = os.popen(f"adb -s {device_id} install {apk_folder_path}").read()

def unitall_and_install_apk_on_all_device_async():
    threading.Thread(target=scan_and_get_versions).start()
    threading.Thread(target=uninstall_app_to_all_devices).start()
    threading.Thread(target=install_apk_on_all_device).start()
   
def scan_and_get_versions():
    scan_devices_id_and_safe_to_file()
    get_app_versions(file_for_save_test_device_id, app_versions_in_device)
    read_file(file_for_save_test_device_id)

# Очень дорогая функция из-за нее тормозит прил app.after(1000, scan_devices_id_and_safe_to_file_cicle)
def scan_devices_id_and_safe_to_file_cicle():
    scan_devices_id_and_safe_to_file()
    get_app_versions(file_for_save_test_device_id, app_versions_in_device)
    read_file(file_for_save_test_device_id)
    app.after(2000, scan_devices_id_and_safe_to_file_cicle)

def read_file(filename):
    with open(filename, 'r') as file:
        text = file.read()
    return text

def open_apk_file():
    file_apk_path  = filedialog.askopenfilename()
    with open('user_apk_file.txt', 'w') as file:
        file.write(file_apk_path)

app = customtkinter.CTk()
textbox = customtkinter.CTkTextbox(app)
# Очень дорогая функция из-за нее тормозит прил app.after(1000, update_text_box)
def update_text_box():
    device_list = read_file(app_versions_in_device)
    textbox.configure(state="normal")  # Включаем редактирование для обновления содержимого
    textbox.delete("0.0", "end")
    textbox.insert("0.0", device_list)
    textbox.configure(state="disabled") 
    textbox.grid(row=0, column=1, padx=20, pady=20)
    app.after(2000, update_text_box)

app.title("APK Installer")
app.geometry("240x400")
app.resizable(False,False)

check_and_update_apk_file()
scan_devices_id_and_safe_to_file_cicle()
update_text_box()

button = customtkinter.CTkButton(app, text="Open APK", command=open_apk_file, hover_color="green")
button.grid(row=1, column=1, padx=20, pady=20)

button = customtkinter.CTkButton(app, text="Global Install", command=unitall_and_install_apk_on_all_device_async, hover_color="red")
button.grid(row=2, column=1, padx=20, pady=20)
#Тут адский костыль с тем что бы ADB не сдохла с количеством поданных на нее команд
button.configure(state="normal")
def disable_button():
    button.configure(state="disabled")
    app.after(20000, enable_button)
def enable_button():
    button.configure(state="normal")
def button_clicked():
    disable_button()
    unitall_and_install_apk_on_all_device_async()
button.configure(command=button_clicked)
app.mainloop()