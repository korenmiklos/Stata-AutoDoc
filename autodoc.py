import yaml
import re
import sys

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
    (re.compile("^.*(outsheet|outfile|log).*\s+using\s+"+NODE_REGEX+".*"), 'data_output'),
    )

FIELDS = {
    'data_input': 'Data inputs',
    'script_input': 'Script inputs',
    'data_output': 'Data outputs',
    'tempfile': 'Temporary files',
    'comment': 'Comments',
    }

class Node(object):
    def __init__(self,filename):
        self.filename = filename
        # each field starst with an emtpy list
        self.attributes = dict([(key, []) for key in FIELDS.keys()])
        self.ignore = False

    @property
    def data_inputs(self):
        return self.attributes['data_input']

    @property
    def data_outputs(self):
        return self.attributes['data_output']
        
    @property
    def script_inputs(self):
        return self.attributes['script_input']
        
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
            self.attributes[categ].append(text.strip())

    def get_absolute_path(self):
        pass 
    def get_canonical_name(self):
        return self.filename
        
    def open_for_reading(self):
        return open(self.filename,"r")
        
    def get_yaml(self):
        # change to verbose name
        dct = {}
        for key, value in self.attributes.iteritems():
            dct[FIELDS[key]] = value
        return yaml.dump(dct,default_flow_style=False)

    def get_blockdiag(self):
        ''' A blockdiag representation of dependencies.'''
        nodes = []
        text = 'NODE0 [label="%s"];\n' % self.get_canonical_name()
        index = 1
        for line in self.data_inputs:
            text += 'NODE%d [label="%s", color="#888888"];\n' % (index,line)
            text += 'NODE%d -> NODE0;\n' % index
            index += 1
        for line in self.data_outputs:
            text += 'NODE%d [label="%s", color="#888888"];\n' % (index,line)
            text += 'NODE0 -> NODE%d;\n' % index
            index += 1
        return text
        

    
class DoFile(Node):
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
    
class Parser(object):
    def walk_directory(self):
        pass 
    def read_yaml_file(self):
        pass 
    
if __name__=="__main__":
    dofile = DoFile(sys.argv[1])
    dofile.extract_inputs_and_outputs()
    print dofile.get_yaml()
    print dofile.get_blockdiag()
