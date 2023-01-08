from IPython.core.display import HTML
from IPython import display
from . import settings
import requests, os
from termcolor import colored

# Функция вывода сообщения об ошибке
def error_programm(text: str):
    print(colored(text, color='red', attrs=['bold']))

def get_points_text(points):
    if points in [0, 5 , 6, 7, 8, 9, 10]:
        return f'{points} баллов'
    if points in [2, 3, 4]:
        return f'{points} балла'
    if points == 1:
        return f' {points} балл'
    
class Keywords():
    def __init__(self, vars_):
        self.builtInFunctions = set(['abs',       'aiter',    'all',          'any',         'anext',      'ascii',   'bin',        'bool',       'breakpoint', 'bytearray',
                                     'bytes',     'callable', 'chr',          'classmethod', 'compile',    'complex', 'delattr',    'dict',       'dir',        'divmod',
                                     'enumerate', 'eval',     'exec',         'filter',      'float',      'format',  'frozenset',  'getattr',    'globals',    'hasattr',
                                     'hash',      'help',     'hex',          'id',          'input',      'int',     'isinstance', 'issubclass', 'iter',       'len', 
                                     'list',      'locals',   'map',          'max',         'memoryview', 'min',     'next',       'object',     'oct',        'open', 
                                     'ord',       'pow',      'print',        'property',    'range',      'repr',    'reversed',   'round',      'set',        'setattr', 
                                     'slice',     'sorted',   'staticmethod', 'str',         'sum',        'super',   'tuple',      'type',       'vars',       'zip'])
        self.variables = vars_
        self.error = '<p><b><font color="#880000">Обратите внимание. Вы создали одну или несколько переменных с именем встроенной функции:</font></b></p>'
        self.information = '<p>Старайтесь избегать подобных, чтобы избежать проблем в работе программ <br> <i>\
                            </p><a href="https://colab.research.google.com/drive/1kUQVE_vTJZEiNJ5yt0Zgg0MRVYslY4b4?usp=sharing"\
                            target="_blank">База знаний | Почему нельзя использовать имена встроенных функций в качестве переменных | УИИ</a>'

    def check(self) -> bool:
        intersection_func = self.builtInFunctions & set(self.variables)
        if len(intersection_func) > 0:
            list_func = ''
            for func in intersection_func:
                list_func += f'<b>&nbsp;&nbsp;&nbsp;&nbsp;{func}</b><br>'
                del self.variables[func]
            display.display(HTML(self.error + list_func + self.information))
            return False
        return True
        
class User(object):
    def __init__(self, hwid, cnt):
        self.login = ''        
        self.id = -1
        self.hwid = int(format(hwid)[1:])
        self.levelid = int(format(hwid)[0])
        self.content = cnt 
        
    def setlogin(self, email):
        self.login = email
        
    def autorization(self):
        # Список параметров, отправляемых на сервер
        param = {'login': self.login,
                 'hw_id': self.hwid,
                 'action': 1}
        # Проверка ответов пользователя на сервере
        data = requests.post(f'{settings.SERVER}{settings.PAGE}', 
                            params=param)
        if 'result' in data.json():        
            if data.json()['result']==-1:
                display.clear_output(wait=True)
                error_programm(f'Указанный email: {self.login} не найден!')        
                print('Проверьте правильность введенных данных и повторите попытку')
                return False
            elif data.json()['result']==-2:
                display.clear_output(wait=True)
                error_programm(f'В Вашей учебной программе нет данного домашнего задания!')
                print('Обратитесь к куратору для решения данной проблемы')
                return False
            else:
                self.id = data.json()['result']
                return True 
        else:
            display.clear_output(wait=True)
            error_programm(f'Ошибка выполнения запроса!')
            print('Обратитесь к куратору для решения данной проблемы')
