import json
import re

class Translator():
    def __init__(self, config):
        self.map = json.load(open(config['translate']['map']))

    def _translate(self, my):
        match_myanmar = re.match(r'(.*)\((.*)\)(.*)', my)

        if match_myanmar:
            state_my = match_myanmar[1]
            people_my = match_myanmar[2]
            id_my = match_myanmar[3]
            
            state_en = self.map['state'].get(state_my, '')
            people_en = self.map['people'].get(people_my, '')
            
            ids_en = []
            for id_char in id_my:
                id_en = self.map['id'].get(id_char, '')
                ids_en.append(id_en)
            
            ids_en = ''.join(ids_en)

            en = '{}({}){}'.format(state_en, people_en, ids_en)

            return en

    def translate(self, layout):
        for d in layout:
            value = d['value']
            if 'id' in value:
                id_my = value['id']

                id_en = self._translate(id_my)
                value['id_en'] = id_en

        return layout

