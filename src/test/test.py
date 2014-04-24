import os
import sys
from geogitpy.cliconnector import CLIConnector
from geogitpy.py4jconnector import shutdownServer
import shutil

libpath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(libpath)        

from testrepo import testRepo
import unittest
from repotest import GeogitRepositoryTest
from treetest import GeogitTreeTest
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
   

if __name__ == '__main__': 
    path = testRepo().url;
    shutil.rmtree(path, False)
    runner=unittest.TextTestRunner()
    runner.run(suite())
    shutdownServer()
    shutil.rmtree(path, True)
