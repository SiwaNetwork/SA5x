# Quick Start: Log Analysis Demo

## 🚀 Быстрый старт для тестирования Log Analysis

### Шаг 1: Запуск веб-интерфейса
```bash
cd sa5x_monitor
python3 run_web.py
```

### Шаг 2: Открытие интерфейса
Откройте браузер: `http://localhost:8080`

### Шаг 3: Тестирование Log Analysis
1. Найдите секцию **"Log Analysis"** на странице
2. Нажмите **"Choose File"**
3. Выберите один из демо файлов:
   - `uploads/demo_holdover_test.log` ✅
   - `uploads/demo_holdover_test_alt.log` ✅  
   - `uploads/demo_holdover_test.csv` ✅
4. Нажмите **"Upload & Analyze"**

### Шаг 4: Просмотр результатов
Вы увидите анализ с данными:
- **Duration**: 1000.00 seconds
- **Measurements**: 101
- **Frequency Stability**: ~1.2e-04
- **Temperature Range**: 25.4°C - 35.4°C

## 📁 Демо файлы

Все файлы содержат реалистичные данные holdover теста:
- 101 измерение каждые 10 секунд
- Длительность: 16.7 минут
- Статус: LOCKED
- Реалистичные изменения частоты, температуры, напряжения и тока

## ✅ Проверка работы

Запустите тест парсера:
```bash
python3 simple_log_test.py
```

Должны увидеть:
```
✅ Successfully parsed uploads/demo_holdover_test.log
   Duration: 1000.00 seconds
   Measurements: 101
   Frequency error range: 1.23e-04 to 1.32e-03
   Temperature range: 25.4°C to 35.4°C
   Primary status: LOCKED
```

## 🔧 Устранение проблем

### Файл не загружается?
- Проверьте, что файл выбран
- Убедитесь, что файл имеет расширение .log, .txt или .csv

### Нет результатов?
- Проверьте логи веб-сервера
- Убедитесь, что папка uploads/ существует
- Попробуйте другой демо файл

### Ошибка парсинга?
- Используйте демо файлы как образец
- Проверьте формат данных в вашем файле

## 📖 Подробная документация

См. `LOG_ANALYSIS_DEMO.md` для подробной информации о форматах файлов и создании собственных демо данных.