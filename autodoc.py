import yaml
import re
import sys

NODE_REGEX = """(?P<node>[.\w_"`'/]*)"""
NAME_REGEX = """(?P<node>[\w\s]*)"""

REGEXES = (
    (re.compile("\s*tempfile\s+"+NAME_REGEX+".*"), 'tempfile'),
    (re.compile("\s*use\s+"+NODE_REGEX+".*"), 'data_input'),
    (re.compile(".*(merge|csvmerge|append|insheet|infile|cross|join).*\s+using\s+"+NODE_REGEX+".*"), 'data_input'),
    (re.compile("\s*(do|run)\s+"+NODE_REGEX+".*"), 'script_input'),
    (re.compile("\s*(save|saveold)\s+"+NODE_REGEX+".*"), 'data_output'),
    (re.compile(".*(outsheet|outfile|log).*\s+using\s+"+NODE_REGEX+".*"), 'data_output'),
    )

class Node(object):
    def __init__(self,filename):
        self.filename = filename
        self.dependencies = {
                'data_input': [],
                'script_input': [],
                'data_output': [],
            }
        self.state = []

    @property
    def data_inputs(self):
        return self.dependencies['data_input']

    @property
    def data_outputs(self):
        return self.dependencies['data_output']
        
    @property
    def script_inputs(self):
        return self.dependencies['script_input']
        
    def add_state(self,text):
        if not text in self.state:
            self.state.append(text)

    def is_in_state(self,text):
        return text in self.state

    def add_dependency(self,text,categ):
        if categ=="tempfile":
            for name in text.split():
                # multiple tempfile names may be separated by space
                self.add_state("`"+name+"'")
        elif not text in self.dependencies[categ]:
            self.dependencies[categ].append(text)

    def add_data_input(self,text):
        self.add_dependency(self,text,'data_input')
            
    def add_script_input(self,text):
        self.add_dependency(self,text,'script_input')
            
    def add_data_output(self,text):
        self.add_dependency(self,text,'data_output')

    def get_absolute_path(self):
        pass 
    def get_canonical_name(self):
        return self.filename
        
    def open_for_reading(self):
        return open(self.filename,"r")
        
    def get_yaml(self):
        dct = {"Data inputs" : self.data_inputs,
         "Script inputs": self.script_inputs,
         "Data outputs": self.data_outputs,
         "Temporary files": self.state}
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
            for rgx, categ in REGEXES:
                if rgx.match(line):
                    m = rgx.match(line)
                    node = m.groupdict()['node']
                    if not self.is_in_state(node):
                        # only add if not a temporary file
                        self.add_dependency(node,categ)
            

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
