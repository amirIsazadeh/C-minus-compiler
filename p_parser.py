from grammer import *
from anytree import Node, RenderTree
from scanner import Scanner
token = None
raw_token = None
old_token = None


class Parser:
    def __init__(self):
        self.rules = build_rules()
        self.scanner = Scanner()
        self.token_counter = 0
        self.syntax_errors = []
        base_dir = ''
        input_dir = ''
        input_file = base_dir + input_dir + 'input.txt'
        with open(input_file, 'r') as f:
            while True:
                character = f.read(1)

                if not character:
                    break

                self.scanner.next(character)

        self.scanner.next('\n')
        self.scanner.finish()
        self.scanner.tokens.append((0, {'type': 'FINISH', 'string': '$'}))

    def get_next_tonken(self):
        self.token_counter += 1
        token = self.scanner.tokens[self.token_counter - 1]
        old_token = token
        token = (token[1]['type'], token[1]['string'])
        if token[0] in terminals or token[0] in non_terminals:
            new_token = token[0]
        else:
            new_token = token[1]
        return new_token, token, old_token

    def find_rule_by_name(self, name):
        for rule in self.rules:
            if rule.name == name:
                return rule
        return None
    
    def find_proper_edge(self, rule : Tree, cur_node, token):
        edges = rule.get_edges_by_start_node(cur_node)
        if len(edges) == 1:
            return edges[0]
        for edge in edges:
            val = edge[0]
            if val in terminals and val == token:
                return edge
            if val in non_terminals and token in firsts[val]:
                return edge
            if val == 'EPSILON' and token in follows[rule.name]:
                return edge
            if val in non_terminals and 'EPSILON' in firsts[val] and token in follows[val]:
                return edge
        return None
    
    def start_parse(self):
        global token, raw_token, old_token
        tree_node = Node('Program')
        token, raw_token, old_token = self.get_next_tonken()
        try:
            self.parse(self.find_rule_by_name('Program'), 0, tree_node)
        except:
            pass
        self.print_tree(tree_node)
        self.print_syntax_errors()

    def parse(self, rule : Tree, cur_node, tree_node):
        global token, raw_token, old_token
        while True:
            if cur_node == rule.accept_state:
                return
            edge = self.find_proper_edge(rule, cur_node, token)
            if edge == None:  # panic mode
                if cur_node == 0:  # error 1, 2 --- non-terminal
                    if token not in follows[rule.name]: # error 1 --- non-terminal, not in follow
                        if token == '$':  # error 4, EOF
                            self.syntax_errors.append(
                                f"#{old_token[0]} : syntax error, Unexpected EOF")
                            raise Exception()
                        else:
                            self.syntax_errors.append(
                                f"#{old_token[0]} : syntax error, illegal {token}")
                            token, raw_token, old_token = self.get_next_tonken()
                            if token == '$':
                                return
                            continue
                    else:  # error 2 --- non-terminal, in follow
                        self.syntax_errors.append(
                            f"#{old_token[0]} : syntax error, missing {rule.name}")
                        return
            
            val = edge[0]
            end_node = edge[2]
            
            if val in terminals and val != token:  # error 3, 4
                if token == '$':  # error 4, EOF
                    self.syntax_errors.append(
                        f"#{old_token[0]} : syntax error, Unexpected EOF")
                    raise Exception()
                else:  # error 3 --- terminal, not equal
                    self.syntax_errors.append(
                        f"#{old_token[0]} : syntax error, missing {val}")
                    cur_node = end_node
                    continue
            if val in non_terminals:
                new_rule = self.find_rule_by_name(val)
                new_tree_node = Node(val, parent=tree_node)
                self.parse(new_rule, new_rule.nodes[0], new_tree_node)
            elif val in terminals:
                if token == '$':
                    raw_token_text = '$'
                else:
                    raw_token_text = f'({raw_token[0]}, {raw_token[1]})'
                Node(raw_token_text, parent=tree_node)

                token, raw_token, old_token = self.get_next_tonken()
                if token == '$':
                    return
            elif val == 'EPSILON':
                Node('epsilon', parent=tree_node)
            if end_node == rule.accept_state:
                return
            cur_node = end_node

    def clean_tree(self, curr_node: Node):
        if len(curr_node.children) == 0 and curr_node.name[-1] != ')' and curr_node.name != 'epsilon' and curr_node.name[-1] != '$':
            curr_node.parent = None
        for node in curr_node.children:
            self.clean_tree(node)
        if len(curr_node.children) == 0 and curr_node.name[-1] != ')' and curr_node.name != 'epsilon' and curr_node.name[-1] != '$':
            curr_node.parent = None
    
    def print_tree(self, tree_node):
        self.clean_tree(tree_node)
        text = ""
        lines = []
        for pre, fill, node in RenderTree(tree_node):
            line = ""
            line += pre
            line += node.name
            line += '\n'
            lines.append(line)
            
        text = "".join(lines)
        text = text[:-1]
        with open("parse_tree.txt", "w", encoding="utf-8") as f:
            f.write(text)
    
    def print_syntax_errors(self):
        if len(self.syntax_errors) == 0:
            text = "There is no syntax error."
        else:
            text = '\n'.join(self.syntax_errors)
            text += '\n'
        with open("syntax_errors.txt", "w", encoding="utf-8") as f:
            f.write(text)
