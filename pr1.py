class DataBase:
    def __init__(self, db_name):
        self.db_name = db_name
        
        self.users = {
            1: ["user@example.com", "password123", "Сапегина Варвара", "Пользователь", False],
            2: ["admin@security.com", "admin123", "Медведев Михаил Александрович", "Администратор", False]
        }
        self.services = {
            1: ["online_banking", "Интернет-банкинг", "Высокий"],
            2: ["payment_system", "Платежная система", "Высокий"],
            3: ["email_service", "Почтовый сервис", "Средний"]
        }
        self.security_events = {
            1: ["15.03.2025", 1, 1, "login_attempt", "Успешный вход с IP 192.168.1.1", "Успех"],
            2: ["14.03.2025", 1, 2, "failed_login", "Неверный пароль с IP 185.130.5.253", "Отказ"],
            3: ["14.03.2025", 1, 3, "suspicious_activity", "Подозрительный вход с нового устройства", "Предупреждение"]
        }
        self.events_count = 3
    
    def add_event(self, date, user_id, service_id, event_type, description, status):
        new_event_id = self.events_count + 1
        self.security_events[new_event_id] = [date, user_id, service_id, event_type, description, status]
        self.events_count += 1
    
    def update_event(self, id, new_status, new_description):
        if id in self.security_events:
            self.security_events[id][5] = new_status
            self.security_events[id][4] = new_description
    
    def view_event(self, id):
        if id in self.security_events:
            return self.security_events[id]
        return "Событие не найдено"
    
    def get_all_events(self):
        return self.security_events


class AuthHandler:
    @staticmethod
    def login(users, email, password):
        for user_id, (user_email, user_pass, full_name, role, is_blocked) in users.items():
            if user_email == email and user_pass == password:
                if is_blocked:
                    return None, None, None, "Аккаунт заблокирован"
                return user_id, full_name, role, "Успешный вход"
        return None, None, None, "Неверные учетные данные"


class AccessControl:
    @staticmethod
    def can_view_all(role):
        return role == "Администратор"
    
    @staticmethod
    def can_block(role):
        return role == "Администратор"


class SecurityService:
    def __init__(self, db_name):
        self.db = DataBase(db_name)
        self.auth = AuthHandler()
        self.access = AccessControl()
    
    def login(self, email, password):
        return self.auth.login(self.db.users, email, password)
    
    def view_all_events(self, user_id, role):
        if user_id in self.db.users:
            all_events = self.db.get_all_events()
            if not self.access.can_view_all(role):
                return {k: v for k, v in all_events.items() if v[1] == user_id}
            return all_events
        return "Пользователь не найден"
    
    def add_event(self, date, user_id, service_id, event_type, description, status):
        self.db.add_event(date, user_id, service_id, event_type, description, status)
    
    def update_event(self, id, new_status, new_description):
        self.db.update_event(id, new_status, new_description)
    
    def view_event(self, id):
        return self.db.view_event(id)
    
    def get_service_name(self, service_id):
        if service_id in self.db.services:
            return self.db.services[service_id][1]
        return "Неизвестный сервис"
    
    def block_user(self, user_id, current_user_role):
        if not self.access.can_block(current_user_role):
            return False, "Недостаточно прав"
        
        if user_id in self.db.users:
            self.db.users[user_id][4] = True
            return True, "Пользователь заблокирован"
        return False, "Пользователь не найден"


class InteractionMenu:
    def __init__(self, db_name):
        self.security_service = SecurityService(db_name)
        self.logged_in = False
        self.current_user_id = None
        self.current_user_name = None
        self.current_user_role = None
    
    def start_menu(self):
        while True:
            print("\n===== СИСТЕМА БЕЗОПАСНОСТИ ЭЛЕКТРОННЫХ СЕРВИСОВ =====")
            print("1. Войти в систему")
            print("2. Просмотреть все события")
            print("3. Добавить событие")
            print("4. Обновить событие")
            print("5. Просмотреть событие по ID")
            print("6. Заблокировать пользователя (только админ)")
            print("7. Выйти")
            action = input("Введите ваш выбор: ")
            
            if action == "1":
                self.login_menu()
            elif action == "2":
                self.view_all_events_menu()
            elif action == "3":
                self.add_event_menu()
            elif action == "4":
                self.update_event_menu()
            elif action == "5":
                self.view_event_menu()
            elif action == "6":
                self.block_user_menu()
            elif action == "7":
                print("До свидания!")
                break
            else:
                print("Неверный выбор")
    
    def login_menu(self):
        if self.logged_in:
            print("Вы уже вошли!")
            return
        email = input("Email: ")
        password = input("Пароль: ")
        user_id, name, role, message = self.security_service.login(email, password)
        if user_id:
            self.logged_in = True
            self.current_user_id = user_id
            self.current_user_name = name
            self.current_user_role = role
            print(f"Добро пожаловать, {name}! Роль: {role}")
        else:
            print(message)
    
    def view_all_events_menu(self):
        if not self.logged_in:
            print("Сначала войдите!")
            return
        events = self.security_service.view_all_events(self.current_user_id, self.current_user_role)
        if events == "Пользователь не найден":
            print("Пользователь не найден")
        else:
            print("\n===== СОБЫТИЯ =====")
            for eid, edata in events.items():
                service_name = self.security_service.get_service_name(edata[2])
                print(f"ID: {eid} | Дата: {edata[0]} | Сервис: {service_name}")
                print(f"Тип: {edata[3]} | Статус: {edata[5]}")
                print(f"Описание: {edata[4]}")
                print("-" * 50)
    
    def add_event_menu(self):
        if not self.logged_in:
            print("Сначала войдите!")
            return
        date = input("Дата (ДД.ММ.ГГГГ): ")
        print("Доступные сервисы:")
        for sid, sdata in self.security_service.db.services.items():
            print(f"  {sid}: {sdata[1]} (уровень риска: {sdata[2]})")
        service_id = int(input("Введите ID сервиса: "))
        event_type = input("Тип (login_attempt/failed_login/suspicious_activity): ")
        description = input("Описание: ")
        status = input("Статус (Успех/Отказ/Предупреждение): ")
        self.security_service.add_event(date, self.current_user_id, service_id, event_type, description, status)
        print("Событие добавлено!")
    
    def update_event_menu(self):
        if not self.logged_in:
            print("Сначала войдите!")
            return
        eid = int(input("ID события: "))
        new_status = input("Новый статус: ")
        new_description = input("Новое описание: ")
        self.security_service.update_event(eid, new_status, new_description)
        print(f"Событие {eid} обновлено!")
    
    def view_event_menu(self):
        if not self.logged_in:
            print("Сначала войдите!")
            return
        eid = int(input("ID события: "))
        event = self.security_service.view_event(eid)
        if event == "Событие не найдено":
            print("Событие не найдено")
        else:
            service_name = self.security_service.get_service_name(event[2])
            print(f"\n=== СОБЫТИЕ {eid} ===")
            print(f"Дата: {event[0]}")
            print(f"ID пользователя: {event[1]}")
            print(f"Сервис: {service_name}")
            print(f"Тип: {event[3]}")
            print(f"Описание: {event[4]}")
            print(f"Статус: {event[5]}")
    
    def block_user_menu(self):
        if not self.logged_in:
            print("Сначала войдите!")
            return
        uid = int(input("ID пользователя для блокировки: "))
        if uid == self.current_user_id:
            print("Нельзя заблокировать себя!")
            return
        success, message = self.security_service.block_user(uid, self.current_user_role)
        print(message)


if __name__ == "__main__":
    app = InteractionMenu("безопасность_электронных_сервисов")
    app.start_menu()
