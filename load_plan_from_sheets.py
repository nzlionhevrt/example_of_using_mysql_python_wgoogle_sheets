#!/usr/bin/env python3
"""
Скрипт для загрузки данных плана выручки из Google Sheets в MySQL.
Выполняет UPSERT: обновляет существующие записи или вставляет новые.
"""

import os
import sys
import mysql.connector
from mysql.connector import Error
from datetime import datetime
import pandas as pd
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()


def get_mysql_connection():
    """Создает подключение к MySQL."""
    try:
        connection = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            port=int(os.getenv('MYSQL_PORT', 3306)),
            database=os.getenv('MYSQL_DATABASE', 'analytics_test'),
            user=os.getenv('MYSQL_USER', 'analytics_user'),
            password=os.getenv('MYSQL_PASSWORD', 'analytics_password')
        )
        return connection
    except Error as e:
        print(f"Ошибка подключения к MySQL: {e}")
        sys.exit(1)


def read_google_sheets(sheet_url):
    """
    Читает данные из Google Sheets.
    Таблица должна быть опубликована для общего доступа (без авторизации).
    """
    try:
        # Преобразуем URL в формат для экспорта CSV
        # Формат: https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit#gid=0
        # CSV: https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0
        
        if '/edit' in sheet_url:
            sheet_id = sheet_url.split('/d/')[1].split('/')[0]
            gid = '0'
            if '#gid=' in sheet_url:
                gid = sheet_url.split('#gid=')[1]
            csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
        else:
            # Если уже в формате CSV или другой формат
            csv_url = sheet_url
        
        # Читаем данные
        df = pd.read_csv(csv_url)
        
        # Проверяем наличие необходимых колонок
        required_columns = ['month', 'club_id', 'club_name', 'plan_revenue']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            print(f"Ошибка: отсутствуют необходимые колонки: {missing_columns}")
            sys.exit(1)
        
        return df
    except Exception as e:
        print(f"Ошибка чтения Google Sheets: {e}")
        print("Убедитесь, что таблица опубликована для общего доступа (без авторизации)")
        sys.exit(1)


def upsert_revenue_plan(connection, df):
    """
    Выполняет UPSERT данных в таблицу revenue_plan.
    Обновляет запись, если существует (month, club_id), иначе вставляет новую.
    """
    cursor = connection.cursor()
    
    try:
        upsert_query = """
        INSERT INTO revenue_plan (month, club_id, club_name, plan_revenue, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            club_name = VALUES(club_name),
            plan_revenue = VALUES(plan_revenue),
            updated_at = VALUES(updated_at)
        """
        
        inserted_count = 0
        updated_count = 0
        
        for _, row in df.iterrows():
            try:
                # Преобразуем month в дату
                month = pd.to_datetime(row['month']).date()
                club_id = int(row['club_id'])
                club_name = str(row['club_name']).strip()
                plan_revenue = float(str(row['plan_revenue']).replace(' ', '').replace(',', ''))
                
                now = datetime.now()
                
                cursor.execute(upsert_query, (
                    month,
                    club_id,
                    club_name,
                    plan_revenue,
                    now,
                    now
                ))
                
                # rowcount = 1 для INSERT, rowcount = 2 для UPDATE при ON DUPLICATE KEY UPDATE
                if cursor.rowcount == 1:
                    inserted_count += 1
                elif cursor.rowcount == 2:
                    updated_count += 1
                    
            except Exception as e:
                print(f"Ошибка обработки строки {row.to_dict()}: {e}")
                continue
        
        connection.commit()
        print(f"Успешно обработано: {inserted_count} новых записей, {updated_count} обновлено")
        
    except Error as e:
        connection.rollback()
        print(f"Ошибка выполнения UPSERT: {e}")
        sys.exit(1)
    finally:
        cursor.close()


def main():
    """Основная функция."""
    sheet_url = os.getenv('GOOGLE_SHEETS_URL')
    
    if not sheet_url:
        print("Ошибка: не указан GOOGLE_SHEETS_URL в .env файле")
        sys.exit(1)
    
    print("Чтение данных из Google Sheets...")
    df = read_google_sheets(sheet_url)
    print(f"Прочитано {len(df)} строк")
    
    print("Подключение к MySQL...")
    connection = get_mysql_connection()
    print("Подключение установлено")
    
    print("Выполнение UPSERT...")
    upsert_revenue_plan(connection, df)
    
    connection.close()
    print("Готово!")


if __name__ == "__main__":
    main()

