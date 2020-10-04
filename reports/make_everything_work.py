import time
'''
    Sequentially выполняем скрипты;
    Каждый скрипт формирует отдельный отчёт;
    time.sleep() позволяет избежать каши в логах;
'''

exec(open('../resources/scripts/script_1.py', encoding='UTF8').read())
time.sleep(0.7)
exec(open('../resources/scripts/script_2.py', encoding='UTF8').read())
time.sleep(0.7)
exec(open('../resources/scripts/script_3.py', encoding='UTF8').read())