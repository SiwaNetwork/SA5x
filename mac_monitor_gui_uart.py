#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MAC SA-53 GUI Monitor with Testing Functionality - UART Version
Графический интерфейс для мониторинга, настройки и тестирования параметров MAC SA-53
Модифицированная версия для работы с UART dev/ttyS6
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import threading
import time
import serial
import os
import sys
from datetime import datetime
import json
import csv
import subprocess
import math
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Константы
DEFAULT_UART_DEVICE = "/dev/ttyS6"
DEFAULT_BAUDRATE = 57600

# Команды MAC
MAC_COMMANDS_GET = [
    "DisciplineLocked",
    "DisciplineThresholdPps0", 
    "PpsInDetected",
    "LockProgress",
    "PpsSource",
    "LastCorrection",
    "DigitalTuning",
    "Phase",
    "Temperature",
    "serial",
    "Locked",
    "PhaseLimit",
    "EffectiveTuning",
]

MAC_COMMANDS_SET = [
    "PpsWidth", 
    "TauPps0", 
    "PpsSource", 
    "PpsOffset", 
    "Disciplining", 
    "DisciplineThresholdPps0", 
    "PhaseMetering", 
    "DigitalTuning", 
    "CableDelay", 
    "latch"
]

# Словари для преобразования русских названий в числа (для анализа данных)
RUSSIAN_DAYS = {
    "Пн": "Mon", "Вт": "Tue", "Ср": "Wed",
    "Чт": "Thu", "Пт": "Fri", "Сб": "Sat", "Вс": "Sun"
}
RUSSIAN_MONTHS = {
    "янв": "Jan", "фев": "Feb", "мар": "Mar", "апр": "Apr",
    "май": "May", "июн": "Jun", "июл": "Jul", "авг": "Aug",
    "сен": "Sep", "окт": "Oct", "ноя": "Nov", "дек": "Dec"
}

