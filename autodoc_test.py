from autodoc import *
import unittest as ut
import os

class TestFunctions(ut.TestCase):
    def setUp(self):
        self.known = (
            ('code/../data/cucc.dta',None,os.path.join('data','cucc.dta')),
            ('code//../data/cucc.dta',None,os.path.join('data','cucc.dta')),
            ('./script.do',None,'script.do'),
            ('code/../data/cucc','data',os.path.join('data','cucc.dta')),
        )

    def test_normalize(self):
        for each in self.known:
            # known nornalizations
            self.assertEqual(normalize(each[0],each[1]),each[2])

class TestNode(ut.TestCase):
    def setUp(self):
        # set up a mock node
        pass

    def test_tempfiles(self):
        # when I add a tempfile, it should be listed
        pass

    def test_hash(self):
        # hash should not change with whitespace
        # hash should change with content
        # short has should be trimmed long
        pass

    def test_attribute(self):
        # test list of attributes and their setting
        pass

    def test_name(self):
        # canonical name should be normalized
        pass

    def test_yaml(self):
        # get_yaml should return a valid yaml document
        pass

class TestGraph(ut.TestCase):
    def test_nodes_unique(self):
        pass

    def test_edges_unique(self):
        pass
    
    def test_blockdiag(self):
        # should return string, will not check validity
        pass

    
def TestDoFile(TestNode):
    # we should already have the mock set up
    def test_regexes(self):
        # test how the regexes resolve a known list of statements, good and bad
        pass
    def test_comments(self):
        # test comments are parsed well
        pass
    def test_graph(self):
        # test that dependencies are reflected in graph
        pass

if __name__ == '__main__':
    ut.main()
