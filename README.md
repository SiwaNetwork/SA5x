# SA5X Контроллер Атомных Часов

Программа на Python для связи с модулем атомных часов Microchip SA5X через последовательный интерфейс.

## Возможности

- Последовательная связь с модулем SA5X на скорости 57600 бод (по умолчанию)
- Поддержка всех команд, предоставленных в документации SA5X
- Интерфейс командной строки с несколькими режимами работы
- Интерактивный режим для управления в реальном времени
- Комплексный мониторинг статуса
- Автоматическое применение конфигурации

## Установка

1. Установите зависимости Python:
```bash
pip install -r requirements.txt
```

2. Убедитесь, что у вас есть доступ к последовательному порту (обычно `/dev/ttyS6` на Linux)

## Использование

### Интерфейс командной строки

Основная программа предоставляет несколько режимов работы:

#### Получить значение параметра
```bash
python sa5x_controller.py --get PpsOffset
```

#### Установить значение параметра
```bash
python sa5x_controller.py --set PpsOffset -30
```

#### Выполнить одну команду
```bash
python sa5x_controller.py --command "{get,Disciplining}"
```

#### Получить полный статус
```bash
python sa5x_controller.py --status
```

#### Применить минимальную конфигурацию
```bash
python sa5x_controller.py --min-config
```

#### Интерактивный режим
```bash
python sa5x_controller.py --interactive
```

### Пример скрипта

Запустите пример скрипта, чтобы увидеть все команды в действии:
```bash
python sa5x_examples.py
```

Для интерактивной демонстрации:
```bash
python sa5x_examples.py interactive
```

## Поддерживаемые команды

### Минимальная необходимая конфигурация
Программа поддерживает минимальную конфигурацию, как указано:

```
{set,Disciplining,1}
{set,PpsWidth,80000000}
{set,TauPps0,10000}
{set,PpsOffset,-30}
{set,DisciplineThresholdPps0,20}
{store}
```

### Команды получения
- `{get,PpsOffset}` - Получить смещение PPS
- `{get,DisciplineLocked}` - Проверить, заблокирована ли дисциплина
- `{get,Locked}` - Проверить, заблокировано ли
- `{get,Disciplining}` - Получить статус дисциплины
- `{get,Phase}` - Получить информацию о фазе
- `{get,TauPps0}` - Получить Tau для PPS0
- `{get,DigitalTuning}` - Получить статус цифровой настройки
- `{get,JamSyncing}` - Получить статус синхронизации Jam
- `{get,PhaseLimit}` - Получить лимит фазы
- `{get,DisciplineThresholdPps0}` - Получить порог дисциплины
- `{get,PpsInDetected}` - Проверить, обнаружен ли вход PPS
- `{get,LockProgress}` - Получить прогресс блокировки
- `{get,PpsSource}` - Получить источник PPS
- `{get,LastCorrection}` - Получить последнюю коррекцию

### Команды установки
- `{set,PpsOffset,value}` - Установить смещение PPS
- `{set,PpsWidth,value}` - Установить ширину импульса PPS
- `{set,Disciplining,value}` - Включить/выключить дисциплину
- `{set,TauPps0,value}` - Установить Tau для PPS0
- `{set,PhaseLimit,value}` - Установить лимит фазы
- `{set,DisciplineThresholdPps0,value}` - Установить порог дисциплины

### Команда сохранения
- `{store}` - Сохранить конфигурацию во флэш-память

## Конфигурация

### Настройки последовательного порта
- **Порт по умолчанию**: `/dev/ttyS6`
- **Скорость по умолчанию**: 57600
- **Биты данных**: 8
- **Четность**: Нет
- **Стоп-биты**: 1
- **Таймаут**: 1 секунда

### Пользовательский порт/скорость
```bash
python sa5x_controller.py --port /dev/ttyS7 --baudrate 115200 --status
```

## Структура программы

### Класс SA5XController
Основной класс контроллера предоставляет:

- **Управление соединением**: `connect()`, `disconnect()`
- **Интерфейс команд**: `send_command()`, `get_parameter()`, `set_parameter()`
- **Конфигурация**: `store_configuration()`, `apply_minimum_configuration()`
- **Мониторинг статуса**: `get_status()`
- **Удобные методы**: `enable_disciplining()`, `set_pps_offset()`, и т.д.

### Обработка ошибок
- Ошибки последовательного соединения
- Обработка таймаутов команд
- Валидация параметров
- Корректное отключение

## Команды интерактивного режима

При использовании интерактивного режима вы можете использовать эти команды:

- `get <parameter>` - Получить значение параметра
- `set <parameter> <value>` - Установить значение параметра
- `status` - Показать все параметры
- `min-config` - Применить минимальную конфигурацию
- `store` - Сохранить конфигурацию
- `quit` - Выйти

## Примеры

### Базовое использование
```python
from sa5x_controller import SA5XController

# Создать контроллер
controller = SA5XController(port="/dev/ttyS6", baudrate=57600)

# Подключиться
if controller.connect():
    # Получить параметр
    offset = controller.get_parameter("PpsOffset")
    print(f"Смещение PPS: {offset}")
    
    # Установить параметр
    controller.set_parameter("PpsOffset", -30)
    
    # Сохранить конфигурацию
    controller.store_configuration()
    
    # Отключиться
    controller.disconnect()
```

### Применить минимальную конфигурацию
```python
controller = SA5XController()
if controller.connect():
    success = controller.apply_minimum_configuration()
    if success:
        print("Конфигурация успешно применена")
    controller.disconnect()
```

## Устранение неполадок

### Проблемы с подключением
1. Проверьте, существует ли последовательный порт: `ls /dev/ttyS*`
2. Проверьте права доступа: `sudo chmod 666 /dev/ttyS6`
3. Проверьте, не использует ли другой программой порт
4. Попробуйте другие скорости, если необходимо

### Проблемы с командами
1. Убедитесь в правильном формате команды: `{get,ParameterName}`
2. Проверьте, что имена параметров соответствуют документации SA5X
3. Убедитесь, что числовые значения находятся в допустимых диапазонах

### Проблемы с правами доступа
```bash
sudo usermod -a -G dialout $USER
# Затем выйдите и войдите снова
```

## Ссылки

- [Руководство пользователя SA5X](http://ww1.microchip.com/downloads/en/DeviceDoc/Miniature-Atomic-Clock-MAC-SA5X-Users-Guide-DS50002938A.pdf)
- [Страница продукта Microchip SA5X](https://www.microchip.com/en-us/product/SA5X)

## Лицензия

Эта программа предоставляется как есть для образовательных и разработческих целей.