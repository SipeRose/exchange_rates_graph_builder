import re
import mechanicalsoup
from matplotlib import pyplot as plt
from ATON2.Addition.url import url
import ATON2.Addition.dictionary as dictionary


class GraphBuilder:  # При инициализации подается список выбранных стран и диапазон дат

    def __init__(self, countries_list: list, first_day, first_month, first_year, last_day, last_month, last_year):

        self.url = url  # Сайт Финмаркет
        self.countries_list = countries_list  # Список выбранных стран
        self.first_day = first_day  # Диапазон дат
        self.first_month = first_month
        self.first_year = first_year
        self.last_day = last_day
        self.last_month = last_month
        self.last_year = last_year

    def build_graph(self):  # Функция потроения графика

        fig, ax = plt.subplots(figsize=(8, 8))
        country_values = self.get_country_values()  # value тэгов option для выбора страны в списке select

        browser = mechanicalsoup.StatefulBrowser()  # Парсинг страниц Финмаркет
        browser.open(self.url)
        i = 0
        for value in country_values:
            self.country_and_date_selector(browser, value)  # Выбор диапазона дат и валюты
            data = self.get_data_from_html(browser)
            dates, changes = self.extract_dates_and_changes(data)
            ax.plot(dates, changes, linewidth=0.6, label=self.countries_list[i])
            i += 1

        self.ax_settings(ax)
        plt.title(f'Относительное изменение курсов валют в %\n за период {self.first_day} {self.first_month} '
                  f'{self.first_year} - {self.last_day} {self.last_month} {self.last_year}. \nЕсли дата начала периода'
                  f' старше даты окончания,\n выводится график за последний месяц')
        plt.xticks([])
        plt.show()

    def country_and_date_selector(self, browser, value):  # Заполнение формы выбора валюты и диапазона дат
        browser.select_form('form[action="/currency/rates/#archive"]')
        browser["cur"] = value  # Выбор нужного диапазона дат по значению атрибутов
        browser["bd"] = self.first_day
        browser["bm"] = dictionary.months_values[self.first_month]
        browser["by"] = self.first_year
        browser["ed"] = self.last_day
        browser["em"] = dictionary.months_values[self.last_month]
        browser["ey"] = self.last_year
        browser.submit_selected()

    def get_country_values(self):  # Получение value для каждой валюты из словаря

        country_values = []
        for country in self.countries_list:
            country_values.append(dictionary.Countries[country])

        return country_values

    def get_data_from_html(self, browser):  # Выделение информации из таблицы курсов и освобождение HTML от тэгов

        html_code = self.decoder(browser)
        pattern1 = '<tbody.*?>.*?</tbody>'
        pattern2 = '<td.*?>.*?</td>'
        data_list = re.findall(pattern1, html_code)  # поиск с помощью регулярных выражений
        data_list = re.findall(pattern2, data_list[0])
        data_list = [re.sub('<.*?>', '', data).replace(',', '.') for data in data_list]

        return data_list

    @staticmethod
    def decoder(browser):  # Декодер для HTML, на вход: browser - объект mechanicalsoup.StatefulBrowser(),

        return ((browser.page.decode('windows-1251').replace('\n', '')).replace("\xa0", '')).replace(' ', '')

    @staticmethod
    def extract_dates_and_changes(data_list):  # Получение даты и относительного изменения курса валюты. На вход -
        # список строк: дата, количество, курс, изменение с содержащими их тэгами HTML

        changes = []  # Относительные изменения курсов
        dates = []   # Даты

        i = 0
        for data in data_list:
            if i == 0:
                i += 1
                dates.append(re.sub('<.*?>', "", data))  # Получение даты
            elif i == 1:
                i += 1
            elif i == 2:
                new_price = float(re.sub('<.*?>', "", data).replace(',', '.'))  # Цена на текущую дату
                i += 1
            else:
                i = 0
                old_price = new_price - float(re.sub('<.*?>', "", data).replace(',', '.'))  # Цена в предыдущий день
                change = (new_price / old_price - 1) * 100  # Относительное изменение курса в %
                changes.append(change)

        return dates, changes

    @staticmethod
    def ax_settings(ax):  # Настройки графика
        ax.set_ylabel('%', rotation=0, fontsize=20, position=(0, 1))
        ax.legend(loc='upper left', prop={'size': 10})
