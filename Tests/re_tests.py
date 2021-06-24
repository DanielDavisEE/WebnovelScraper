import re, time, sys

#str = "nope hello world"

##Check if the string starts with 'hello':

#x = re.findall("^hello|^nope", str)
#if (x):
  #print("Yes, the string starts with 'hello' or 'nope'")
#else:
  #print("No match")

#text = 'asdfsad.dasfsdf'

#x = re.search(r"\S\.\S", text)

#if x:
    #print(1)


#index = text.find('...')
#print(index)
#if index > -1:
    #print(text[:index+2] + ' ' + text[index+2:])

#word = 'b.l.o.o.d.y'
#replacement = 'bloody'
#line = 'b.l.o.o.d.y'

#t = re.sub(word, replacement, line)
#print(t)

'''word = 'of...six...How'

num = word.count('...')
print(num)
if num > 0:
    j = 0
    for _ in range(num):
        index = word[j:].find('...') + j
        if index > -1:
            word = word[:index+3] + ' ' + word[index+3:]
        j = index + 3
    
print(word)'''

for x in range(5):
    print('Loading'+'.'*x, end='\r')
    
    sys.stdout.write("\033[F")
    time.sleep(1)