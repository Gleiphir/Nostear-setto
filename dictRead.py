import json
from collections import Set,OrderedDict

class Dict:
    def __init__(self,fileName):
        try:
            with open(fileName,encoding='utf-8') as F:
                self.ori = json.load(F)
            self._comment = self.ori['comment']
            self._author = self.ori['author']
            self.data = self.ori['data']

            self.dict = {} # dict: key => dict
            for word in self.data:
                if word['k'].lower() in self.dict:
                    self.dict[word['k'].lower()][word['w']] = word['m']
                else:
                    self.dict[word['k'].lower()] = {}
                    self.dict[word['k'].lower()][word['w']] = word['m']
            print(self.dict)
        except IOError as e:
            print('File not Found')
        except KeyError as ke:
            print("File not valid")

    def author(self):
        return self._author

    def comment(self):
        return self._comment

    def ListKey(self, key:str):
        if not key in self.dict:return []
        return self.dict[key]

    def Meaning4name(self,name:str): # assume valid
        for key in self.dict:
            for N in self.dict[key]:
                if N == name:
                    return self.dict[key][name]