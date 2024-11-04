import csv
import requests
from io import StringIO
from pprint import pprint
import re


def read_file(hw_url):
    """
    Загружает CSV-файл с URL-адреса и преобразует его в список списков.

    Параметры:
    hw_url (str): URL-адрес CSV-файла

    Возвращает:
    list: список списков, представляющий телефонную книгу
    """
    response = requests.get(hw_url)
    response.raise_for_status()  # Проверка на успешность запроса, выбрасывает исключение при ошибке

    file_content = StringIO(response.text)
    reader = csv.reader(file_content)
    phonebook = list(reader)

    return phonebook


def put_things_in_order(phonebook):
    """
    Обрабатывает телефонную книгу для упорядочивания имен и удаления лишних данных.

    Параметры:
    phonebook (list): оригинальный список списков, представляющий телефонную книгу

    Возвращает:
    list: отредактированный список списков с упорядоченными именами
    """
    phonebook_corrected = []
    value_for_remove = ''  # Используется для удаления пустых строк в имени

    headers = phonebook.pop(0)  # Извлекаем заголовки
    phonebook_corrected.append(headers)  # Добавляем заголовки в новый список

    for row in phonebook:
        full_name = ' '.join(row[:3])  # Объединяем первые три элемента в полное имя
        full_name_list = full_name.split(' ')  # Разделяем на составляющие имя, фамилию, отчество
        # Убираем пустые значения из списка имен
        full_name_list = [el for el in full_name_list if el != value_for_remove]
        # Дополняем список до трех элементов (если не хватает отчества, добавляется пустая строка)
        if len(full_name_list) < 3:
            full_name_list += [''] * (3 - len(full_name_list))
        # Полный список данных, объединяющий имя и другие поля
        full = full_name_list + row[3:]
        phonebook_corrected.append(full)

    return phonebook_corrected


def merge_duplicates(phonebook):
    """
    Объединяет дублирующиеся записи, сохраняя непустые данные из каждой записи.

    Параметры:
    phonebook (list): отредактированный список телефонной книги

    Возвращает:
    list: телефонная книга без дубликатов
    """
    unique_names = set()  # Хранит уникальные сочетания имени и фамилии

    # Заполняем множество уникальных имен (имя и фамилия)
    for row in phonebook[1:]:
        unique_names.add((row[0], row[1]))

    phonebook_merged = [phonebook[0]]  # Добавляем заголовки
    for names in unique_names:
        obj_for_comparison = []
        # Собираем все записи, которые имеют одинаковое имя и фамилию
        for row in phonebook[1:]:
            if names[0] == row[0] and names[1] == row[1]:
                obj_for_comparison.append(row)

        if len(obj_for_comparison) == 1:
            phonebook_merged.append(obj_for_comparison[0])  # Добавляем запись, если она уникальна
        else:
            fields_num = len(obj_for_comparison[0])
            result = ['' for _ in range(fields_num)]  # Создаем пустую строку для объединения данных

            # Объединяем непустые поля, выбирая первое непустое значение
            for i in range(fields_num):
                for row in obj_for_comparison:
                    if row[i] != '':
                        result[i] = row[i]
                        break
                else:
                    result[i] = ''  # Оставляем поле пустым, если все значения пустые

            phonebook_merged.append(result)

    return phonebook_merged


def fix_phone_number(phonebook):
    """
    Форматирует номера телефонов по шаблону +7(XXX)XXX-XX-XX и добавляет
    добавочный номер, если он присутствует.

    Параметры:
    phonebook (list): список телефонной книги

    Возвращает:
    list: телефонная книга с отформатированными номерами телефонов
    """
    # Шаблон для поиска номеров в произвольных форматах
    pattern = r'(?:\+7|8)[\s-]*\(?(\d{3})\)?[\s-]*(\d{3})[\s-]*(\d{2})[\s-]*(\d{2})(?:\s*\(?(?:(\w+\.)?)\s*(\d{4})\)?)?'
    substitution = r'+7(\1)\2-\3-\4'  # Шаблон для замены, без добавочного номера

    for row in phonebook[1:]:
        match = re.match(pattern, row[5])
        if match:
            # Форматируем номер и добавляем добавочный, если он есть
            formatted_number = re.sub(pattern, substitution, row[5])
            if match.group(6):  # Проверяем наличие добавочного номера
                formatted_number += f' доб.{match.group(6)}'
            row[5] = formatted_number.strip()  # Заменяем номер в записи

    # pprint(phonebook)  # Отключено, но полезно для отладки
    return phonebook


def write_to_csv(phonebook):
    """
    Записывает обновленную телефонную книгу в CSV-файл.

    Параметры:
    phonebook (list): телефонная книга для записи в файл
    """
    with open('phonebook_fixed.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(phonebook)


# URL исходного CSV-файла с телефонной книгой
url = 'https://raw.githubusercontent.com/netology-code/py-homeworks-advanced/master/5.Regexp/phonebook_raw.csv'

if __name__ == '__main__':
    # Обработка данных: чтение, упорядочивание, объединение дубликатов, исправление номеров, запись в файл
    write_to_csv(fix_phone_number(merge_duplicates(put_things_in_order(read_file(url)))))
