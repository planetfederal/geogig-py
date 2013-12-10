from py4j.java_gateway import JavaGateway
import logging
from geogitexception import GeoGitException
from cliconnector import CLIConnector
import subprocess
import os
import time

_proc = None
_gateway = None

def _connect(geogitPath):
    global _gateway    
    try: 
        _gateway = JavaGateway(start_callback_server=True)       
        _gateway.entry_point.isGeoGitServer()        
    except Exception, e:
        _gateway = None                   
        global _proc
        if os.name == 'nt':
            _proc = subprocess.Popen([geogitPath + "geogit-gateway.bat"], shell = True)
        else:
            _proc = subprocess.Popen(geogitPath + "geogit-gateway", stdout=subprocess.PIPE, stdin=subprocess.PIPE)

        time.sleep(3) #improve this and wait until the "server started" string is printed out        
        try:            
            _gateway = JavaGateway(start_callback_server=True)
            _gateway.entry_point.isGeoGitServer()                   
        except Exception, e:
            _gateway = None
            raise Exception("Cannot start GeoGit gateway server.\n"
                            +"Check that 'geogit-gateway' is available in PATH.\n"
                            +"If problems persist, start the gateway server manually.")               

def _javaGateway(geogitPath):    
    global _gateway
    if _gateway is None:
        _connect(geogitPath)
    return _gateway

def shutdownServer():    
    global _gateway, _proc
    _gateway = None
    if _proc is not None:
        if os.name == 'nt':            
            subprocess.Popen("TASKKILL /F /PID " + str(_proc.pid) + " /T", shell = True)
        else:
            pass #TODO        
        _proc = None
        
def _runGateway(command, url, geogitPath):     
    command = " ".join(command)
    command = command.replace("\r", "")
    _javaGateway(geogitPath).entry_point.setRepository(url)     
    returncode = _javaGateway(geogitPath).entry_point.runCommand(command)
    output = _javaGateway(geogitPath).entry_point.lastOutput()            
    output = output.strip("\r\n").split("\n")
    output = [s.strip("\r\n") for s in output]        
    if returncode:                                
        raise GeoGitException("\n".join(output))
    logging.info("Executed " + command + "\n" + " ".join(output[:5]))      
    return output    

    
class Py4JCLIConnector(CLIConnector):    
    ''' A connector that uses a Py4J gateway server to connect to geogit'''

    def __init__(self, geogitPath = ""):
        self.geogitPath = geogitPath 
        self.commandslog = []
        
    def silentProgress(self, i):
        pass
    
    @staticmethod
    def clone(url, dest, geogitPath = ""):            
        commands = ['clone', url, dest]
        _runGateway(commands, url, geogitPath) 
        
    def run(self, commands):
        self.commandslog.append(" ".join(commands))                
        return _runGateway(commands, self.repo.url, self.geogitPath)

    def setRepository(self, repo):
        self.repo = repo    

    def setProgressListener(self, listenerFunc):
        class Listener(object):
            def __init__(self, listener):
                self.listener = listener
            
            def setProgress(self, i):
                self.listener.setProgress(i)

            class Java:
                implements = ['org.geogit.cli.GeoGitPy4JProgressListener']
        
        _javaGateway(self.geogitPath).entry_point.setProgressListener(Listener(listenerFunc))

        
