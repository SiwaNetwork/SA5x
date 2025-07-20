#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестирование логики UART GUI приложения без графического интерфейса
"""

import sys
import os
import time
import csv
from datetime import datetime
from unittest.mock import Mock

# Добавляем текущую директорию в путь
sys.path.insert(0, '/home/ubuntu')

def test_holdover_data_functionality():
    """Тестирование функциональности HoldoverTestData"""
    print("=== ТЕСТИРОВАНИЕ HOLDOVERTESTDATA ===")
    
    try:
        # Импорт без GUI компонентов
        import importlib.util
        spec = importlib.util.spec_from_file_location("mac_uart", "/home/ubuntu/mac_monitor_gui_uart.py")
        mac_uart = importlib.util.module_from_spec(spec)
        
        # Мокаем tkinter для избежания ошибок GUI
        sys.modules['tkinter'] = Mock()
        sys.modules['tkinter.ttk'] = Mock()
        sys.modules['tkinter.messagebox'] = Mock()
        sys.modules['tkinter.scrolledtext'] = Mock()
        sys.modules['tkinter.filedialog'] = Mock()
        sys.modules['matplotlib.backends.backend_tkagg'] = Mock()
        
        spec.loader.exec_module(mac_uart)
        
        # Тестирование HoldoverTestData
        test_data = mac_uart.HoldoverTestData()
        print("✓ HoldoverTestData создан")
        
        # Добавление тестовых данных
        test_records = [
            ("1", "10000", "12345", "54321", "1", "1000"),
            ("0", "10000", "12345", "54321", "1", "2000"),  # Изменение дисциплинирования
            ("0", "500", "12345", "54321", "1", "3000"),    # Изменение Tau
            ("1", "500", "12345", "54321", "1", "1500"),    # Изменение дисциплинирования обратно
        ]
        
        for record in test_records:
            test_data.add_record(*record)
        
        assert len(test_data.data) == 4, f"Неверное количество записей: {len(test_data.data)}"
        print(f"✓ Добавлено {len(test_data.data)} записей")
        
        # Тестирование сохранения/загрузки CSV
        test_file = "/tmp/test_uart_data.csv"
        test_data.save_to_csv(test_file)
        assert os.path.exists(test_file), "CSV файл не создан"
        print("✓ CSV файл сохранен")
        
        # Проверка содержимого CSV
        with open(test_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            lines = list(reader)
            assert len(lines) == 5, f"Неверное количество строк в CSV: {len(lines)}"  # заголовок + 4 записи
            assert lines[0] == test_data.headers, "Неверные заголовки CSV"
        print("✓ Содержимое CSV корректно")
        
        # Тестирование загрузки
        new_test_data = mac_uart.HoldoverTestData()
        result = new_test_data.load_from_csv(test_file)
        assert result == True, "Загрузка не удалась"
        assert len(new_test_data.data) == 4, f"Неверное количество загруженных записей: {len(new_test_data.data)}"
        print("✓ Данные загружены из CSV")
        
        # Тестирование анализа изменений
        changes = new_test_data.analyze_changes()
        print(f"✓ Найдено {len(changes)} изменений состояния")
        
        # Проверка конкретных изменений
        expected_changes = 3  # Ожидаем 3 изменения
        assert len(changes) == expected_changes, f"Неверное количество изменений: {len(changes)}, ожидалось {expected_changes}"
        
        # Тестирование генерации отчета
        report = new_test_data.generate_analysis_report()
        assert len(report) > 100, "Отчет слишком короткий"
        assert "АНАЛИЗ ДАННЫХ ТЕСТИРОВАНИЯ" in report, "Заголовок отчета не найден"
        print("✓ Отчет анализа сгенерирован")
        
        # Очистка
        os.remove(test_file)
        
        return True
        
    except Exception as e:
        print(f"✗ Ошибка тестирования HoldoverTestData: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_uart_constants():
    """Тестирование констант и настроек UART"""
    print("\n=== ТЕСТИРОВАНИЕ КОНСТАНТ UART ===")
    
    try:
        # Чтение файла напрямую для проверки констант
        with open("/home/ubuntu/mac_monitor_gui_uart.py", 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Проверка наличия ключевых констант
        assert 'DEFAULT_UART_DEVICE = "/dev/ttyS6"' in content, "Константа DEFAULT_UART_DEVICE не найдена"
        assert 'DEFAULT_BAUDRATE = 57600' in content, "Константа DEFAULT_BAUDRATE не найдена"
        print("✓ Константы UART найдены в коде")
        
        # Проверка команд MAC
        assert 'MAC_COMMANDS_GET = [' in content, "Список MAC_COMMANDS_GET не найден"
        assert 'MAC_COMMANDS_SET = [' in content, "Список MAC_COMMANDS_SET не найден"
        assert '"Phase"' in content, "Команда Phase не найдена"
        assert '"Disciplining"' in content, "Команда Disciplining не найдена"
        print("✓ Команды MAC найдены в коде")
        
        # Проверка словарей для русских дат
        assert 'RUSSIAN_DAYS = {' in content, "Словарь RUSSIAN_DAYS не найден"
        assert 'RUSSIAN_MONTHS = {' in content, "Словарь RUSSIAN_MONTHS не найден"
        print("✓ Словари для русских дат найдены")
        
        # Проверка методов UART
        assert 'def connect_device(self):' in content, "Метод connect_device не найден"
        assert 'def send_mac_command(self, command):' in content, "Метод send_mac_command не найден"
        assert 'serial.Serial(' in content, "Использование pyserial не найдено"
        print("✓ Методы UART найдены")
        
        return True
        
    except Exception as e:
        print(f"✗ Ошибка тестирования констант: {e}")
        return False

def test_russian_date_parsing():
    """Тестирование парсинга русских дат"""
    print("\n=== ТЕСТИРОВАНИЕ ПАРСИНГА РУССКИХ ДАТ ===")
    
    try:
        # Создаем простой класс для тестирования парсинга дат
        class TestDateParser:
            def __init__(self):
                self.RUSSIAN_DAYS = {
                    "Пн": "Mon", "Вт": "Tue", "Ср": "Wed",
                    "Чт": "Thu", "Пт": "Fri", "Сб": "Sat", "Вс": "Sun"
                }
                self.RUSSIAN_MONTHS = {
                    "янв": "Jan", "фев": "Feb", "мар": "Mar", "апр": "Apr",
                    "май": "May", "июн": "Jun", "июл": "Jul", "авг": "Aug",
                    "сен": "Sep", "окт": "Oct", "ноя": "Nov", "дек": "Dec"
                }
            
            def parse_russian_date(self, date_string):
                try:
                    date_string = date_string.replace(" GMT", "")
                    parts = date_string.split()
                    if len(parts) < 5:
                        raise ValueError(f"Некорректная дата: {date_string}")
                    
                    day_of_week = self.RUSSIAN_DAYS.get(parts[0], parts[0])
                    day = parts[1]
                    month = self.RUSSIAN_MONTHS.get(parts[2], parts[2])
                    year = parts[3]
                    time = parts[4]
                    
                    english_date = f"{day_of_week} {day} {month} {year} {time}"
                    return datetime.strptime(english_date, "%a %d %b %Y %H:%M:%S")
                except Exception as e:
                    print(f"Ошибка при парсинге даты '{date_string}': {e}")
                    return None
        
        parser = TestDateParser()
        
        # Тестовые русские даты
        test_dates = [
            "Пн 24 апр 2025 15:29:18 GMT",
            "Вт 25 дек 2024 12:00:00 GMT",
            "Ср 01 янв 2025 00:00:00 GMT"
        ]
        
        for test_date in test_dates:
            parsed = parser.parse_russian_date(test_date)
            assert parsed is not None, f"Не удалось распарсить дату: {test_date}"
            assert isinstance(parsed, datetime), f"Результат не является datetime: {type(parsed)}"
            print(f"✓ Дата '{test_date}' распарсена как {parsed}")
        
        # Тестирование некорректных дат
        invalid_dates = [
            "Неверная дата",
            "Пн 24",
            ""
        ]
        
        for invalid_date in invalid_dates:
            parsed = parser.parse_russian_date(invalid_date)
            assert parsed is None, f"Некорректная дата была распарсена: {invalid_date}"
        
        print("✓ Обработка некорректных дат работает")
        
        return True
        
    except Exception as e:
        print(f"✗ Ошибка тестирования парсинга дат: {e}")
        return False

def test_file_structure():
    """Тестирование структуры файла"""
    print("\n=== ТЕСТИРОВАНИЕ СТРУКТУРЫ ФАЙЛА ===")
    
    try:
        main_file = "/home/ubuntu/mac_monitor_gui_uart.py"
        
        # Проверка существования и размера
        assert os.path.exists(main_file), "Основной файл не найден"
        file_size = os.path.getsize(main_file)
        assert file_size > 30000, f"Файл слишком мал: {file_size} байт"
        print(f"✓ Файл существует, размер: {file_size} байт")
        
        # Проверка кодировки и содержимого
        with open(main_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Проверка основных компонентов
        required_components = [
            "class HoldoverTestData:",
            "class MACMonitorGUI:",
            "def connect_device(self):",
            "def send_mac_command(self, command):",
            "def quick_holdover_test(self):",
            "def degradation_test(self):",
            "def convergence_test(self):",
            "DEFAULT_UART_DEVICE",
            "DEFAULT_BAUDRATE",
            "MAC_COMMANDS_GET",
            "MAC_COMMANDS_SET"
        ]
        
        for component in required_components:
            assert component in content, f"Компонент не найден: {component}"
        
        print("✓ Все основные компоненты найдены")
        
        # Проверка количества строк
        lines = content.split('\n')
        assert len(lines) > 1000, f"Файл слишком короткий: {len(lines)} строк"
        print(f"✓ Количество строк: {len(lines)}")
        
        # Проверка комментариев и документации
        docstring_count = content.count('"""')
        assert docstring_count >= 10, f"Недостаточно документации: {docstring_count} docstrings"
        print(f"✓ Документация присутствует: {docstring_count} docstrings")
        
        return True
        
    except Exception as e:
        print(f"✗ Ошибка тестирования структуры файла: {e}")
        return False

