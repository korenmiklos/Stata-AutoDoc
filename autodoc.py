import yaml
import re
import sys
import os
import glob

NODE_REGEX = """(?P<node>[.\w_"`'/]*)"""
NAME_REGEX = """(?P<node>[\w\s]*)"""

SINGLE_LINE_COMMENT = re.compile("^\s*\*(?P<comment>.*)")
INLINE_COMMENT = re.compile("^(?P<line1>.*)/\*(?P<comment>.*)\*/(?P<line2>.*)$")
MULTILINE_COMMENT_BEGIN = re.compile("^(?P<line>.*)/\*(?P<comment>.*)")
MULTILINE_COMMENT_END = re.compile("^(?P<comment>.*)\*/(?P<line>.*)$")

REGEXES = (
    (re.compile("^\s*tempfile\s+"+NAME_REGEX+".*"), 'tempfile'),
    (re.compile("^\s*use\s+"+NODE_REGEX+".*"), 'data_input'),
    (re.compile("^.*(merge|csvmerge|append|insheet|infile|cross|join).*\s+using\s+"+NODE_REGEX+".*"), 'data_input'),
    (re.compile("^\s*(do|run)\s+"+NODE_REGEX+".*"), 'script_input'),
    (re.compile("^\s*(save|saveold)\s+"+NODE_REGEX+".*"), 'data_output'),
    (re.compile("^.*(outsheet|outfile).*\s+using\s+"+NODE_REGEX+".*"), 'data_output'),
    (re.compile("^.*(log|outreg).*\s+using\s+"+NODE_REGEX+".*"), 'text_output'),
    (re.compile("^.*graph\s+export\s+"+NODE_REGEX+".*"), 'graph_output'),
    )

FIELDS = {
    'docstring': 'Purpose of this file',
    'data_input': 'Requires data',
    'script_input': 'Requires script',
    'data_output': 'Creates data',
    'text_output': 'Creates text',
    'graph_output': 'Creates graph',
    'tempfile': 'Temporary files',
    'comment': 'Comments',
    }
    
NODE_TYPES = {
    'script': { 'extension': 'do',
                'color': '#99B3CC'},
    'data': { 'extension': 'dta',
                'color': '#FFFFFF'},
    'graph': { 'extension': 'png',
                'color': '#CC99B3'},
    'text': { 'extension': 'txt',
                'color': '#71B7B7'},
}

def normalize(name):
    # strip whitespace and "s
    name = ''.join(name.strip().split('"'))
    return os.path.normpath(name)   

class Node(object):
    def __init__(self,filename,node_type,graph):
        path, name = os.path.split(normalize(filename))
        self.filename = name
        self.path = path
        self.node_type = node_type
        # each field starst with an emtpy list
        self.attributes = dict([(key, []) for key in FIELDS.keys()])
        self.ignore = False
        self.graph = graph
        # add node to its graph if not there yet
        self.graph.add_node(self)

    def add_tempfile(self,text):
        if not text in self.attributes['tempfile']:
            self.attributes['tempfile'].append(text)

    def is_tempfile(self,text):
        return text in self.attributes['tempfile']

    def add_attribute(self,text,categ):
        if categ=="tempfile":
            for name in text.split():
                # multiple tempfile names may be separated by space
                self.add_tempfile("`"+name+"'")
        elif not text in self.attributes[categ]:
            node_type = categ.split('_')[0] # e.g., data
            if node_type in NODE_TYPES.keys():
                # only do node processing for know node types
                node_direction = categ.split('_')[1] # e.g., output
                if node_direction in ('input', 'output'):
                    # preprocessing of node
                    name = normalize(os.path.join(self.path,text.strip()))
                    # name is relative to current path
                    if self.graph.has_name(name):
                        newnode = self.graph.get_node(name)
                    else:                    
                        newnode = Node(name,node_type,self.graph)
                    if node_direction in ('input', ):
                        # dependence may be encoded in an option
                        self.graph.depends_on(newnode,self)
                    else:
                        self.graph.depends_on(self,newnode)
            self.attributes[categ].append(text.strip())

    def get_canonical_name(self):
        return os.path.join(self.path,self.filename)
        
    def open_for_reading(self):
        return open(os.path.join(self.path,self.filename),"r")
        
    def get_yaml(self):
        # change to verbose name
        dct = {}
        for key, value in self.attributes.iteritems():
            dct[FIELDS[key]] = value
        # add a docstring
        if self.attributes['comment']:
            dct[FIELDS['docstring']] = self.attributes['comment'][0]
            del dct[FIELDS['comment']][0]
        return yaml.dump(dct,default_flow_style=False)

        