class HoldoverTestData:
    """Класс для хранения и анализа данных тестов holdover"""
    
    def __init__(self):
        self.data = []
        self.headers = ["Date", "Disciplining", "TauPps0", "DigitalTuning", 
                       "EffectiveTuning", "PPS In Detected", "Phase"]
    
    def add_record(self, disciplining, tau, digital_tuning, effective_tuning, 
                   pps_detected, phase):
        """Добавить запись данных"""
        record = {
            "Date": datetime.now().strftime("%a %d %b %Y %H:%M:%S GMT"),
            "Disciplining": disciplining,
            "TauPps0": tau,
            "DigitalTuning": digital_tuning,
            "EffectiveTuning": effective_tuning,
            "PPS In Detected": pps_detected,
            "Phase": phase
        }
        self.data.append(record)
    
    def save_to_csv(self, filename):
        """Сохранить данные в CSV файл"""
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.headers)
            writer.writeheader()
            writer.writerows(self.data)
    
    def load_from_csv(self, filename):
        """Загрузить данные из CSV файла"""
        self.data = []
        try:
            with open(filename, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    self.data.append(row)
            return True
        except Exception as e:
            print(f"Ошибка загрузки CSV: {e}")
            return False
    
    def parse_russian_date(self, date_string):
        """Функция для преобразования русской даты"""
        try:
            # Удаляем часовой пояс (например, " GMT")
            date_string = date_string.replace(" GMT", "")
            
            # Разбиваем строку на части
            parts = date_string.split()
            if len(parts) < 5:
                raise ValueError(f"Некорректная дата: {date_string}")
            
            # Заменяем русские названия дней недели и месяцев на английские
            day_of_week = RUSSIAN_DAYS.get(parts[0], parts[0])
            day = parts[1]
            month = RUSSIAN_MONTHS.get(parts[2], parts[2])
            year = parts[3]
            time = parts[4]
            
            # Формируем строку в английском формате
            english_date = f"{day_of_week} {day} {month} {year} {time}"
            
            # Преобразуем строку в объект datetime
            return datetime.strptime(english_date, "%a %d %b %Y %H:%M:%S")
        except Exception as e:
            print(f"Ошибка при парсинге даты '{date_string}': {e}")
            return None
    
    def analyze_changes(self):
        """Анализ изменений в данных"""
        if len(self.data) < 2:
            return []
        
        changes = []
        
        # Найти изменения в дисциплинировании и Tau
        for i in range(1, len(self.data)):
            prev_disc = self.data[i-1]["Disciplining"]
            curr_disc = self.data[i]["Disciplining"]
            prev_tau = self.data[i-1]["TauPps0"]
            curr_tau = self.data[i]["TauPps0"]
            
            if prev_disc != curr_disc or prev_tau != curr_tau:
                try:
                    curr_date = self.parse_russian_date(self.data[i]["Date"])
                    prev_date = self.parse_russian_date(self.data[i-1]["Date"])
                    
                    if curr_date and prev_date:
                        duration = (curr_date - prev_date).total_seconds()
                        
                        change_info = {
                            "index": i,
                            "date": self.data[i]["Date"],
                            "disciplining": curr_disc,
                            "tau": curr_tau,
                            "duration": duration,
                            "phase_start": self.data[i-1]["Phase"],
                            "phase_end": self.data[i]["Phase"]
                        }
                        changes.append(change_info)
                except Exception as e:
                    print(f"Ошибка анализа изменений: {e}")
                    continue
        
        return changes
    
    def generate_analysis_report(self):
        """Генерация отчета анализа данных"""
        changes = self.analyze_changes()
        report = []
        
        report.append("=== АНАЛИЗ ДАННЫХ ТЕСТИРОВАНИЯ ===\n")
        report.append(f"Общее количество записей: {len(self.data)}")
        report.append(f"Количество изменений состояния: {len(changes)}\n")
        
        for i, change in enumerate(changes):
            report.append(f"Изменение {i+1}:")
            report.append(f"  Время: {change['date']}")
            report.append(f"  Дисциплинирование: {change['disciplining']}")
            report.append(f"  Tau: {change['tau']}")
            report.append(f"  Длительность предыдущего состояния: {change['duration']:.0f} сек ({change['duration']/3600:.3f} ч)")
            report.append(f"  Фаза в начале: {change['phase_start']}")
            report.append(f"  Фаза в конце: {change['phase_end']}")
            
            # Анализ holdover периодов (когда дисциплинирование = 0)
            if change['disciplining'] == '0':
                try:
                    phase_start = float(change['phase_start'])
                    phase_end = float(change['phase_end'])
                    phase_drift = abs(phase_end - phase_start)
                    report.append(f"  Дрейф фазы за период holdover: {phase_drift:.0f} нс")
                    
                    if change['duration'] > 0:
                        drift_rate = phase_drift / (change['duration'] / 3600)  # нс/час
                        report.append(f"  Скорость дрейфа: {drift_rate:.2f} нс/час")
                except ValueError:
                    pass
            
            report.append("")
        
        return "\n".join(report)

class MACMonitorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("MAC SA-53 GUI Monitor - UART Version")
        self.root.geometry("1200x800")
        
        # Переменные состояния
        self.serial_connection = None
        self.monitoring_active = False
        self.monitoring_thread = None
        self.update_interval = tk.DoubleVar(value=1.0)
        self.save_to_eeprom = tk.BooleanVar(value=False)
        
        # UART настройки
        self.uart_device = tk.StringVar(value=DEFAULT_UART_DEVICE)
        self.uart_baudrate = tk.IntVar(value=DEFAULT_BAUDRATE)
        
        # Данные тестирования
        self.test_data = HoldoverTestData()
        self.test_active = False
        self.test_thread = None
        
        # Создание интерфейса
        self.create_menu()
        self.create_widgets()
        
        # Обработчик закрытия окна
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_menu(self):
        """Создание меню приложения"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Меню Файл
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Сохранить лог", command=self.save_log)
        file_menu.add_command(label="Очистить лог", command=self.clear_log)
        file_menu.add_separator()
        file_menu.add_command(label="Сохранить данные теста", command=self.save_test_data)
        file_menu.add_command(label="Загрузить данные теста", command=self.load_test_data)
        file_menu.add_command(label="Анализировать данные теста", command=self.analyze_test_data)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.on_closing)
        
        # Меню Тесты
        test_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Тесты", menu=test_menu)
        test_menu.add_command(label="Быстрый тест holdover", command=self.quick_holdover_test)
        test_menu.add_command(label="Тест деградации", command=self.degradation_test)
        test_menu.add_command(label="Полный тест конвергенции", command=self.full_convergence_test)
        test_menu.add_command(label="Остановить тест", command=self.stop_test)
        
        # Меню Справка
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Справка", menu=help_menu)
        help_menu.add_command(label="О программе", command=self.show_about)
    
    def create_widgets(self):
        """Создание виджетов интерфейса"""
        # Создание notebook для вкладок
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Вкладка мониторинга
        self.create_monitoring_tab()
        
        # Вкладка настроек
        self.create_settings_tab()
        
        # Вкладка тестирования
        self.create_testing_tab()
        
        # Вкладка логов
        self.create_logs_tab()
    
    def create_monitoring_tab(self):
        """Создание вкладки мониторинга"""
        monitoring_frame = ttk.Frame(self.notebook)
        self.notebook.add(monitoring_frame, text="Мониторинг")
        
        # Фрейм управления
        control_frame = ttk.LabelFrame(monitoring_frame, text="Управление мониторингом")
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Интервал обновления
        ttk.Label(control_frame, text="Интервал обновления (сек):").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        interval_spinbox = ttk.Spinbox(control_frame, from_=0.5, to=60.0, increment=0.5, 
                                      textvariable=self.update_interval, width=10)
        interval_spinbox.grid(row=0, column=1, padx=5, pady=5)
        
        # Кнопки управления
        self.start_monitoring_btn = ttk.Button(control_frame, text="Начать мониторинг", 
                                              command=self.start_monitoring)
        self.start_monitoring_btn.grid(row=0, column=2, padx=5, pady=5)
        
        self.stop_monitoring_btn = ttk.Button(control_frame, text="Остановить мониторинг", 
                                             command=self.stop_monitoring, state=tk.DISABLED)
        self.stop_monitoring_btn.grid(row=0, column=3, padx=5, pady=5)
        
        self.update_once_btn = ttk.Button(control_frame, text="Обновить", 
                                         command=self.update_parameters_once)
        self.update_once_btn.grid(row=0, column=4, padx=5, pady=5)
        
        # Таблица параметров
        params_frame = ttk.LabelFrame(monitoring_frame, text="Параметры устройства")
        params_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Создание Treeview для отображения параметров
        columns = ("Параметр", "Значение", "Единицы", "Время обновления")
        self.params_tree = ttk.Treeview(params_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.params_tree.heading(col, text=col)
            self.params_tree.column(col, width=150)
        
        # Скроллбар для таблицы
        params_scrollbar = ttk.Scrollbar(params_frame, orient=tk.VERTICAL, command=self.params_tree.yview)
        self.params_tree.configure(yscrollcommand=params_scrollbar.set)
        
        self.params_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        params_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Инициализация строк таблицы
        self.param_items = {}
        for param in MAC_COMMANDS_GET:
            item_id = self.params_tree.insert("", tk.END, values=(param, "—", "—", "—"))
            self.param_items[param] = item_id
    
    def create_settings_tab(self):
        """Создание вкладки настроек"""
        settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(settings_frame, text="Настройки")
        
        # Фрейм подключения UART
        connection_frame = ttk.LabelFrame(settings_frame, text="Подключение UART")
        connection_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # UART устройство
        ttk.Label(connection_frame, text="UART устройство:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        uart_entry = ttk.Entry(connection_frame, textvariable=self.uart_device, width=20)
        uart_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Скорость передачи
        ttk.Label(connection_frame, text="Скорость (baud):").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        baudrate_combo = ttk.Combobox(connection_frame, textvariable=self.uart_baudrate, 
                                     values=[9600, 19200, 38400, 57600, 115200], 
                                     state="readonly", width=10)
        baudrate_combo.grid(row=0, column=3, padx=5, pady=5)
        
        # Кнопки подключения
        self.connect_btn = ttk.Button(connection_frame, text="Подключиться", 
                                     command=self.connect_device)
        self.connect_btn.grid(row=0, column=4, padx=5, pady=5)
        
        self.disconnect_btn = ttk.Button(connection_frame, text="Отключиться", 
                                        command=self.disconnect_device, state=tk.DISABLED)
        self.disconnect_btn.grid(row=0, column=5, padx=5, pady=5)
        
        # Статус подключения
        self.connection_status = ttk.Label(connection_frame, text="Не подключено", 
                                          foreground="red")
        self.connection_status.grid(row=1, column=0, columnspan=6, padx=5, pady=5)
        
        # Фрейм настройки параметров
        param_settings_frame = ttk.LabelFrame(settings_frame, text="Настройка параметров")
        param_settings_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Выбор параметра
        ttk.Label(param_settings_frame, text="Параметр:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.param_var = tk.StringVar()
        self.param_combo = ttk.Combobox(param_settings_frame, textvariable=self.param_var, 
                                       values=MAC_COMMANDS_SET, state="readonly", width=20)
        self.param_combo.grid(row=0, column=1, padx=5, pady=5)
        
        # Значение параметра
        ttk.Label(param_settings_frame, text="Значение:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.param_value_var = tk.StringVar()
        self.param_value_entry = ttk.Entry(param_settings_frame, textvariable=self.param_value_var, width=15)
        self.param_value_entry.grid(row=0, column=3, padx=5, pady=5)
        
        # Сохранение в EEPROM
        self.eeprom_check = ttk.Checkbutton(param_settings_frame, text="Сохранить в EEPROM", 
                                           variable=self.save_to_eeprom)
        self.eeprom_check.grid(row=0, column=4, padx=5, pady=5)
        
        # Кнопка установки
        self.set_param_btn = ttk.Button(param_settings_frame, text="Установить", 
                                       command=self.set_parameter)
        self.set_param_btn.grid(row=0, column=5, padx=5, pady=5)
    
    def create_testing_tab(self):
        """Создание вкладки тестирования"""
        testing_frame = ttk.Frame(self.notebook)
        self.notebook.add(testing_frame, text="Тестирование")
        
        # Фрейм управления тестами
        test_control_frame = ttk.LabelFrame(testing_frame, text="Управление тестами")
        test_control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Кнопки тестов
        ttk.Button(test_control_frame, text="Быстрый тест holdover (5 мин)", 
                  command=self.quick_holdover_test).grid(row=0, column=0, padx=5, pady=5)
        
        ttk.Button(test_control_frame, text="Тест деградации", 
                  command=self.degradation_test).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Button(test_control_frame, text="Тест конвергенции", 
                  command=self.convergence_test).grid(row=0, column=2, padx=5, pady=5)
        
        self.stop_test_btn = ttk.Button(test_control_frame, text="Остановить тест", 
                                       command=self.stop_test, state=tk.DISABLED)
        self.stop_test_btn.grid(row=0, column=3, padx=5, pady=5)
        
        # Статус теста
        self.test_status = ttk.Label(test_control_frame, text="Тест не запущен", 
                                    foreground="blue")
        self.test_status.grid(row=1, column=0, columnspan=4, padx=5, pady=5)
        
        # Прогресс-бар
        self.test_progress = ttk.Progressbar(test_control_frame, mode='indeterminate')
        self.test_progress.grid(row=2, column=0, columnspan=4, padx=5, pady=5, sticky=tk.EW)
        
        # Фрейм параметров теста
        test_params_frame = ttk.LabelFrame(testing_frame, text="Параметры тестирования")
        test_params_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Длительность holdover теста
        ttk.Label(test_params_frame, text="Длительность holdover (сек):").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.holdover_duration = tk.IntVar(value=300)  # 5 минут по умолчанию
        ttk.Spinbox(test_params_frame, from_=60, to=86400, increment=60, 
                   textvariable=self.holdover_duration, width=10).grid(row=0, column=1, padx=5, pady=5)
        
        # Пороговое значение фазы для деградации
        ttk.Label(test_params_frame, text="Порог деградации фазы (нс):").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.degradation_threshold = tk.IntVar(value=120000)
        ttk.Spinbox(test_params_frame, from_=10000, to=1000000, increment=10000, 
                   textvariable=self.degradation_threshold, width=10).grid(row=0, column=3, padx=5, pady=5)
        
        # Фрейм результатов тестов
        test_results_frame = ttk.LabelFrame(testing_frame, text="Результаты тестирования")
        test_results_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Текстовое поле для результатов
        self.test_results_text = scrolledtext.ScrolledText(test_results_frame, height=15, 
                                                          wrap=tk.WORD, state=tk.DISABLED)
        self.test_results_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def create_logs_tab(self):
        """Создание вкладки логов"""
        logs_frame = ttk.Frame(self.notebook)
        self.notebook.add(logs_frame, text="Логи")
        
        # Текстовое поле для логов
        self.log_text = scrolledtext.ScrolledText(logs_frame, height=30, wrap=tk.WORD, state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def log_message(self, message):
        """Добавление сообщения в лог"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def connect_device(self):
        """Подключение к UART устройству"""
        try:
            device = self.uart_device.get()
            baudrate = self.uart_baudrate.get()
            
            self.serial_connection = serial.Serial(device, baudrate=baudrate, timeout=1)
            
            self.connection_status.config(text=f"Подключено к {device} ({baudrate} baud)", 
                                        foreground="green")
            self.connect_btn.config(state=tk.DISABLED)
            self.disconnect_btn.config(state=tk.NORMAL)
            
            self.log_message(f"Успешное подключение к {device} на скорости {baudrate} baud")
            
        except Exception as e:
            messagebox.showerror("Ошибка подключения", f"Не удалось подключиться к устройству:\n{str(e)}")
            self.log_message(f"Ошибка подключения: {str(e)}")
    
    def disconnect_device(self):
        """Отключение от устройства"""
        if self.serial_connection:
            self.serial_connection.close()
            self.serial_connection = None
        
        self.connection_status.config(text="Не подключено", foreground="red")
        self.connect_btn.config(state=tk.NORMAL)
        self.disconnect_btn.config(state=tk.DISABLED)
        
        # Остановить мониторинг если активен
        if self.monitoring_active:
            self.stop_monitoring()
        
        self.log_message("Отключение от устройства")
    
    def send_mac_command(self, command):
        """Отправка команды MAC устройству"""
        if not self.serial_connection:
            raise Exception("Нет подключения к устройству")
        
        cmd_str = f"\\{{{command}}}"
        self.serial_connection.write(cmd_str.encode())
        response = self.serial_connection.readline().decode().strip()
        return response
    
    def get_parameter(self, param):
        """Получение значения параметра"""
        try:
            command = f"get,{param}"
            response = self.send_mac_command(command)
            return response
        except Exception as e:
            self.log_message(f"Ошибка получения параметра {param}: {str(e)}")
            return "Ошибка"
    
    def set_parameter(self):
        """Установка значения параметра"""
        if not self.serial_connection:
            messagebox.showerror("Ошибка", "Нет подключения к устройству")
            return
        
        param = self.param_var.get()
        value = self.param_value_var.get()
        
        if not param or not value:
            messagebox.showerror("Ошибка", "Выберите параметр и введите значение")
            return
        
        try:
            if param == "latch":
                command = "latch"
            else:
                command = f"set,{param},{value}"
            
            response = self.send_mac_command(command)
            
            if self.save_to_eeprom.get():
                store_response = self.send_mac_command("store")
                self.log_message(f"Параметр {param} установлен в {value}, сохранен в EEPROM. Ответ: {response}, {store_response}")
            else:
                self.log_message(f"Параметр {param} установлен в {value}. Ответ: {response}")
            
            messagebox.showinfo("Успех", f"Параметр {param} успешно установлен")
            
        except Exception as e:
            error_msg = f"Ошибка установки параметра: {str(e)}"
            messagebox.showerror("Ошибка", error_msg)
            self.log_message(error_msg)
    
    def update_parameters_once(self):
        """Однократное обновление параметров"""
        if not self.serial_connection:
            messagebox.showerror("Ошибка", "Нет подключения к устройству")
            return
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        for param in MAC_COMMANDS_GET:
            try:
                value = self.get_parameter(param)
                
                # Определение единиц измерения
                units = ""
                if param == "Phase":
                    units = "нс"
                elif param == "Temperature":
                    units = "°C"
                elif param in ["TauPps0", "PpsWidth", "PpsOffset"]:
                    units = "мкс" if param == "PpsWidth" else ""
                
                # Обновление таблицы
                item_id = self.param_items[param]
                self.params_tree.item(item_id, values=(param, value, units, timestamp))
                
            except Exception as e:
                self.log_message(f"Ошибка обновления {param}: {str(e)}")
    
    def start_monitoring(self):
        """Запуск мониторинга"""
        if not self.serial_connection:
            messagebox.showerror("Ошибка", "Нет подключения к устройству")
            return
        
        self.monitoring_active = True
        self.start_monitoring_btn.config(state=tk.DISABLED)
        self.stop_monitoring_btn.config(state=tk.NORMAL)
        
        self.monitoring_thread = threading.Thread(target=self.monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        self.log_message("Мониторинг запущен")
    
    def stop_monitoring(self):
        """Остановка мониторинга"""
        self.monitoring_active = False
        self.start_monitoring_btn.config(state=tk.NORMAL)
        self.stop_monitoring_btn.config(state=tk.DISABLED)
        
        self.log_message("Мониторинг остановлен")
    
    def monitoring_loop(self):
        """Цикл мониторинга"""
        while self.monitoring_active:
            try:
                self.update_parameters_once()
                time.sleep(self.update_interval.get())
            except Exception as e:
                self.log_message(f"Ошибка в цикле мониторинга: {str(e)}")
                break
    
    def quick_holdover_test(self):
        """Быстрый тест holdover"""
        if self.test_active:
            messagebox.showwarning("Предупреждение", "Тест уже выполняется")
            return
        
        if not self.serial_connection:
            messagebox.showerror("Ошибка", "Нет подключения к устройству")
            return
        
        duration = self.holdover_duration.get()
        
        self.test_active = True
        self.stop_test_btn.config(state=tk.NORMAL)
        self.test_progress.start()
        
        self.test_thread = threading.Thread(target=self._run_holdover_test, args=(duration,), daemon=True)
        self.test_thread.start()
    
    def _run_holdover_test(self, duration):
        """Выполнение теста holdover"""
        try:
            self.test_status.config(text=f"Выполняется тест holdover ({duration} сек)")
            self.log_test_message("=== НАЧАЛО ТЕСТА HOLDOVER ===")
            self.log_test_message(f"Длительность: {duration} секунд")
            
            # Остановка дисциплинирования
            self.send_mac_command("set,Disciplining,0")
            self.log_test_message("Дисциплинирование остановлено")
            
            # Очистка данных теста
            self.test_data.data = []
            
            start_time = time.time()
            
            while self.test_active and (time.time() - start_time) < duration:
                try:
                    # Получение параметров
                    disciplining = self.get_parameter("Disciplining")
                    tau = self.get_parameter("TauPps0")
                    digital_tuning = self.get_parameter("DigitalTuning")
                    effective_tuning = self.get_parameter("EffectiveTuning")
                    pps_detected = self.get_parameter("PpsInDetected")
                    phase = self.get_parameter("Phase")
                    
                    # Добавление записи
                    self.test_data.add_record(disciplining, tau, digital_tuning, 
                                            effective_tuning, pps_detected, phase)
                    
                    elapsed = time.time() - start_time
                    remaining = duration - elapsed
                    self.test_status.config(text=f"Holdover тест: {remaining:.0f} сек осталось")
                    
                    time.sleep(5)  # Интервал записи данных
                    
                except Exception as e:
                    self.log_test_message(f"Ошибка в тесте: {str(e)}")
                    break
            
            if self.test_active:
                # Получение финального значения фазы
                final_phase = self.get_parameter("Phase")
                self.log_test_message(f"Финальное значение фазы: {final_phase} нс")
                self.log_test_message("=== ТЕСТ HOLDOVER ЗАВЕРШЕН ===")
                
                # Возобновление дисциплинирования
                self.send_mac_command("set,Disciplining,1")
                self.log_test_message("Дисциплинирование возобновлено")
                
                self.test_status.config(text="Тест holdover завершен успешно")
            else:
                self.log_test_message("=== ТЕСТ HOLDOVER ПРЕРВАН ===")
                self.test_status.config(text="Тест holdover прерван")
            
        except Exception as e:
            self.log_test_message(f"Критическая ошибка теста: {str(e)}")
            self.test_status.config(text="Ошибка выполнения теста")
        finally:
            self.test_active = False
            self.stop_test_btn.config(state=tk.DISABLED)
            self.test_progress.stop()
    
    def degradation_test(self):
        """Тест деградации"""
        if self.test_active:
            messagebox.showwarning("Предупреждение", "Тест уже выполняется")
            return
        
        if not self.serial_connection:
            messagebox.showerror("Ошибка", "Нет подключения к устройству")
            return
        
        threshold = self.degradation_threshold.get()
        
        self.test_active = True
        self.stop_test_btn.config(state=tk.NORMAL)
        self.test_progress.start()
        
        self.test_thread = threading.Thread(target=self._run_degradation_test, args=(threshold,), daemon=True)
        self.test_thread.start()
    
    def _run_degradation_test(self, threshold):
        """Выполнение теста деградации"""
        try:
            self.test_status.config(text="Выполняется тест деградации")
            self.log_test_message("=== НАЧАЛО ТЕСТА ДЕГРАДАЦИИ ===")
            self.log_test_message(f"Пороговое значение фазы: {threshold} нс")
            
            # Остановка дисциплинирования
            self.send_mac_command("set,Disciplining,0")
            self.log_test_message("Дисциплинирование остановлено")
            
            # Намеренная деградация
            self.log_test_message("Начало намеренной деградации")
            for i in range(31):  # Как в оригинальном скрипте
                if not self.test_active:
                    break
                self.send_mac_command(f"set,DigitalTuning,{i}")
                self.log_test_message(f"Деградация цифровой настройки {i}")
                time.sleep(1)
            
            # Ожидание достижения порогового значения
            start_time = time.time()
            while self.test_active:
                phase = self.get_parameter("Phase")
                try:
                    phase_value = float(phase)
                    elapsed = time.time() - start_time
                    
                    if abs(phase_value) >= threshold:
                        self.log_test_message(f"Достигнуто пороговое значение фазы: {phase} нс")
                        self.log_test_message(f"Время деградации: {elapsed:.0f} секунд")
                        break
                    else:
                        self.log_test_message(f"Фаза = {phase}, деградация недостаточна, порог {threshold}")
                        self.log_test_message(f"{elapsed:.0f} секунд прошло при ожидании деградации")
                    
                    time.sleep(5)
                    
                except ValueError:
                    self.log_test_message(f"Некорректное значение фазы: {phase}")
                    time.sleep(5)
            
            if self.test_active:
                self.log_test_message("=== ТЕСТ ДЕГРАДАЦИИ ЗАВЕРШЕН ===")
                self.test_status.config(text="Тест деградации завершен успешно")
            else:
                self.log_test_message("=== ТЕСТ ДЕГРАДАЦИИ ПРЕРВАН ===")
                self.test_status.config(text="Тест деградации прерван")
            
        except Exception as e:
            self.log_test_message(f"Критическая ошибка теста: {str(e)}")
            self.test_status.config(text="Ошибка выполнения теста")
        finally:
            self.test_active = False
            self.stop_test_btn.config(state=tk.DISABLED)
            self.test_progress.stop()
    
    def convergence_test(self):
        """Тест конвергенции"""
        if self.test_active:
            messagebox.showwarning("Предупреждение", "Тест уже выполняется")
            return
        
        if not self.serial_connection:
            messagebox.showerror("Ошибка", "Нет подключения к устройству")
            return
        
        # Подтверждение длительного теста
        result = messagebox.askyesno("Подтверждение", 
                                   "Тест конвергенции может занять более 24 часов.\n"
                                   "Продолжить?")
        if not result:
            return
        
        self.test_active = True
        self.stop_test_btn.config(state=tk.NORMAL)
        self.test_progress.start()
        
        self.test_thread = threading.Thread(target=self._run_convergence_test, daemon=True)
        self.test_thread.start()
    
    def _run_convergence_test(self):
        """Выполнение полного теста конвергенции"""
        try:
            self.test_status.config(text="Выполняется полный тест конвергенции")
            self.log_test_message("=== НАЧАЛО ПОЛНОГО ТЕСТА КОНВЕРГЕНЦИИ ===")
            
            # Этап 1: Деградация
            self.log_test_message("ЭТАП 1: Деградация")
            self._run_degradation_test(self.degradation_threshold.get())
            
            if not self.test_active:
                return
            
            # Этап 2: Восстановление с Tau=50 (10 минут)
            self.log_test_message("ЭТАП 2: Восстановление с Tau=50")
            self.send_mac_command("set,TauPps0,50")
            self.send_mac_command("set,Disciplining,1")
            self._wait_and_log(600, "Восстановление Tau=50")  # 10 минут
            
            if not self.test_active:
                return
            
            # Этап 3: Восстановление с Tau=500 (2 часа)
            self.log_test_message("ЭТАП 3: Восстановление с Tau=500")
            self.send_mac_command("set,TauPps0,500")
            self._wait_and_log(7200, "Восстановление Tau=500")  # 2 часа
            
            if not self.test_active:
                return
            
            # Этап 4: Восстановление с Tau=10000 (13.9 часа)
            self.log_test_message("ЭТАП 4: Восстановление с Tau=10000")
            self.send_mac_command("set,TauPps0,10000")
            self._wait_and_log(50000, "Восстановление Tau=10000")  # 13.9 часа
            
            if not self.test_active:
                return
            
            # Этап 5: Holdover тест (24 часа)
            self.log_test_message("ЭТАП 5: Holdover тест (24 часа)")
            self._run_holdover_test(86400)  # 24 часа
            
            if self.test_active:
                self.log_test_message("=== ПОЛНЫЙ ТЕСТ КОНВЕРГЕНЦИИ ЗАВЕРШЕН ===")
                self.test_status.config(text="Полный тест конвергенции завершен успешно")
            else:
                self.log_test_message("=== ПОЛНЫЙ ТЕСТ КОНВЕРГЕНЦИИ ПРЕРВАН ===")
                self.test_status.config(text="Полный тест конвергенции прерван")
            
        except Exception as e:
            self.log_test_message(f"Критическая ошибка теста: {str(e)}")
            self.test_status.config(text="Ошибка выполнения теста")
        finally:
            self.test_active = False
            self.stop_test_btn.config(state=tk.DISABLED)
            self.test_progress.stop()
    
    def _wait_and_log(self, duration, stage_name):
        """Ожидание с логированием прогресса"""
        start_time = time.time()
        while self.test_active and (time.time() - start_time) < duration:
            elapsed = time.time() - start_time
            remaining = duration - elapsed
            
            # Логирование каждые 5 минут
            if int(elapsed) % 300 == 0:
                phase = self.get_parameter("Phase")
                self.log_test_message(f"{stage_name}: {elapsed/3600:.1f}ч прошло, фаза = {phase} нс")
            
            self.test_status.config(text=f"{stage_name}: {remaining/3600:.1f}ч осталось")
            time.sleep(60)  # Проверка каждую минуту
    
    def stop_test(self):
        """Остановка активного теста"""
        self.test_active = False
        self.stop_test_btn.config(state=tk.DISABLED)
        self.test_progress.stop()
        self.test_status.config(text="Тест остановлен пользователем")
        self.log_test_message("Тест остановлен пользователем")
    
    def full_convergence_test(self):
        """Полный тест конвергенции (алиас для совместимости с меню)"""
        self.convergence_test()
    
    def log_test_message(self, message):
        """Добавление сообщения в лог тестирования"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        # Добавление в общий лог
        self.log_message(f"ТЕСТ: {message}")
        
        # Добавление в лог тестирования
        self.test_results_text.config(state=tk.NORMAL)
        self.test_results_text.insert(tk.END, log_entry)
        self.test_results_text.see(tk.END)
        self.test_results_text.config(state=tk.DISABLED)
    
    def save_log(self):
        """Сохранение лога в файл"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.log_text.get(1.0, tk.END))
                messagebox.showinfo("Успех", f"Лог сохранен в {filename}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить лог:\n{str(e)}")
    
    def clear_log(self):
        """Очистка лога"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def save_test_data(self):
        """Сохранение данных теста"""
        if not self.test_data.data:
            messagebox.showwarning("Предупреждение", "Нет данных для сохранения")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            try:
                self.test_data.save_to_csv(filename)
                messagebox.showinfo("Успех", f"Данные сохранены в {filename}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить данные:\n{str(e)}")
    
    def load_test_data(self):
        """Загрузка данных теста"""
        filename = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            if self.test_data.load_from_csv(filename):
                messagebox.showinfo("Успех", f"Данные загружены из {filename}")
                self.log_message(f"Загружено {len(self.test_data.data)} записей из {filename}")
            else:
                messagebox.showerror("Ошибка", "Не удалось загрузить данные")
    
    def analyze_test_data(self):
        """Анализ данных теста"""
        if not self.test_data.data:
            messagebox.showwarning("Предупреждение", "Нет данных для анализа")
            return
        
        try:
            report = self.test_data.generate_analysis_report()
            
            # Создание окна с результатами анализа
            analysis_window = tk.Toplevel(self.root)
            analysis_window.title("Анализ данных тестирования")
            analysis_window.geometry("800x600")
            
            text_widget = scrolledtext.ScrolledText(analysis_window, wrap=tk.WORD)
            text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            text_widget.insert(tk.END, report)
            text_widget.config(state=tk.DISABLED)
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка анализа данных:\n{str(e)}")
    
    def show_about(self):
        """Показать информацию о программе"""
        about_text = """MAC SA-53 GUI Monitor - UART Version

Версия: 3.0
Дата: 2025

Программа для мониторинга, настройки и тестирования 
параметров атомных часов MAC SA-53 через UART.

Особенности версии 3.0:
• Прямое подключение через UART (/dev/ttyS6)
• Автоматизированное тестирование holdover
• Тесты деградации и конвергенции
• Анализ данных тестирования
• Экспорт/импорт данных в CSV
• Расширенное логирование

Разработано на основе timetickler.py и скриптов 
анализа данных holdover."""
        
        messagebox.showinfo("О программе", about_text)
    
    def on_closing(self):
        """Обработчик закрытия окна"""
        if self.monitoring_active:
            self.stop_monitoring()
        
        if self.test_active:
            self.stop_test()
        
        if self.serial_connection:
            self.disconnect_device()
        
        self.root.destroy()

def main():
    root = tk.Tk()
    app = MACMonitorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()

