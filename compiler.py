import re
from itertools import groupby

states = {
    0 : 'start',
    15: 'ID',
    16: 'NUM',
    17: 'SYMBOL',
    7: 'SYMBOL',
    18: 'SYMBOL',
    6: 'SYMBOL',
    22: 'SYMBOL',
    21: 'comment', 
    20: 'comment', 
    19: 'whitespace',
    20: 'open_comment'
}
special_states = {
    7: 'SYMBOL'
}
keywords = ["if", "else", "void", "int", "repeat", "break", "until", "return"]
symbol = [";", ":", ",", "[", "]", "(", ")", "{", "}", "+", "-", "<"]
whitespace = [" ", "\n", "\t", "\r", "\f", "\v"]


def lookahead_state(state: int, char: str):
    print(char, state)
    position = "next_state or error type"
    error = False
    end = False

    if (state == 0): # start
        # keyword an id
        if (re.match('[a-zA-Z]', char)):
            position = 1
        # num
        elif (re.match('[0-9]', char)):
            position = 3
        elif (char == '*'):
            position = 2
        # =
        elif (char == '='):
            position = 4
        # =
        elif (char == ';'):
            position = 22
            end = True
        # symbol exept for = and ;
        elif (char in symbol):
            position = 7
        # comment
        elif (char == '/'):
            position = 8
        # whitespace
        elif (char in whitespace):
            position = 14
        else:
            error = True
            position = "Invalid input"
    # id
    elif (state == 1):
        if (re.match('[a-zA-Z0-9]', char)):
            position = 1
        elif (char in whitespace + symbol + ["=", "*", "/"]):
            position = 15
            end = True
        else:
            error = True
            position = "Invalid input"
    # * has been seen
    elif (state == 2):
        if (char == '/'):
            error = True
            position = "Unmatched comment"
        elif char in whitespace + ["=", "*", "/"] + symbol or re.match('[a-zA-Z0-9]', char):
            position = 18
            end = True
        else:
            error = True
            position = "Invalid input"

    # num
    elif (state == 3):
        if (re.match('[0-9]', char)):
            position = 3
        elif (char in whitespace + symbol + ["=", "*", "/"]):
            position = 16
            end = True
        else:
            position = "Invalid number"
            error = True
    # =
    elif (state == 4):
        if (char == '='):
            position = 5
        elif (char in whitespace + symbol + ["*", "/"] or re.match('[a-zA-Z0-9]', char)):
            position = 6
            end = True
        else:
            error = True
            position = "Invalid input"
    # ==
    elif (state == 5):
        if (char in whitespace + symbol + ["=", "*", "/"] or re.match('[a-zA-Z0-9]', char)):
            position = 17
            end = True
        else:
            error = True
            position = "Invalid input"
    # symbol
    elif (state == 7):
        if char in whitespace + ["=", "*", "/"] + symbol or re.match('[a-zA-Z0-9]', char):
            position = 18
            end = True
        else:
            end = True
    # when first / has been seen
    elif (state == 8):
        if (char == '*'):
            position = 9
        # elif (char == '/'):
        #     position = 12
        else:
            position = "Invalid input"
            error = True
    # /* has been seen
    elif (state == 9):
        if (not char == '*'):
            position = 9 # todo
        elif (char == '*'):
            position = 10
        else:
            position = "Unclosed comment"
            error = True
    # /* ... * has been seen
    elif (state == 10):
        if (char == '/'):
            position = 11
        else:
            position = 9

    elif (state == 11):
        if (char in whitespace + symbol + ["=", "*", "/"] or re.match('[a-zA-Z0-9]', char)):
            position = 21
            end = True
        else:
            position = "Invalid input"
            error = True
    elif (state == 12):
        if (not char == "\n"):
            position = 12
        else:
            position = 13
    elif (state == 13):
        if (char in whitespace + symbol + ["=", "*", "/"] or re.match('[a-zA-Z0-9]', char)):
            position = 20
            end = True
        else:
            position = "Invalid input"
            error = True
    elif (state == 14):
        if (char in whitespace + symbol + ["=", "*", "/"] or re.match('[a-zA-Z0-9]', char)):
            position = 19
            end = True
        else:
            position = "Invalid input"
            error = True

    if (position == "next_state or error type"):
        position = state

    print(f'lookahead_state: error={error} , position={position} , end={end}')
    return error, position, end


