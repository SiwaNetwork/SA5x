# Быстрый старт: Анализ лог-файлов для Frequency Stability и Allan Deviation

## 🎯 Проблема решена!

Теперь данные из лог и CSV файлов корректно подгружаются на графики Frequency Stability и Allan Deviation Analysis.

## 🚀 Как использовать

### 1. Запуск веб-интерфейса

```bash
cd sa5x_monitor
python3 web/app.py
```

Откройте браузер: `http://localhost:8080`

### 2. Загрузка лог-файла

1. В веб-интерфейсе найдите раздел **"Log Analysis"**
2. Нажмите **"Choose File"** и выберите ваш лог-файл
3. Нажмите **"Upload & Analyze"**

### 3. Просмотр результатов

После загрузки автоматически обновятся:
- ✅ **Frequency Stability** график
- ✅ **Allan Deviation Analysis** график  
- ✅ **Temperature & Electrical** график
- ✅ **Статистика анализа**

## 📊 Поддерживаемые форматы

### Лог-файлы
```
# Format: timestamp,frequency_error,temperature,voltage,current,status
0,1.23e-04,25.1,12.0,0.15,LOCKED
10,1.24e-04,25.2,12.0,0.15,LOCKED
20,1.22e-04,25.1,12.0,0.15,LOCKED
```

### CSV файлы
```csv
timestamp,frequency_error,temperature,voltage,current,status
0,1.23e-04,25.1,12.0,0.15,LOCKED
10,1.24e-04,25.2,12.0,0.15,LOCKED
```

## 🔍 Что анализируется

### Frequency Stability
- Стабильность частоты
- Дрейф частоты
- Статистика ошибок частоты

### Allan Deviation
- 1-секундное отклонение Аллана
- Отклонения для tau = 1, 10, 100, 1000 секунд
- Анализ стабильности во времени

### Temperature Analysis
- Стабильность температуры
- Диапазон температур
- Статистика температурных изменений

## 🧪 Тестирование

Для проверки функциональности:

```bash
python3 test_log_analysis.py
```

Ожидаемый результат:
```
✅ Log analysis completed successfully
✅ Allan deviation calculation working
✅ Frequency stability analysis working
✅ Temperature analysis working
```

## 📈 Пример результатов

```
=== Frequency Analysis ===
Frequency stability: 1.23e-06
Frequency drift rate: 2.60e-10
Frequency error range: 1.22e-04 to 1.26e-04

=== Allan Deviation Analysis ===
Allan deviation (1s): 1.27e-06
Tau=1s: 1.27e-06
Tau=10s: 1.27e-06
Tau=100s: 1.12e-06
Tau=1000s: 2.12e-06
```

## ⚡ Ключевые улучшения

1. **Поддержка научной нотации** - корректная обработка `1.23e-04`
2. **Автоматическое обновление графиков** - данные из логов сразу отображаются
3. **Расширенная статистика** - полный анализ всех параметров
4. **Интеграция с веб-интерфейсом** - seamless опыт пользователя

## 🎉 Результат

Теперь вы можете:
- ✅ Загружать любые лог-файлы
- ✅ Анализировать Frequency Stability
- ✅ Рассчитывать Allan Deviation
- ✅ Просматривать данные на интерактивных графиках
- ✅ Получать детальную статистику

**Проблема полностью решена!** 🚀