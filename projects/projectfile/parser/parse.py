import re

from projects.projectfile import error
from projects.projectfile.utils import get_current_command


def parse_version(line):
    m = re.match('^from\s+v?(\d+)\.(\d+)\.(\d+)\s*$', line)
    if m:
        return int(m.group(1)), int(m.group(2)), int(m.group(3))
    else:
        if re.match('^\s+from.*$', line):
            raise SyntaxError(error.VERSION_INDENTATION_ERROR)
        elif re.match('^from.*$', line) and not re.match('^from\s+v?(\d+)\.(\d+)\.(\d+)\s*$', line):
            raise SyntaxError(error.VERSION_FORMAT_ERROR)
        else:
            return None


def parse_line(line):
    m = re.match('^(.*)$', line)
    if m:
        return m.group(1).strip()
    else:
        return None


def parse_empty_line(line):
    if re.match('^\s*$', line):
        return True
    else:
        return False


def parse_indented_line(line):
    m = re.match('^\s+(.*)$', line)
    if m:
        return m.group(1).strip()
    else:
        return None


def parse_comment_delimiter(line):
    if re.match('\s*""".*$', line):
        return True
    else:
        return False


def parse_variable(line):
    m = re.match('^([\w\.-]+)\s*=\s*(.*)$', line)
    if m:
        value = m.group(2).strip()
        temp_value = value
        if value.startswith('"') or value.startswith("'"):
            if value.endswith('"') or value.endswith("'"):
                temp_value = value[1:]
            else:
                raise SyntaxError(error.VARIABLE_QUOTE_AFTER_ERROR)
        if value.endswith('"') or value.endswith("'"):
            if value.startswith('"') or value.startswith("'"):
                value = temp_value[:-1]
            else:
                raise SyntaxError(error.VARIABLE_QUOTE_BEFORE_ERROR)
        value = value.replace('\\"', '"')
        value = value.replace("\\'", "'")
        return {m.group(1): value}
    else:
        if re.match('^\s+[\w\.-]+\s*=\s*.*$', line):
            raise SyntaxError(error.VARIABLE_INDENTATION_ERROR)
        return None


def parse_command_divisor(line):
    if re.match('\s*===.*$', line):
        return True
    else:
        return False


def parse_command_header(line):
    if re.match('^\s+.*:.*', line):
        raise SyntaxError(error.COMMAND_HEADER_INDENTATION_ERROR)
    m = re.match('^([\w\|\.\s-]+):\s*(?:\[([\w\.\s,-]+)\])?\s*$', line)
    if m:
        keys = m.group(1).split('|')
        keys = [k.strip() for k in keys]
        for key in keys:
            if not key:
                raise SyntaxError(error.COMMAND_HEADER_INVALID_ALTERNATIVE)
        if m.group(2):
            deps = m.group(2).split(',')
            deps = [d.strip() for d in deps]
            for dep in deps:
                if not dep:
                    raise SyntaxError(error.COMMAND_HEADER_INVALID_DEPENDENCY_LIST)
        else:
            deps = []

        ret = {keys[0]: {'done': False}}
        if deps:
            ret[keys[0]]['dependencies'] = deps
        if len(keys) > 1:
            for key in keys[1:]:
                ret[key] = {'alias': keys[0]}
        return ret
    else:
        if not re.match('^\s+.*', line) and not re.search(':', line):
            raise SyntaxError(error.COMMAND_HEADER_MISSING_COLON_ERROR)
        if not re.match('^\s+.*', line) and re.search('(\w:\w|^:)', line):
            raise SyntaxError(error.COMMAND_HEADER_COLON_ERROR)
        if re.search('\[\]', line):
            raise SyntaxError(error.COMMAND_HEADER_EMPTY_DEPENDENCY_LIST)
        if re.search('[\[\]]', line):
            if not re.search('\[[^\[\]]*\]', line) or re.search('\[(\s*,\s*|[^,]*,\s*,[^,]*)\]', line):
                raise SyntaxError(error.COMMAND_HEADER_INVALID_DEPENDENCY_LIST)
        raise SyntaxError(error.COMMAND_HEADER_SYNTAX_ERROR)






