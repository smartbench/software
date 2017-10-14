from kivy.base import runTouchApp
from kivy.uix.spinner import Spinner
from serial.tools.list_ports import comports

ports = sorted(comports())
ports_strings_list = []
for port in ports:
    ports_strings_list.append( port.name + ': ' + port.description )

ports_strings_list = tuple( ports_strings_list )
# print( ports_strings_list )

spinner = Spinner(
    # default value shown
    text='Select port',

    # available values
    values= ports_strings_list,

    # just for positioning in our example
    size_hint=(None, None),
    size=(100, 44),
    pos_hint={'center_x': .5, 'center_y': .5}
    )

def show_selected_value(instance,data,*largs):#(spinner, text):
    print(data.index(':'))
    spinner.text = data[0:(data.index(':'))]
    spinner.is_open = False
    spinner.size = (100,44)

    # spinner.text = spinner.text[0:(spinner.text.index(':')-1)]
    #print('The spinner', spinner, 'have text', text)

def larger_spinner():
    spinner.size = (300,44)

spinner._dropdown.unbind(on_select=spinner._on_dropdown_select)
spinner._dropdown.bind(on_select=show_selected_value)
spinner.on_release = larger_spinner
# spinner.bind(text=show_selected_value)

runTouchApp(spinner)