class Graph(object):
    def __init__(self):
        self.nodes = {}
        self.edges = []

    def has_name(self,text):
        return text in self.nodes.keys()

    def has_node(self,node):
        return self.has_name(node.get_canonical_name())

    def add_node(self,node):
        if not self.has_node(node):
            self.nodes[node.get_canonical_name()] = node

    def get_node(self,name):
        if self.has_name(name):
            return self.nodes[name]

    def depends_on(self,A,B):
        self.add_node(A)
        self.add_node(B)
        edge = (A.get_canonical_name(), B.get_canonical_name())
        if not edge in self.edges:
            self.edges.append(edge)

    def get_blockdiag(self):
        ''' A blockdiag representation of dependencies.'''
        index = 0
        dct = {}
        text = ""
        # list nodes
        for name in self.nodes.keys():
            dct[name] = index
            color = NODE_TYPES[self.get_node(name).node_type]['color']
            # format should depend on node attributes
            text += 'NODE%d [label="%s", color="%s"];\n' % (index,name,color)
            index += 1
        for edge in self.edges:
            A = dct[edge[0]]
            B = dct[edge[1]]
            text += 'NODE%d -> NODE%d;\n' % (A,B)
        return text

    
class DoFile(Node):
    def __init__(self,fname,graph):
        super(DoFile,self).__init__(fname,'script',graph)
    
    def extract_inputs_and_outputs(self):
        for line in self.open_for_reading():
            if self.ignore:
                # when in comment mode, ignore all other patterns
                if MULTILINE_COMMENT_END.match(line):
                    m = MULTILINE_COMMENT_END.match(line)
                    # pass end of line on to further processing
                    line = m.groupdict()['line']
                    # add last line of comment
                    comment +=  m.groupdict()['comment']
                    self.add_attribute(comment,'comment')
                    self.ignore = False
                else:
                    # if no match, keep adding to comment
                    comment += line 
            else:
                # check comments first
                if SINGLE_LINE_COMMENT.match(line):
                    comment = SINGLE_LINE_COMMENT.match(line).groupdict()['comment']
                    self.add_attribute(comment,'comment')
                elif INLINE_COMMENT.match(line):
                    m = INLINE_COMMENT.match(line).groupdict()
                    comment = m['comment']
                    self.add_attribute(comment,'comment')
                    line = m['line1'] + ' ' + m['line2']
                elif MULTILINE_COMMENT_BEGIN.match(line):
                    m = MULTILINE_COMMENT_BEGIN.match(line)
                    # pass beginning of line on to further processing
                    line = m.groupdict()['line']
                    comment = m.groupdict()['comment'] 
                    self.ignore = True
                for rgx, categ in REGEXES:
                    if rgx.match(line):
                        m = rgx.match(line)
                        node = m.groupdict()['node']
                        if not self.is_tempfile(node):
                            # only add if not a temporary file
                            self.add_attribute(node,categ)
            

class DataFile(Node):
    pass
    
    
if __name__=="__main__":

    # creare an empty graph
    graph = Graph()
    try:
        path = sys.argv[1]
    except:
        path = './'
    for infile in glob.glob( os.path.join(path, '*.do') ):
        print "Current file is: " + infile
        dofile = DoFile(infile,graph)
        dofile.extract_inputs_and_outputs()
        print dofile.get_yaml()
    print graph.get_blockdiag()
