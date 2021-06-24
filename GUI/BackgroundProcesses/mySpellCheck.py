import re
from spellchecker import SpellChecker

class mySpellChecker():
    
    def __init__(self, infile, spell, replacementDict, censoredDict, nonStandardWords):
        self.infile = infile
        self.spell = spell
        self.replacementDict = replacementDict
        self.censoredDict = censoredDict
        self.nonStandardWords = nonStandardWords
    
    def word_splitter(self, word):
        potential_matches = []
        index = word.find('...')
        if index > -1:
            return [word[:index+3] + ' ' + word[index+3:]]
        index = word.find('.')
        if index > -1:
            return [word[:index+1] + ' ' + word[index+1:]]
        for i in range(len(word)):
            if (self.spell[word[:i]] 
                or word[:i] in self.nonStandardWords) and (self.spell[word[i:]] 
                or word[i:] in self.nonStandardWords):
                try:
                    potential_matches.append(word[:i] + ' - ' + word[i:])
                except:
                    print('Error in mySpellChecker.word_splitter')
                    print(word, i)
        return potential_matches
    
    
    def add_replacement(self, word, replacement):
        add_list = [(word, replacement)] if word == word.capitalize() \
            else [(word, replacement), (word.capitalize(), replacement.capitalize())]
        for w, r in add_list:
            self.replacementDict[w] = r
        return r
    
    
    def check_word_spelling(self, word):
        """
        y = real word, add to dict
        n = not a real word, suggest replacements
        - = conjoined word
        s = skip
        """
        
        #Split words with ellipses within them
        num = word.count('...')        
        if num > 0:
            j = 0
            for _ in range(num):
                index = word[j:].find('...') + j
                if index > -1:
                    word = word[:index+3] + ' ' + word[index+3:]
                j = index + 3
            return word
        
        # Replace known errors
        if word in self.replacementDict.keys():
            return self.replacementDict[word]
        
        if not self.spell[word] and word not in self.nonStandardWords and '.' in word:
            replacement = self.spell.correction(word)
            keyword = input(word + '\ny/n/-/s (' + replacement + '): ')
            
            # Is the word actually correct?
            if keyword == 'y':
                add_list = [word] if word == word.capitalize() else [word, word.capitalize()]
                if any(x in word for x in "'1234567890,%"):
                    self.nonStandardWords.extend(add_list)
                else:
                    for w in add_list:
                        self.spell.word_frequency.add(w)
                        self.infile.write(w + '\n')
                        
            # Should the word by split by a hyphen?
            elif keyword == '-':
                potential_matches = self.word_splitter(word)
                
                # No options available, spell manually
                if len(potential_matches) == 0:
                    replacement = input('Correct spelling: ')
                    word = self.add_replacement(word, replacement)
                    
                # One option, approve or spell manually
                elif len(potential_matches) == 1:
                    replacement = potential_matches[0]
                    if input('Replacement: ' + replacement + '\ny/n: ') != 'y':
                        replacement = input('Correct spelling: ')
                    word = self.add_replacement(word, replacement)
                    
                # More than one option, choose one or spell manually
                else:
                    for i, potential_match in enumerate(potential_matches):
                        print(i, potential_match)
                    choice = input("0 - {} or n: ".format(i))
                    if choice == 'n':
                        replacement = input('Correct spelling: ')
                        word = self.add_replacement(word, replacement)
                    else:
                        replacement = potential_matches[int(choice)]
                        word = self.add_replacement(word, replacement)                    
            
            # Does the word need to be manually spelled?
            elif keyword == 'n':
                if input('Replacement: ' + replacement + '\ny/n: ') != 'y':
                    replacement = input('Correct spelling: ')
                word = self.add_replacement(word, replacement)
                
            # end program
            elif keyword == 'q':
                pass
        return word
    
    def fixCommonErrors(self, text):
        """ Expects 'text' to be list
        """
        re_mask = r"(\d{1,3}?)([,]?\d{3})*(((\.\d+)%?)|%|st|nd|rd|th)?"
        errorFound = False
        #print(self.censoredDict.items())
        for i, line in enumerate(text):
            print(line)
            if line == '' and len(text) != 1:
                errorFound = True
            for word, replacement in self.censoredDict.items():
                line = re.sub(word, replacement, line)
            text[i] = line

            line = line.split()
            for j, main_word in enumerate(line):
                subword_list = []
                onlyPunctuation = False
                for word in main_word.split('-'):                    
                        
                    punctuation = '.,()?!" :;\'~'
                    l_punc = ''
                    r_punc = ''
                    
                    # Remove and store punctuation from left of word
                    while word:
                        if word[0] in punctuation:
                            l_punc = l_punc + word[0]
                            word = word[1:]
                        else:
                            break
            
                    # Remove and store punctuation from right of word                
                    while word:
                        if word[-1] in punctuation:
                            r_punc = word[-1] + r_punc
                            word = word[:-1]
                        else:
                            break
                    
                    if not word:
                        onlyPunctuation = True
                        
                    # Remove 's
                    if word[-2:] == "'s":
                        r_punc = word[-2:] + r_punc
                        word = word[:-2]
                        
                    if re.fullmatch(re_mask, word) or onlyPunctuation:
                        pass # Don't check spelling of numbers or punctuation
                    else:
                        word = self.check_word_spelling(word)
                    
                    # Add punctuation back to word and put in sub-word list
                    subword_list.append(l_punc + word + r_punc)
                    
                line[j] = '-'.join(subword_list)
            
            text[i] = ' '.join(line)
        if errorFound:
            raise ValueError("empty text")
        return text