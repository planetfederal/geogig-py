import unittest
from treetest import GeogigTreeTest
from testrepo import testRepo
from repotest import GeogigRepositoryTest
from featuretest import GeogigFeatureTest
from commitishtest import GeogigCommitishTest
from committest import GeogigCommitTest
from difftest import GeogigDiffTest

def suite():
    suite = unittest.makeSuite(GeogigTreeTest, 'test')    
    suite.addTests(unittest.makeSuite(GeogigRepositoryTest, 'test'))
    suite.addTests(unittest.makeSuite(GeogigFeatureTest, 'test'))
    suite.addTests(unittest.makeSuite(GeogigCommitishTest, 'test'))
    suite.addTests(unittest.makeSuite(GeogigCommitTest, 'test'))
    suite.addTests(unittest.makeSuite(GeogigDiffTest, 'test'))
    return suite