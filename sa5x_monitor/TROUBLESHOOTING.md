# SA5X Monitor - Устранение неполадок

## Проблемы с подключением к серийному порту

### Ошибка: "Serial port /dev/ttyS6 does not exist"

1. **Проверьте, существует ли порт:**
   ```bash
   ls -la /dev/ttyS6
   ```

2. **Создайте символическую ссылку (если порт физически находится в другом месте):**
   ```bash
   sudo ln -s /dev/ttyS0 /dev/ttyS6
   ```

3. **Проверьте доступные порты:**
   ```bash
   python3 sa5x_monitor/test_serial_connection.py
   ```

### Ошибка: "Permission denied"

1. **Добавьте пользователя в группу dialout:**
   ```bash
   sudo usermod -a -G dialout $USER
   ```
   После этого нужно выйти и войти в систему заново.

2. **Временное решение - изменить права доступа:**
   ```bash
   sudo chmod 666 /dev/ttyS6
   ```

3. **Проверьте текущие группы пользователя:**
   ```bash
   groups
   ```

### Ошибка: "Device or resource busy"

1. **Проверьте, не используется ли порт другим процессом:**
   ```bash
   sudo lsof /dev/ttyS6
   ```

2. **Остановите процесс, использующий порт:**
   ```bash
   sudo kill -9 <PID>
   ```

### Проверка подключения

Используйте тестовый скрипт для диагностики:
```bash
python3 sa5x_monitor/test_serial_connection.py /dev/ttyS6
```

### Настройка udev правил (для постоянного решения)

Создайте файл `/etc/udev/rules.d/99-serial.rules`:
```
KERNEL=="ttyS[0-9]*", MODE="0666"
```

Затем перезагрузите правила:
```bash
sudo udevadm control --reload-rules
sudo udevadm trigger
```

## Проблемы с веб-интерфейсом

### Ошибка подключения в браузере

1. **Проверьте консоль браузера (F12)** для дополнительной информации об ошибках

2. **Проверьте логи сервера:**
   ```bash
   tail -f sa5x_monitor/sa5x_web_monitor.log
   ```

3. **Убедитесь, что сервер запущен:**
   ```bash
   python3 sa5x_monitor/run_web.py
   ```

### Отладка соединения

1. **Используйте minicom для проверки порта:**
   ```bash
   sudo minicom -D /dev/ttyS6 -b 115200
   ```

2. **Используйте screen:**
   ```bash
   sudo screen /dev/ttyS6 115200
   ```
   (Выход: Ctrl+A, затем K)

## Логирование

Для более детального логирования измените уровень в `sa5x_controller.py`:
```python
logging.basicConfig(level=logging.DEBUG)
```