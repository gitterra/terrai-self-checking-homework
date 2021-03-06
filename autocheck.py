from . import utils
from . import settings
from . import ultralight
from IPython import display
import ipywidgets as widgets

class Worker(object):
    def __init__(self, hwid, content):
        self.authorized = False
        self.hwid = hwid
        self.content = content
        self.createwidgets()
        
    # Создание кнопки «Приступить»
    def createwidgets(self):
        self.button_start = widgets.Button(
            description='Приступить',
            disabled=False,
            button_style='success', # 'success', 'info', 'warning', 'danger' or ''
            tooltip='Приступить',
            icon='pencil' # (FontAwesome names without the `fa-` prefix)
            )
        self.button_start.on_click(self.authorization)
        
        # Создание поля ввода логина
        self.login_text= widgets.Text(
            value='',
            placeholder='login@login.com',
            description='Введите ваш логин (email) на учебной платформе:',
            disabled=False,
            layout=widgets.Layout(width='600px'),
            style={'description_width': 'initial'},
        )
        
            
    def authorization(self, target):
        self.user.setlogin(self.login_text.value)
        self.button_start.disabled = True
        self.authorized = self.user.autorization()
        if self.authorized:
            self.choosehw()
            self.button_start.close()
            del self.button_start
        else:
            self.button_start.disabled = False
            display.display(self.login_text)
            display.display(self.button_start)
    
    
    def choosehw(self):
        if self.user.levelid == 1:
            ultralightworker = ultralight.Worker(self.user)
            ultralightworker.start()            
            
            
    def start(self):
        if not self.authorized:
            self.user = utils.User(self.hwid, self.content)
            display.display(self.login_text)
            display.display(self.button_start)            
        else:
            self.choosehw()
