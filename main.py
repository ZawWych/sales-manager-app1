import flet as ft
import csv
import os
import requests
import json
from datetime import datetime

class GoogleSheetsManager:
    def __init__(self, web_app_url):
        self.web_app_url = web_app_url
    
    def save_to_sheets(self, data_type, data):
        """Отправляет данные в Google Sheets через Web App"""
        payload = {
            'type': data_type,
            **data
        }
        
        try:
            response = requests.post(self.web_app_url, json=payload)
            result = response.json()
            return result['success'], result['message']
        except Exception as e:
            return False, f"❌ Ошибка соединения: {str(e)}"

class SalesApp:
    def __init__(self, sheets_manager=None):
        self.csv_file = 'sales_data.csv'
        self.podzakaz_file = 'podzakaz_data.csv'
        self.categories = ["SET", "Т.люда", "Аня", "Resale", "Подзаказ"]
        self.sheets_manager = sheets_manager
        self.create_csv_if_not_exists()

    def create_csv_if_not_exists(self):
        """Создает файлы для хранения данных, если их нет"""
        # Основные продажи
        if not os.path.exists(self.csv_file):
            with open(self.csv_file, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['Дата', 'Товар', 'Цвет', 'Размер', 'Цена', 'Категория', 'Курьер', 'Сумма курьеру'])
        
        # Подзаказы
        if not os.path.exists(self.podzakaz_file):
            with open(self.podzakaz_file, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['Дата', 'Товар', 'Цвет', 'Размер', 'Цена', 'Сколько заплатили', 'Сколько осталось заплатить', 'Связь с клиентом'])

    def save_sale(self, product_name, color, size, price, category, courier_name, courier_amount):
        """Сохраняет новую продажу в файл и Google Sheets (ТАБЛИЦА ОБЫЧНЫХ ЗАКАЗОВ)"""
        try:
            date_to_save = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Сохраняем в локальный CSV
            data = [
                date_to_save,
                product_name,
                color,
                size,
                price,
                category,
                courier_name,
                courier_amount
            ]
            
            with open(self.csv_file, 'a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(data)
            
            # Сохраняем в Google Sheets (ТАБЛИЦА ОБЫЧНЫХ ЗАКАЗОВ)
            if self.sheets_manager:
                sheets_success, sheets_message = self.sheets_manager.save_to_sheets('order', {
                    'category': category,
                    'date': date_to_save,
                    'product': product_name,
                    'color': color,
                    'size': size,
                    'price': price,
                    'courier': courier_name or "",
                    'courier_amount': courier_amount or ""
                })
                
                if sheets_success:
                    return True, "✅ Данные успешно сохранены в таблицу обычных заказов!"
                else:
                    return False, f"❌ Ошибка Google Таблиц: {sheets_message}"
            
            return True, "✅ Данные успешно сохранены локально!"
            
        except Exception as e:
            return False, f"❌ Ошибка: {str(e)}"

    def save_podzakaz(self, product_name, color, size, price, paid_amount, remaining_amount, client_link):
        """Сохраняет подзаказ в отдельный файл и Google Sheets (ТАБЛИЦА ПОДЗАКАЗОВ)"""
        try:
            date_to_save = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Сохраняем в локальный CSV
            data = [
                date_to_save,
                product_name,
                color,
                size,
                price,
                paid_amount,
                remaining_amount,
                client_link
            ]
            
            with open(self.podzakaz_file, 'a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(data)
            
            # Сохраняем в Google Sheets (ОТДЕЛЬНАЯ ТАБЛИЦА ПОДЗАКАЗОВ)
            if self.sheets_manager:
                sheets_success, sheets_message = self.sheets_manager.save_to_sheets('podzakaz', {
                    'date': date_to_save,
                    'product': product_name,
                    'color': color,
                    'size': size,
                    'price': price,
                    'courier': "",  # Для подзаказов можно оставить пустым
                    'courier_amount': "",  # Для подзаказов можно оставить пустым
                    'paid': paid_amount,
                    'remaining': remaining_amount or "0",
                    'client_link': client_link or ""
                })
                
                if sheets_success:
                    return True, "✅ Подзаказ успешно сохранен в таблицу подзаказов!"
                else:
                    return False, f"❌ Ошибка Google Таблиц: {sheets_message}"
            
            return True, "✅ Подзаказ успешно сохранен локально!"
            
        except Exception as e:
            return False, f"❌ Ошибка: {str(e)}"

    def get_sales_history(self):
        """Загружает всю историю продаж из файла"""
        try:
            if not os.path.exists(self.csv_file):
                return []
            
            with open(self.csv_file, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                rows = list(reader)
                
                if rows and rows[0] == ['Дата', 'Товар', 'Цвет', 'Размер', 'Цена', 'Категория', 'Курьер', 'Сумма курьеру']:
                    rows = rows[1:]
                
                history = []
                for row in rows:
                    if len(row) >= 8:
                        history.append({
                            'Дата': row[0],
                            'Товар': row[1],
                            'Цвет': row[2],
                            'Размер': row[3],
                            'Цена': row[4],
                            'Категория': row[5],
                            'Курьер': row[6],
                            'Сумма курьеру': row[7]
                        })
                
                return history
        except Exception as e:
            print(f"Ошибка загрузки истории: {e}")
            return []

    def get_podzakaz_history(self):
        """Загружает историю подзаказов"""
        try:
            if not os.path.exists(self.podzakaz_file):
                return []
            
            with open(self.podzakaz_file, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                rows = list(reader)
                
                if rows and rows[0] == ['Дата', 'Товар', 'Цвет', 'Размер', 'Цена', 'Сколько заплатили', 'Сколько осталось заплатить', 'Связь с клиентом']:
                    rows = rows[1:]
                
                history = []
                for row in rows:
                    if len(row) >= 8:
                        history.append({
                            'Дата': row[0],
                            'Товар': row[1],
                            'Цвет': row[2],
                            'Размер': row[3],
                            'Цена': row[4],
                            'Сколько заплатили': row[5],
                            'Сколько осталось заплатить': row[6],
                            'Связь с клиентом': row[7]
                        })
                
                return history
        except Exception as e:
            print(f"Ошибка загрузки подзаказов: {e}")
            return []

    def clear_history(self, file_path):
        """Очищает историю"""
        try:
            if file_path == self.csv_file:
                with open(self.csv_file, 'w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow(['Дата', 'Товар', 'Цвет', 'Размер', 'Цена', 'Категория', 'Курьер', 'Сумма курьеру'])
            else:
                with open(self.podzakaz_file, 'w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow(['Дата', 'Товар', 'Цвет', 'Размер', 'Цена', 'Сколько заплатили', 'Сколько осталось заплатить', 'Связь с клиентом'])
            return True
        except Exception as e:
            print(f"Ошибка очистки: {e}")
            return False

def main(page: ft.Page):
    page.title = "Менеджер продаж"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    page.scroll = "adaptive"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.START

    # Инициализация менеджера Google Таблиц
    # ЗАМЕНИ ЭТОТ URL НА СВОЙ URL ИЗ GOOGLE APPS SCRIPT
    WEB_APP_URL = "https://script.google.com/macros/s/AKfycbz6pbOosDMOZGa-YELYdZSnyMcKnQjI8VN36ycROMV9EBtvyI7DqNMaBt7l_3uR4Y3K/exec"
    sheets_manager = GoogleSheetsManager(WEB_APP_URL)
    app = SalesApp(sheets_manager)
    
    # Переменная для диалога очистки
    clear_dialog = None
    
    # Поля ввода данных
    product_name = ft.TextField(label="Название товара", hint_text="Введите название товара")
    color = ft.TextField(label="Цвет", hint_text="Введите цвет")
    size = ft.TextField(label="Размер", hint_text="Введите размер")
    price = ft.TextField(
        label="Цена", 
        hint_text="Введите цену", 
        input_filter=ft.NumbersOnlyInputFilter(),
        on_change=lambda e: calculate_remaining()
    )
    
    category = ft.Dropdown(
        label="Категория товара",
        hint_text="Выберите категорию",
        options=[ft.dropdown.Option(cat) for cat in app.categories],
        on_change=lambda e: on_category_change()
    )
    
    courier_name = ft.TextField(label="Имя курьера (необязательно)", hint_text="Введите имя курьера")
    courier_amount = ft.TextField(
        label="Сумма курьеру (необязательно)", 
        hint_text="Введите сумму курьеру",
        input_filter=ft.NumbersOnlyInputFilter()
    )
    
    # Поля для подзаказа (изначально скрыты)
    paid_amount = ft.TextField(
        label="Сколько заплатили", 
        hint_text="Введите сумму", 
        input_filter=ft.NumbersOnlyInputFilter(), 
        visible=False,
        on_change=lambda e: calculate_remaining()
    )
    remaining_amount = ft.TextField(
        label="Сколько осталось заплатить", 
        hint_text="Автоматический расчет", 
        input_filter=ft.NumbersOnlyInputFilter(), 
        visible=False,
        read_only=True
    )
    client_link = ft.TextField(label="Связь с клиентом", hint_text="Ссылка или номер", visible=False)
    
    # Поле для сообщений
    result_text = ft.Text("", size=16)
    
    # Индикатор подключения к Google Таблицам
    connection_status = ft.Text("✅ Подключено к Google Таблицам", color="green", size=12, 
                               visible=bool(WEB_APP_URL and "https://script.google.com/macros/s/AKfycbz6pbOosDMOZGa-YELYdZSnyMcKnQjI8VN36ycROMV9EBtvyI7DqNMaBt7l_3uR4Y3K/exec" not in WEB_APP_URL))
    
    def calculate_remaining():
        """Автоматически рассчитывает остаток оплаты"""
        if price.value and paid_amount.value:
            try:
                total_price = float(price.value)
                paid = float(paid_amount.value)
                remaining = total_price - paid
                remaining_amount.value = str(max(0, remaining))
                page.update()
            except ValueError:
                remaining_amount.value = "0"
                page.update()
    
    def on_category_change():
        """Обработчик изменения категории"""
        is_podzakaz = category.value == "Подзаказ"
        
        # Показываем/скрываем поля подзаказа
        paid_amount.visible = is_podzakaz
        remaining_amount.visible = is_podzakaz
        client_link.visible = is_podzakaz
        
        # Для подзаказов скрываем поля курьера (они есть в основном объекте)
        courier_name.visible = not is_podzakaz
        courier_amount.visible = not is_podzakaz
        
        page.update()

    def save_click(e):
        """Обработчик кнопки Сохранить"""
        if not product_name.value:
            show_message("⚠ Введите название товара", "orange")
        elif not color.value:
            show_message("⚠ Введите цвет", "orange")
        elif not size.value:
            show_message("⚠ Введите размер", "orange")
        elif not price.value:
            show_message("⚠ Введите цену", "orange")
        elif not category.value:
            show_message("⚠ Выберите категорию", "orange")
        else:
            # Показываем индикатор загрузки
            result_text.value = "⏳ Сохранение данных..."
            result_text.color = "blue"
            page.update()
            
            if category.value == "Подзаказ":
                # Сохраняем подзаказ в ТАБЛИЦУ ПОДЗАКАЗОВ
                if not paid_amount.value:
                    show_message("⚠ Введите сумму оплаты", "orange")
                    return
                
                success, message = app.save_podzakaz(
                    product_name.value,
                    color.value,
                    size.value,
                    price.value,
                    paid_amount.value,
                    remaining_amount.value or "0",
                    client_link.value or ""
                )
            else:
                # Сохраняем обычный заказ в ТАБЛИЦУ ОБЫЧНЫХ ЗАКАЗОВ
                success, message = app.save_sale(
                    product_name.value,
                    color.value,
                    size.value,
                    price.value,
                    category.value,
                    courier_name.value or "",
                    courier_amount.value or ""
                )
            
            show_message(message, "green" if success else "red")
            
            if success:
                clear_input_fields()

    def show_message(message, color):
        """Показывает сообщение пользователю"""
        result_text.value = message
        result_text.color = color
        page.update()

    def clear_input_fields():
        """Очищает все поля ввода"""
        product_name.value = ""
        color.value = ""
        size.value = ""
        price.value = ""
        category.value = ""
        courier_name.value = ""
        courier_amount.value = ""
        paid_amount.value = ""
        remaining_amount.value = ""
        client_link.value = ""
        
        # Сбрасываем видимость полей подзаказа
        paid_amount.visible = False
        remaining_amount.visible = False
        client_link.visible = False
        courier_name.visible = True
        courier_amount.visible = True
        
        page.update()

    def show_clear_confirmation(file_to_clear, title, is_podzakaz):
        """Показывает диалог подтверждения очистки"""
        nonlocal clear_dialog
        
        def confirm_clear(e):
            """Обработчик кнопки Очистить"""
            if app.clear_history(file_to_clear):
                # Закрываем диалог СРАЗУ
                clear_dialog.open = False
                page.update()
                
                # Показываем уведомление об успехе
                page.snack_bar = ft.SnackBar(content=ft.Text("✅ История успешно очищена"))
                page.snack_bar.open = True
                
                # Обновляем страницу истории (теперь она пустая)
                show_history_page([], title, file_to_clear, is_podzakaz)
            else:
                # Показываем уведомление об ошибке
                page.snack_bar = ft.SnackBar(content=ft.Text("❌ Ошибка при очистке"))
                page.snack_bar.open = True
                page.update()

        def cancel_clear(e):
            """Обработчик кнопки Отмена"""
            clear_dialog.open = False
            page.update()

        # Создаем диалог если его еще нет
        if clear_dialog is None:
            clear_dialog = ft.AlertDialog(
                title=ft.Text("Подтверждение очистки"),
                content=ft.Text("Вы уверены, что хотите очистить всю историю продаж?\nЭто действие невозможно отменить."),
                actions=[
                    ft.TextButton("Отмена", on_click=cancel_clear),
                    ft.TextButton("Очистить", on_click=confirm_clear),
                ],
            )
            page.overlay.append(clear_dialog)
        
        # Показываем диалог
        clear_dialog.open = True
        page.update()

    def show_history_page(history, title, file_path, is_podzakaz=False):
        """Показывает страницу с историей"""
        history_content = []
        
        if not history:
            history_content = [
                ft.Container(
                    content=ft.Column([
                        ft.Text("📋", size=64),
                        ft.Text("Нет записей в истории", size=20, color="grey"),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=50,
                    alignment=ft.alignment.center
                )
            ]
        else:
            total_sales = len(history)
            total_revenue = sum(float(record.get('Цена', 0)) for record in history)
            
            history_content = [
                ft.Text(title, size=24, weight=ft.FontWeight.BOLD),
                
                # Карточки статистики
                ft.Row([
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Всего продаж", size=14, color="grey"),
                            ft.Text(str(total_sales), size=24, weight=ft.FontWeight.BOLD),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        padding=15,
                        bgcolor="#0d47a1",
                        border_radius=10,
                        expand=1
                    ),
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Общая выручка", size=14, color="grey"),
                            ft.Text(f"{total_revenue:,.0f} ₸", size=24, weight=ft.FontWeight.BOLD),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        padding=15,
                        bgcolor="#1b5e20",
                        border_radius=10,
                        expand=1
                    ),
                ]),
                ft.Divider(),
            ]
            
            # Показываем все записи (новые сверху)
            for record in reversed(history):
                date = record.get('Дата', '')[:16]
                product = record.get('Товар', '')
                color_val = record.get('Цвет', '')
                size_val = record.get('Размер', '')
                price_val = record.get('Цена', '')
                category_val = record.get('Категория', '')
                courier_val = record.get('Курьер', '')
                courier_amount_val = record.get('Сумма курьеру', '')
                
                # Создаем карточку для записи
                record_card_content = [
                    # Первая строка: товар и цена
                    ft.Row([
                        ft.Text(product, weight=ft.FontWeight.BOLD, expand=1, size=16),
                        ft.Text(f"{price_val} ₸", color="green", weight=ft.FontWeight.BOLD, size=16),
                    ]),
                    # Вторая строка: цвет и размер
                    ft.Text(f"Цвет: {color_val} | Размер: {size_val}"),
                ]
                
                if is_podzakaz:
                    # Для подзаказов
                    paid = record.get('Сколько заплатили', '')
                    remaining = record.get('Сколько осталось заплатить', '')
                    client = record.get('Связь с клиентом', '')
                    
                    record_card_content.extend([
                        ft.Text(f"Оплачено: {paid} ₸"),
                        ft.Text(f"Осталось: {remaining} ₸"),
                        ft.Text(f"Клиент: {client}") if client else ft.Text("Клиент: не указан", color="grey"),
                    ])
                else:
                    # Для обычных заказов
                    record_card_content.extend([
                        ft.Text(f"Категория: {category_val}"),
                        *([ft.Text(f"Курьер: {courier_val}")] if courier_val else []),
                        *([ft.Text(f"Сумма курьеру: {courier_amount_val} ₸")] if courier_amount_val else []),
                    ])
                
                record_card_content.append(ft.Text(f"Дата: {date}", size=12, color="grey"))
                
                record_card = ft.Card(
                    content=ft.Container(
                        ft.Column(record_card_content, spacing=5),
                        padding=15,
                    ),
                    margin=ft.margin.only(bottom=10),
                )
                
                history_content.append(record_card)
        
        # Создаем кнопки
        buttons = [
            ft.ElevatedButton(
                "Назад к добавлению заказов", 
                on_click=lambda e: show_main_page(),
                style=ft.ButtonStyle(padding=20)
            )
        ]
        
        # Добавляем кнопку очистки только если есть история
        if history:
            buttons.append(
                ft.OutlinedButton(
                    "Очистить историю", 
                    on_click=lambda e: show_clear_confirmation(file_path, title, is_podzakaz),
                    style=ft.ButtonStyle(color="red")
                )
            )
        
        history_content.append(ft.Row(buttons, alignment=ft.MainAxisAlignment.CENTER))
        
        # Показываем страницу истории
        page.clean()
        page.add(ft.Column(history_content, scroll=ft.ScrollMode.ADAPTIVE))

    def show_history(e):
        """Показывает страницу с историей продаж"""
        history = app.get_sales_history()
        show_history_page(history, "История продаж", app.csv_file)

    def show_podzakaz_history(e):
        """Показывает страницу с историей подзаказов"""
        history = app.get_podzakaz_history()
        show_history_page(history, "История подзаказов", app.podzakaz_file, is_podzakaz=True)

    def show_main_page():
        """Показывает главную страницу с формой ввода"""
        page.clean()
        page.add(
            ft.Column([
                ft.Row([
                    ft.Text("Добавление продажи", size=24, weight=ft.FontWeight.BOLD, expand=True),
                    connection_status,
                ]),
                ft.Divider(),
                product_name,
                color,
                size,
                price,
                category,
                courier_name,
                courier_amount,
                paid_amount,
                remaining_amount,
                client_link,
                ft.Row([
                    ft.ElevatedButton("Сохранить", on_click=save_click, style=ft.ButtonStyle(color="white")),
                    ft.OutlinedButton("История продаж", on_click=show_history),
                    ft.OutlinedButton("Подзаказы", on_click=show_podzakaz_history),
                ]),
                result_text,
            ], scroll=ft.ScrollMode.ADAPTIVE)
        )

    # Запускаем приложение с главной страницы
    show_main_page()

if __name__ == "__main__":
    ft.app(target=main)