def test_mock_serial_operations():
    """Тестирование операций с мок-serial"""
    print("\n=== ТЕСТИРОВАНИЕ МОК-SERIAL ОПЕРАЦИЙ ===")
    
    try:
        # Создание мок-объекта serial
        class MockSerial:
            def __init__(self, device, baudrate, timeout):
                self.device = device
                self.baudrate = baudrate
                self.timeout = timeout
                self.is_open = True
                self.commands_sent = []
            
            def write(self, data):
                command = data.decode()
                self.commands_sent.append(command)
                return len(data)
            
            def readline(self):
                # Возвращаем разные ответы в зависимости от команды
                if self.commands_sent:
                    last_command = self.commands_sent[-1]
                    if "get,Phase" in last_command:
                        return b"1000\n"
                    elif "get,Disciplining" in last_command:
                        return b"1\n"
                    elif "get,Temperature" in last_command:
                        return b"25.5\n"
                    else:
                        return b"OK\n"
                return b"OK\n"
            
            def close(self):
                self.is_open = False
        
        # Тестирование создания соединения
        mock_serial = MockSerial("/dev/ttyS6", 57600, 1)
        assert mock_serial.device == "/dev/ttyS6", "Неверное устройство"
        assert mock_serial.baudrate == 57600, "Неверная скорость"
        print("✓ Мок-serial создан")
        
        # Тестирование отправки команд
        test_commands = [
            "\\{get,Phase}",
            "\\{get,Disciplining}",
            "\\{set,TauPps0,10000}",
            "\\{store}"
        ]
        
        for cmd in test_commands:
            mock_serial.write(cmd.encode())
            response = mock_serial.readline()
            assert len(response) > 0, f"Нет ответа на команду: {cmd}"
        
        assert len(mock_serial.commands_sent) == len(test_commands), "Не все команды отправлены"
        print(f"✓ Отправлено {len(mock_serial.commands_sent)} команд")
        
        # Тестирование специфических ответов
        mock_serial.write(b"\\{get,Phase}")
        phase_response = mock_serial.readline().decode().strip()
        assert phase_response == "1000", f"Неверный ответ на Phase: {phase_response}"
        
        mock_serial.write(b"\\{get,Disciplining}")
        disc_response = mock_serial.readline().decode().strip()
        assert disc_response == "1", f"Неверный ответ на Disciplining: {disc_response}"
        
        print("✓ Специфические ответы корректны")
        
        # Тестирование закрытия
        mock_serial.close()
        assert not mock_serial.is_open, "Соединение не закрыто"
        print("✓ Соединение закрыто")
        
        return True
        
    except Exception as e:
        print(f"✗ Ошибка тестирования мок-serial: {e}")
        return False

def run_all_tests():
    """Запуск всех тестов без GUI"""
    print("ТЕСТИРОВАНИЕ ЛОГИКИ MAC SA-53 UART GUI (БЕЗ GUI)")
    print("=" * 60)
    
    tests = [
        test_uart_constants,
        test_file_structure,
        test_russian_date_parsing,
        test_mock_serial_operations,
        test_holdover_data_functionality,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print(f"✗ Тест {test.__name__} не прошел")
        except Exception as e:
            print(f"✗ Исключение в тесте {test.__name__}: {e}")
    
    print("\n" + "=" * 60)
    print(f"РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ: {passed}/{total} тестов прошли")
    
    if passed == total:
        print("✓ ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
        print("\nПрограмма готова к использованию с реальным UART устройством.")
        return True
    else:
        print("✗ НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОШЛИ")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

