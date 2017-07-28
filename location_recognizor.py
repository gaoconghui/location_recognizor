# -*- coding: utf-8 -*-
from collections import Counter
from optparse import OptionParser
import logging

logger = logging.getLogger(__name__)

class TrieTree(object):
    def __init__(self):
        self.tree = {}

    def add(self, item, key_getter=lambda x: x):
        word = key_getter(item)
        tree = self.tree
        for char in word:
            if char in tree:
                tree = tree[char]
            else:
                tree[char] = {}
                tree = tree[char]

        tree['exist'] = True

    def search(self, item, key_getter=lambda x: x):
        word = key_getter(item)
        tree = self.tree
        for char in word:
            if char in tree:
                tree = tree[char]
            else:
                return False

        if "exist" in tree and tree["exist"] == True:
            return True
        else:
            return False

    def split_str(self, item, key_getter=lambda x: x):
        """
        按字符按树中能匹配到的最长字符串分割字符
        :param item:
        :param key_getter:
        :return:
        """
        word = key_getter(item)
        result = set()
        tree = self.tree
        sub_word = ""
        i = 0
        while i < len(word):
            char = word[i]
            if char in tree:
                sub_word += char
                tree = tree[char]
                i += 1
            else:
                if sub_word == "":
                    result.add(char)
                    i += 1
                else:
                    result.add(sub_word)
                    sub_word = ""
                tree = self.tree
        result.add(sub_word)
        return result


class LocationRecognizer():
    """
    保存地点信息，每个地点信息都是一个dict，有以下字段
    {
        "code" : 地点code,
        "name" : 地点名字，为搜索的key，
        "type" : province city or area，
        "belong" : 另一个地点信息，dict ，可以不填
    }
    """

    def __init__(self,path):
        self.searcher = TrieTree()
        self.locations_code = {}
        self.locations_name = {}
        self.__load_location(path)

    def __load_location(self,path):
        with open(path) as f:
            items = f.readlines()
            for item in items:
                subs = item.replace("\n", "").split(",")
                m = {
                    "code": subs[0],
                    "name": subs[1],
                    "type": subs[2]
                }
                if len(subs) == 4:
                    m['belong'] = self.locations_code[subs[3]]
                self.__add(m)

    def __add(self, location):
        self.locations_code[location.get("code")] = location
        self.locations_name[location.get("name")] = location
        self.searcher.add(location.get("name"))

    def __search_location(self, s):
        s_split = self.searcher.split_str(s)
        items = [self.locations_name.get(key) for key in s_split if key in self.locations_name]
        for item in items:
            tmp = item
            while tmp.get("belong"):
                tmp = self.locations_code.get(tmp.get("belong").get("code"))
                items.append(tmp)
        return items

    def identify_location(self, s):
        if isinstance(s, unicode):
            s = s.encode('utf-8')
        result = {}
        if not s:
            return result
        try:
            items = self.__search_location(s)
            c = Counter([i.get("code") for i in items]).most_common()
            for code, _ in c:
                item = self.locations_code.get(code)
                t = item.get("type")
                if t not in result:
                    result[t] = item.get('name').decode('utf-8')
            logger.debug('in location recognizor, source : %s, source type : %s, result : %s' % (s, type(s), result))
        except Exception, e:
            logger.error('failed to process location : %s, error : %s' % (s, e))
        return result

def main(text):
    l = LocationRecognizer("location.dat")
    for k, v in l.identify_location(text).items():
        print '%s : %s' % (k, v)

if __name__ == '__main__':
    l = LocationRecognizer("location.dat")
    parser = OptionParser()
    parser.add_option('-t', '--text', dest='text',
                      default='浙江 杭州',
                      help='location text')
    (options, args) = parser.parse_args()
    main(options.text)
