import requests, os, random, json
from . import settings
import ipywidgets as widgets
from IPython import display
from termcolor import colored
import numpy as np
import functools


class Worker(object):
    def __init__(self, user):
        self.user = user
        self.questionsid = []
        self.answerbuttons = []
        self.reload()
        self.createbtn()
        
        
    def createbtn(self):
        # Создание кнопки «Проверить»
        self.button_check = widgets.Button(
            description='Проверить',
            disabled=False,
            button_style='success', # 'success', 'info', 'warning', 'danger' or ''
            tooltip='Проверить',
            icon='search' # (FontAwesome names without the `fa-` prefix)
        )

         # Создание кнопки «Пересдать»
        self.button_retake = widgets.Button(
            description='Пересдать',
            disabled=False,
            button_style='warning', # 'success', 'info', 'warning', 'danger' or ''
            tooltip='Пересдать',
            icon='refresh' # (FontAwesome names without the `fa-` prefix)
        )

        # Создание кнопки «Зачесть ДЗ»
        self.button_send_homework = widgets.Button(
            description='Зачесть ДЗ',
            disabled=False,
            button_style='info', # 'success', 'info', 'warning', 'danger' or ''
            tooltip='Зачесть ДЗ',
            icon='check-circle'
        )   
        self.button_check.on_click(self.checkhomework)
        self.button_retake.on_click(self.showquestion)        
        self.button_send_homework.on_click(self.sendhomework)
        
        
    def reload(self):
        display.clear_output(wait=True) # Очищение экрана
        self.questionsid.clear()
        self.answerbuttons.clear()
    
    
    def start(self):
        self.showquestion(None)  
        
        
    def buttonsdisable(self):
        self.button_retake.disabled = True
        self.button_check.disabled = True
        self.button_send_homework.disabled = True
        self.button_retake.layout.display = 'None'
        self.button_check.layout.display = 'None'
        self.button_send_homework.layout.display = 'None'
        
        
    def showbuttons(self, btn):
        btn.layout.display = 'block'
        btn.disabled = False
        display.display(btn)       
        
        
    def showquestion(self, target):
        self.buttonsdisable()
        # Параметры запроса (id домашки)
        param = {'hwid': self.user.hwid}
        # Отправка запроса на сервер (получение списка из случайных 10 вопросов)
        questions = requests.get(
            os.path.join(settings.SERVER, settings.PAGE_QUESTION),
            params=param).json()
        variants = ['a','b','c','d'] # Нумерация ответов
        self.reload()
        # Визуализация вопросов
        for i, q in enumerate(questions):
            answers = q['variants'][1:-1].split("',") # Получение вариантов ответов
            self.questionsid.append(q['id']) # Сохранение id вопроса
            # Создание кнопок с вариантами ответов
            wt = widgets.ToggleButtons(
                value=None,
                options=variants,        
                disabled=False,
                button_style ='', # 'success', 'info', 'warning', 'danger' or ''
                tooltips=answers,
              )
            print('\n'*3)            
            # Печать текста вопроса
            print(colored(f'Вопрос №{i+1}: {q["text"]}:', attrs=['bold']))
            # Печать вариантов ответа
            for i in range(4):
                print(' '*5, variants[i] + ') ' + answers[i].lstrip().replace("'",""))        
            display.display(wt) # Вывод кнопок с ответами
            self.answerbuttons.append(wt) # Сохранение кнопок 
        self.showbuttons(self.button_check)
        
        
    def checkhomework(self, target):
        self.buttonsdisable()
        param = {'hwid': self.user.hwid,
             'questions': json.dumps(self.questionsid),
             'answers':'',
             'status': 0,
             'user_id': self.user.id
            }
        # Получение ответов пользователя
        useranswers = [self.answerbuttons[i].options.index(self.answerbuttons[i].value) 
                        + 1 if self.answerbuttons[i].value else 0 for i in range(10)]
        
        # Добавление ответов пользователя в параметры
        param['answers'] = json.dumps(useranswers)
        
        # Проверка ответов пользователя на сервере
        data = requests.get(os.path.join(settings.SERVER, settings.PAGE_CHECK_UL), 
                            params=param)
        # Проверка ответа сервера
        if data.status_code!=200:
            # Если сервер не обработал запрос
            display.clear_output(wait=True)
            utils.error_programm(f'Ошибка обработки запроса (status_code={data.status_code})')
            return
        else:
            # Получение результатов проверки
            result = json.loads(data.json()['result'])
       
        # Визуализация правильных/неправильных ответов на кнопках
        for i, r in enumerate(result):
            if r:
                self.answerbuttons[i].button_style = 'success'      
            else:
                self.answerbuttons[i].button_style = 'danger'
            self.answerbuttons[i].disabled = True      
        print('\n'*2)        
        # Отображение результата тестирования
        if sum(result) < 10:
            # Если есть ошибки
            print(colored(f'Ваш результат составил {utils.get_points_text(sum(result))}',
                          color='red', attrs=['bold']))
            print('   * Для повторного тестирования нажмите «Пересдать»')
            print('   * Для сдачи домшней работы нажмите «Зачесть ДЗ»')
            print('Вы можете вернуться и пересдать домашнее задание в любое время')   
            self.showbuttons(self.button_retake)
        else:
            # Если ошибок нет
            print(colored(f'Поздравляем. Вы верно ответили на все вопросы и набрали 10 баллов', 
                          color='green', attrs=['bold']))
        
        # Отображение кнопки «Зачесть ДЗ»
        self.showbuttons(self.button_send_homework)
        
        
    def sendhomework(self, target):
        display.clear_output(wait=True)# Список параметров, отправляемых на сервер    
        self.buttonsdisable()
        param = {'hwid': self.user.hwid,
                 'questions': json.dumps(self.questionsid),
                 'answers':'',
                 'status': 1,
                 'userid': self.user.id
                }
        # Получение ответов пользователя
        useranswers = [self.answerbuttons[i].options.index(self.answerbuttons[i].value) 
                        + 1 if self.answerbuttons[i].value else 0 for i in range(10)]
        
        # Добавление ответов пользователя в параметры
        param['answers'] = json.dumps(useranswers)
        
        # Проверка ответов пользователя на сервере
        data = requests.get(os.path.join(settings.SERVER, settings.PAGE_CHECK_UL), 
                            params=param)
        print(data.json()['result'])  
