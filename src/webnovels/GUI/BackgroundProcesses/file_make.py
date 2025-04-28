import os

def create_new_folder(name):
    os.mkdir(name)
    return None

def create_new_txt_file(name):
    if name[-4:] != '.txt':
        name += '.txt'
    file = open(name, 'w+', encoding='utf-8')
    file.close()
    
if __name__ == '__main__':
    main()