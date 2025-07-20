#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MAC SA-53 Simulator
Симулятор для тестирования GUI приложения MAC SA-53
"""

import socket
import threading
import time
import random
from datetime import datetime

class MacSimulator:
    def __init__(self, host='localhost', port=12345):
        self.host = host
        self.port = port
        self.running = False
        self.server_socket = None
        
        # Симулированные значения параметров
        self.parameters = {
            "DisciplineLocked": "1",
            "DisciplineThresholdPps0": "20",
            "PpsInDetected": "1", 
            "LockProgress": "100",
            "PpsSource": "0",
            "LastCorrection": str(random.randint(-100, 100)),
            "DigitalTuning": str(random.randint(1000, 2000)),
            "Phase": str(random.randint(-500, 500)),
            "Temperature": f"{random.uniform(20.0, 40.0):.1f}",
            "serial": "SA53-001",
            "Locked": "1",
            "PhaseLimit": "1000",
            "EffectiveTuning": str(random.randint(1500, 1800)),
            "PpsWidth": "80000000",
            "TauPps0": "10000",
            "PpsOffset": "-30",
            "Disciplining": "1",
            "PhaseMetering": "0",
            "CableDelay": "0"
        }
        
    def start(self):
        """Запуск симулятора"""
        self.running = True
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(1)
        
        print(f"MAC Simulator запущен на {self.host}:{self.port}")
        
        # Поток для обновления параметров
        update_thread = threading.Thread(target=self.update_parameters, daemon=True)
        update_thread.start()
        
        while self.running:
            try:
                client_socket, address = self.server_socket.accept()
                print(f"Подключение от {address}")
                
                client_thread = threading.Thread(
                    target=self.handle_client, 
                    args=(client_socket,), 
                    daemon=True
                )
                client_thread.start()
                
            except Exception as e:
                if self.running:
                    print(f"Ошибка сервера: {e}")
                break
                
    def stop(self):
        """Остановка симулятора"""
        self.running = False
        if self.server_socket:
            self.server_socket.close()
            
    def update_parameters(self):
        """Обновление параметров для симуляции изменений"""
        while self.running:
            # Обновляем некоторые параметры случайными значениями
            self.parameters["LastCorrection"] = str(random.randint(-100, 100))
            self.parameters["Phase"] = str(random.randint(-500, 500))
            self.parameters["Temperature"] = f"{random.uniform(20.0, 40.0):.1f}"
            self.parameters["DigitalTuning"] = str(random.randint(1000, 2000))
            self.parameters["EffectiveTuning"] = str(random.randint(1500, 1800))
            
            time.sleep(2)  # Обновляем каждые 2 секунды
            
    def handle_client(self, client_socket):
        """Обработка клиентских команд"""
        try:
            while self.running:
                data = client_socket.recv(1024).decode().strip()
                if not data:
                    break
                    
                print(f"Получена команда: {data}")
                response = self.process_command(data)
                
                if response:
                    client_socket.send((response + "\n").encode())
                    
        except Exception as e:
            print(f"Ошибка при обработке клиента: {e}")
        finally:
            client_socket.close()
            
    def process_command(self, command):
        """Обработка команд MAC"""
        try:
            # Удаляем фигурные скобки
            if command.startswith('{') and command.endswith('}'):
                command = command[1:-1]
                
            parts = command.split(',')
            
            if len(parts) >= 2:
                action = parts[0]
                param = parts[1]
                
                if action == "get":
                    if param in self.parameters:
                        return self.parameters[param]
                    else:
                        return "ERROR: Unknown parameter"
                        
                elif action == "set" and len(parts) >= 3:
                    value = parts[2]
                    if param in self.parameters:
                        self.parameters[param] = value
                        return "OK"
                    else:
                        return "ERROR: Unknown parameter"
                        
                elif action == "store":
                    return "OK"
                    
                elif action == "latch":
                    return "OK"
                    
            return "ERROR: Invalid command"
            
        except Exception as e:
            return f"ERROR: {e}"

def main():
    """Главная функция симулятора"""
    simulator = MacSimulator()
    
    try:
        simulator.start()
    except KeyboardInterrupt:
        print("\nОстановка симулятора...")
        simulator.stop()

if __name__ == "__main__":
    main()

