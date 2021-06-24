import os
import BackgroundProcesses.file_make

def create_new_novel():
    confirmation = 'n'
    while confirmation.lower() != 'y':
        title = input("Please input full novel title: ")
        confirmation = input(f"Confirm that the title will be:\n{title}\n[y,n]: ")
    if ' ' in title.strip(' \n\t'):
        tmp = title[0]
        for i in range(1, len(title)):
            if title[i-1] == ' ':
                tmp = tmp + title[i]
    
    os.makedirs(f"{title}\\Pages")
    create_new_txt_file(f"{title}\\ReplacementDict.txt")
    create_new_txt_file(f"{title}\\CensoredWords.txt")
    create_new_txt_file(f"{title}\\NonStandardWords.txt")
    create_new_txt_file(f"{title}\\RemoveWords.txt")
    create_new_txt_file(f"{title}\\{tmp}Dict.txt")
    print("Files successfully created.")

if __name__ == '__main__':
    main()