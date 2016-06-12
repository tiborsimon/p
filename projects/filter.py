import re


def _get_pattern_list(keys):
    ret = []
    template = '({0})'
    for i in reversed(range(1, len(keys)+1)):
        temp = ['']
        for j in range(len(keys)):
            if j < i:
                temp[0] += keys[j]
            else:
                temp.append(keys[j])
        for k in range(len(temp)):
            temp[k] = '({})'.format(temp[k])
        ret.append(''.join(temp))
    return ret


def weight_string_for_item(item):
    buffer = list('0'*len(item['string']))
    for s in item['selection']:
        for i in range(s[0], s[1]):
            buffer[i] = '1'
    return ''.join(buffer)


def generate_weight(weight_string):
    if '1' not in weight_string:
        return 0


def weight_item(item):
    weight_string = weight_string_for_item(item)
    item['weight'] = int(weight_string, 2)/len(item['string'])


def sort_structure(data):
    for item in data:
        weight_item(item)
    data.sort(key=lambda k: k['string'])
    data.sort(key=lambda k: k['weight'], reverse=True)
    for item in data:
        del item['weight']
    return data


def merge_neighbour_selections(data):
    for node in data:
        merged = []
        last = ()
        if len(node['selection']) < 2:
            continue
        for s in node['selection']:
            if last:
                if last[1] == s[0]:
                    new_s = (last[0], s[1])
                    if merged:
                        merged.pop()
                    merged.append(new_s)
                    last = new_s
                else:
                    if not merged:
                        merged.append(last)
                    elif merged[-1] != last:
                        merged.append(last)
                    merged.append(s)
                    last = s
            else:
                last = s
        node['selection'] = tuple(merged)


def generate_data_structure_for_search_string(patterns, search_string):
    ret = []
    for line in search_string:
        for pattern in patterns:
            p = re.compile(pattern)
            selections = []
            for m in p.finditer(line):
                selections.extend(m.regs[1:])
            if selections:
                ret.append({
                    'string': line,
                    'selection': tuple(selections)
                })
                break
        else:
            ret.append({
                'string': line,
                'selection': ()
            })
    merge_neighbour_selections(ret)
    return ret


def transform_data(data):
    ret = []
    for item in data:
        node = []
        if item['selection']:
            index = 0
            line = item['string']
            for s in item['selection']:
                if s[0] == 0:
                    node.append({
                        'string': line[:s[1]],
                        'highlight': True
                    })
                else:
                    node.append({
                        'string': line[index-index:s[0]-index],
                        'highlight': False
                    })
                    node.append({
                        'string': line[s[0]-index:s[1]-index],
                        'highlight': True
                    })
                line = line[s[1]-index:]
                index = s[1]

            else:
                if line:
                    node.append({
                        'string': line,
                        'highlight': False
                    })
        else:
            node.append({
                'string': item['string'],
                'highlight': False
            })
        ret.append(node)
    return ret


def filter_data(keys, data):
    pattern = _get_pattern_list(keys)
    data = generate_data_structure_for_search_string(pattern, data)
    sorted_data = sort_structure(data)
    final_data = transform_data(sorted_data)
    return final_data


class Filter(object):
    def __init__(self, data):
        self.data = data
        self.keys = ''

    def add_key(self, key):
        self.keys += key

    def remove_key(self):
        if len(self.keys) == 0:
            pass
        elif len(self.keys) == 1:
            self.keys = ''
        else:
            self.keys = self.keys[:-1]

    def filter(self):
        return filter_data(self.keys, self.data)