class Scanner:
    def __init__(self):
        self.line_number = 1
        self.current_state = 0
        self.string = ''
        self.errors = []
        self.tokens = []

    def next(self, character, count=True):

        error, position, end = lookahead_state(self.current_state, character)

        if error:
            # # adding last token
            # last_token = ''
            # if self.current_state in special_states:
            #     if position == 'Invalid input':
            #         self.tokens.append(
            #             (self.line_number, {'type': special_states[self.current_state], 'string': self.string}))
            #         last_token = self.string
            #         print(self.tokens[-1])
            
            string, self.string = self.string.strip(), ''
            self.current_state = 0
            self.errors.append(
                (self.line_number, {'string': string + character, 'message': position}))
            if character == '\n':
                self.errors.pop(-1)
                self.errors.append(
                    (self.line_number, {'string': string, 'message': position}))

            if string == '/' and (re.match('[a-zA-Z0-9]', character) or character == '/' or character in symbol):
                self.errors.pop(-1)
                self.errors.append(
                    (self.line_number, {'string': string, 'message': position}))
                self.next(character, count=False)
                
            if character == '\n' and count:
                self.line_number += 1

            return

        if end:

            if self.string:
                string, self.string = self.string.strip(), ''
                self.current_state = 0
                if states[position] in {'ID', 'SYMBOL', 'NUM'}:
                    type_ = 'KEYWORD' if states[position] == 'ID' and string in keywords else states[position]
                    self.tokens.append(
                        (self.line_number, {'type': type_, 'string': string}))
                    print(self.tokens[-1])

                self.next(character, count=False)

                if character == '\n' and count:
                    self.line_number += 1
            elif not self.string and character == ';':
                self.tokens.append(
                    (self.line_number, {'type': 'SYMBOL', 'string': character}))
                print(self.tokens[-1])
            return

        self.string += character
        self.current_state = position

        if character == '\n' and count:
            self.line_number += 1

    def finish(self):
        if self.current_state in {9, 10, 11}:
            err = self.string[:-1][:7] + ('...' if len(self.string[:-1]) > 7 else '')
            self.errors.append(
                (self.line_number - self.string.count('\n'), {'string': err, 'message': 'Unclosed comment'}))

scanner = Scanner()

base_dir = ''
input_dir = ''

# base_dir = 'code/'
# input_dir = 'testcases/T09/'


input_file = base_dir + input_dir + 'input.txt'
lexical_error_file = base_dir + 'lexical_errors.txt'
tokens_file = base_dir + 'tokens.txt'
symbol_table_file = base_dir + 'symbol_table.txt'


with open(input_file, 'r') as f:
    while True:
        character = f.read(1)

        if not character:
            break

        scanner.next(character)

scanner.next('\n')
scanner.finish()

with open(lexical_error_file, 'w') as f:
    if scanner.errors:
        for line, val in groupby(scanner.errors, key=lambda x: x[0]):
            f.write('{}.\t'.format(line))
            f.write(' '.join(['({}, {})'.format(x['string'], x['message']) for _, x in val]) + '\n')
    else:
        f.write('There is no lexical error.')

with open(tokens_file, 'w') as f:
    for line, val in groupby(scanner.tokens, key=lambda x: x[0]):
        f.write('{}.\t'.format(line))
        f.write(' '.join(['({}, {})'.format(x['type'], x['string']) for _, x in val]) + '\n')


with open(symbol_table_file, 'w') as f:
    ids = [x[1]['string'] for x in scanner.tokens if x[1]['type'] == 'ID']
    for i, name in enumerate(keywords):
        f.write('{}.\t{}'.format(i + 1, name) + '\n')

    set_ids = set()
    for identifier in ids:
        if identifier in set_ids:
            continue

        set_ids.add(identifier)
        f.write('{}.\t{}'.format(len(keywords) + len(set_ids), identifier) + '\n')

