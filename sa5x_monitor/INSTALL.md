# Установка и запуск SA5X Monitor

## Быстрый старт

### 1. Установка зависимостей

```bash
# Установка Python зависимостей
pip install -r requirements.txt
```

### 2. Проверка установки

```bash
# Запуск тестов
python -m pytest tests/test_basic.py -v
```

### 3. Запуск CLI версии

```bash
# Показать справку
python run_cli.py --help

# Показать текущий статус SA5X
python run_cli.py --port /dev/ttyUSB0

# Запустить мониторинг
python run_cli.py --port /dev/ttyUSB0 --monitor --interval 10

# Запустить тест holdover
python run_cli.py --port /dev/ttyUSB0 --holdover-test --duration 3600 --interval 10

# Анализ существующего лога
python run_cli.py --parse-log examples/sample_holdover_log.txt
```

### 4. Запуск Web версии

```bash
# Запуск веб-сервера
python run_web.py

# Запуск с кастомными параметрами
python run_web.py --host 0.0.0.0 --port 8080 --debug
```

Веб-интерфейс будет доступен по адресу: http://localhost:8080

## Подробная установка

### Требования системы

- Python 3.8 или выше
- Доступ к последовательному порту (для подключения к SA5X)
- Минимум 100MB свободного места на диске

### Установка на Linux

```bash
# Обновление пакетов
sudo apt update

# Установка Python и pip
sudo apt install python3 python3-pip python3-venv

# Создание виртуального окружения
python3 -m venv sa5x_env
source sa5x_env/bin/activate

# Установка зависимостей
pip install -r requirements.txt
```

### Установка на Windows

```bash
# Создание виртуального окружения
python -m venv sa5x_env
sa5x_env\Scripts\activate

# Установка зависимостей
pip install -r requirements.txt
```

### Установка на macOS

```bash
# Установка через Homebrew (если не установлен)
brew install python3

# Создание виртуального окружения
python3 -m venv sa5x_env
source sa5x_env/bin/activate

# Установка зависимостей
pip install -r requirements.txt
```

## Настройка

### 1. Конфигурационный файл

По умолчанию используется `config/sa5x_config.json`. Вы можете изменить настройки:

```json
{
  "serial": {
    "default_port": "/dev/ttyUSB0",
    "default_baudrate": 115200
  },
  "web_interface": {
    "host": "localhost",
    "port": 8080
  }
}
```

### 2. Права доступа к последовательному порту (Linux)

```bash
# Добавление пользователя в группу dialout
sudo usermod -a -G dialout $USER

# Перезагрузка или перелогин
sudo reboot
```

### 3. Проверка доступных портов

```bash
# Linux/macOS
ls /dev/tty*

# Windows
# Проверьте в Диспетчере устройств -> Порты (COM и LPT)
```

## Использование

### CLI Версия

#### Базовые команды

```bash
# Показать справку
python run_cli.py --help

# Показать статус SA5X
python run_cli.py --port /dev/ttyUSB0

# Запустить мониторинг на 1 минуту
python run_cli.py --port /dev/ttyUSB0 --monitor --interval 5
```

#### Тестирование holdover

```bash
# Короткий тест (5 минут)
python run_cli.py --port /dev/ttyUSB0 --holdover-test --duration 300 --interval 10

# Длинный тест (1 час)
python run_cli.py --port /dev/ttyUSB0 --holdover-test --duration 3600 --interval 10

# Очень длинный тест (24 часа)
python run_cli.py --port /dev/ttyUSB0 --holdover-test --duration 86400 --interval 60
```

#### Анализ логов

```bash
# Анализ существующего файла
python run_cli.py --parse-log examples/sample_holdover_log.txt

# Анализ с сохранением отчета
python run_cli.py --parse-log examples/sample_holdover_log.txt --output analysis_report.txt
```

### Web Версия

#### Запуск

```bash
# Базовый запуск
python run_web.py

# Запуск для доступа из сети
python run_web.py --host 0.0.0.0 --port 8080

# Запуск в режиме отладки
python run_web.py --debug
```

#### Использование веб-интерфейса

1. Откройте браузер и перейдите по адресу http://localhost:8080
2. Настройте параметры соединения (порт, скорость передачи)
3. Нажмите "Connect" для подключения к SA5X
4. Используйте панели для:
   - Мониторинга в реальном времени
   - Запуска тестов holdover
   - Анализа загруженных логов
   - Настройки конфигурации

## Устранение неполадок

### Проблемы с подключением

```bash
# Проверка доступных портов
ls /dev/tty*

# Проверка прав доступа
ls -l /dev/ttyUSB0

# Добавление прав
sudo chmod 666 /dev/ttyUSB0
```

### Проблемы с зависимостями

```bash
# Обновление pip
pip install --upgrade pip

# Переустановка зависимостей
pip uninstall -r requirements.txt
pip install -r requirements.txt
```

### Проблемы с веб-интерфейсом

```bash
# Проверка порта
netstat -tulpn | grep 8080

# Запуск на другом порту
python run_web.py --port 8081
```

### Логи и отладка

```bash
# Включение подробного вывода
python run_cli.py --verbose --port /dev/ttyUSB0

# Просмотр логов
tail -f sa5x_monitor.log
```

## Разработка

### Установка для разработки

```bash
# Установка дополнительных зависимостей
pip install -r requirements.txt
pip install pytest black flake8

# Запуск тестов
pytest tests/ -v

# Форматирование кода
black sa5x_monitor/
flake8 sa5x_monitor/
```

### Структура проекта

```
sa5x_monitor/
├── cli/                    # CLI версия
├── web/                    # Web версия
├── utils/                  # Общие утилиты
├── config/                 # Конфигурация
├── tests/                  # Тесты
├── examples/               # Примеры
├── requirements.txt        # Зависимости
├── README.md              # Документация
├── INSTALL.md             # Инструкции по установке
├── run_cli.py             # Запуск CLI
└── run_web.py             # Запуск Web
```

## Поддержка

При возникновении проблем:

1. Проверьте логи в файле `sa5x_monitor.log`
2. Убедитесь, что все зависимости установлены
3. Проверьте права доступа к последовательному порту
4. Создайте issue в репозитории проекта с подробным описанием проблемы