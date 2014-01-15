from py4j.java_gateway import JavaGateway
import logging
from geogitexception import GeoGitException
from cliconnector import CLIConnector
import subprocess
import os
import time
import gc

_proc = None
_gateway = None
_geogitPath = None

def setGeoGitPath(path):
    global _geogitPath
    _geogitPath = path

def _connect():    
    global _gateway
    try: 
        _gateway = JavaGateway()       
        _gateway.entry_point.isGeoGitServer()        
    except Exception, e:
        _gateway = None                   
        global _proc, _geogitPath
        geogitPath = _geogitPath or os.getenv("GEOGIT_HOME", "")
        try:            
            if os.name == 'nt':
                _proc = subprocess.Popen([os.path.join(geogitPath , "geogit-gateway.bat")], shell = True)
            else:
                _proc = subprocess.Popen(os.path.join(geogitPath, "geogit-gateway"), stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    
            time.sleep(3) #improve this and wait until the "server started" string is printed out                            
            _gateway = JavaGateway()
            _gateway.entry_point.isGeoGitServer()                   
        except Exception, e:
            _gateway = None
            raise Py4JConnectionException()               

def _javaGateway():    
    global _gateway
    if _gateway is None:
        _connect()
    return _gateway

def shutdownServer():    
    global _gateway, _proc
    _gateway = None
    if _proc is not None:
        if os.name == 'nt':            
            subprocess.Popen("TASKKILL /F /PID " + str(_proc.pid) + " /T", shell = True)
        else:
            os.kill(_proc.pid, signal.SIGKILL)        
        _proc = None
        
def _runGateway(command, url): 
    gc.collect()    
    command = " ".join(command)
    command = command.replace("\r", "")    
    returncode = _javaGateway().entry_point.runCommand(url, command)
    output = _javaGateway().entry_point.lastOutput()            
    output = output.strip("\n\r").replace("\r\n", "\n").replace("\r    ", "\n").split("\n")
    output = [s.strip("\r\n") for s in output]        
    if returncode:                                
        raise GeoGitException("\n".join(output))
    logging.info("Executed " + command + "\n" + " ".join(output[:5]))      
    return output    


def removeProgressListener():
    global _gateway    
    _javaGateway().entry_point.removeProgressListener()

def setProgressListener(listenerFunc):
    class Listener(object):
        def __init__(self, listener):
            self.listener = listener
        
        def setProgress(self, i):
            self.listener(i)

        class Java:
            implements = ['org.geogit.cli.GeoGitPy4JProgressListener']
    
    _javaGateway().entry_point.setProgressListener(Listener(listenerFunc))
    
class Py4JConnectionException(Exception):
    pass
    
class Py4JCLIConnector(CLIConnector):    
    ''' A connector that uses a Py4J gateway server to connect to geogit'''

    def __init__(self):
        self.commandslog = []
        
    def silentProgress(self, i):
        pass
    
    @staticmethod
    def clone(url, dest):            
        commands = ['clone', url, dest]
        _runGateway(commands, url) 
        
    def run(self, commands):
        self.commandslog.append(" ".join(commands))                
        return _runGateway(commands, self.repo.url)

    def setRepository(self, repo):
        self.repo = repo    
        
    def checkIsAlive(self):
        _connect()
        
        


        
