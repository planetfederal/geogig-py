import unittest
from treetest import GeogitTreeTest
from testrepo import testRepo
from repotest import GeogitRepositoryTest
from featuretest import GeogitFeatureTest
from commitishtest import GeogitCommitishTest
from committest import GeogitCommitTest
from difftest import GeogitDiffTest

def suite():
    suite = unittest.makeSuite(GeogitTreeTest, 'test')    
    suite.addTests(unittest.makeSuite(GeogitRepositoryTest, 'test'))
    suite.addTests(unittest.makeSuite(GeogitFeatureTest, 'test'))
    suite.addTests(unittest.makeSuite(GeogitCommitishTest, 'test'))
    suite.addTests(unittest.makeSuite(GeogitCommitTest, 'test'))
    suite.addTests(unittest.makeSuite(GeogitDiffTest, 'test'))
    return suite