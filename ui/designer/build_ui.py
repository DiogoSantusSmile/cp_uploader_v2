import os

if __name__ == '__main__':
    for file in os.listdir('.'):
        if file.endswith('.ui'):
            os.system('pyuic5 {} > ./{}'.format(file, file.replace('.ui', '.py')))
            os.system('pyrcc5 ./resources.qrc -o ../../resources_rc.py')