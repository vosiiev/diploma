import os

categories = [
    'невинний',
    'сирота',
    'герой',
    'наставник',
    'мандрівник',
    'коханець',
    'бунтар',
    'творець',
    'правитель',
    'чарівник',
    'мудрець',
    'блазень',
]

directory = '/home/vosiiev/DW/program'

for item in categories:
    os.mkdir(os.path.join(directory, 'test', item))
