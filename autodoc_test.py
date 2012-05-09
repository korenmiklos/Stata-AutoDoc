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
            ('"long stuff.dta"',None,'"long stuff.dta"'),
        )

    def test_normalize(self):
        for each in self.known:
            # known nornalizations
            self.assertEqual(normalize(each[0],each[1]),each[2])

def make_DoNode(filecontent):
    class Mock(DoFile):
        def open_for_reading(self):
            return filecontent.splitlines()
    return Mock()

class TestNode(ut.TestCase):
    def setUp(self):
        self.graph = Graph()
        self.node = Node(filename='',node_type=None,graph=self.graph)
        
    def test_tempfile_exists(self):
        # when I add a tempfile, it should be listed
        self.node.add_tempfile('tmp1')
        self.failUnless(self.node.is_tempfile('tmp1'))

    def test_nonexistent_tempfile(self):
        # a nonexistent tempfile should not be listed
        self.failIf(self.node.is_tempfile('tmp2'))

    def test_hash_robust_to_whitespace(self):
        # hash should not change with whitespace
        pass 

    def test_hash_changes_with_content(self):
        # hash should change with content
        pass 

    def test_short_hash_vs_long(self):
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
    # set up a mock node
        sample_file1 = make_DoNode('''
                /* customs and bertarifa merge */
                clear
                set mem 650m
                set more off

                selectdir /share/datastore /media/home/share/datastore
                local datastore `r(found)'

                /* read bertarifa */
                use `datastore'/bertarifa/balance9103_cleaned, clear
                d
                drop tmp* ln* foreign
                ''')
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
