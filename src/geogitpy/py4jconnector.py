from py4j.java_gateway import JavaGateway, GatewayClient
import logging
from geogitexception import GeoGitException
from cliconnector import CLIConnector
import subprocess
import os
import time
import gc
import signal

_proc = None
_gateway = None
_geogitPath = None
_geogitPort = None

_logger = logging.getLogger("geogitpy")

  
def setGatewayPort(port):
    global _geogitPort
    _geogitPort = port

def _connect():    
    global _gateway
    try: 
        if _geogitPort is None:
            _gateway = JavaGateway()
        else:
            _gateway = JavaGateway(GatewayClient(port = int(_geogitPort)))     
        _gateway.entry_point.isGeoGitServer()        
    except Exception, e:             
        raise Py4JConnectionException()               

def _javaGateway():    
    global _gateway
    if _gateway is None:
        _connect()
    return _gateway

def _runGateway(commands, url, addcolor = True):    
    gc.collect()    
    if addcolor:
        commands.extend(["--color", "never"])
    command = " ".join(commands)
    command = command.replace("\r", "")   

    strclass = _javaGateway().jvm.String
    array = _javaGateway().new_array(strclass,len(commands))
    for i, c in enumerate(commands):
        array[i] = c
    start = time.clock()
    returncode = _javaGateway().entry_point.runCommand(url, array)
    end = time.clock()
    diff = end - start
    _logger.debug("Executed " + command  + "in " + str(diff) + " millisecs")
    output = [""]    
    page = _javaGateway().entry_point.nextOutputPage()
    while page is not None:
        output.append(page)
        page = _javaGateway().entry_point.nextOutputPage()
    output = "".join(output)            
    output = output.strip("\r\n").splitlines()
    output = [s.strip("\r\n") for s in output]        
    if returncode:                             
        errormsg = "\n".join(output)
        _logger.error("Error running command '%s': %s" % (command, errormsg))
        raise GeoGitException("\n".join(output))
         
    return output 


def removeProgressListener():
    global _gateway    
    _javaGateway().entry_point.removeProgressListener()

def setProgressListener(progressFunc, progressTextFunc):
    class Listener(object):
        def __init__(self, progressFunc, progressTextFunc):
            self.progressFunc = progressFunc
            self.progressTextFunc = progressTextFunc
        
        def setProgress(self, i):
            self.progressFunc(i)
            
        def setProgressText(self, s):
            self.progressTextFunc(s)

        class Java:
            implements = ['org.geogit.cli.GeoGitPy4JProgressListener']
    
    _javaGateway().entry_point.setProgressListener(Listener(progressFunc, progressTextFunc))
    
def geogitVersion():
    commands = ['--version']        
    try:
        out = _runGateway(commands, os.path.dirname(__file__), False)
        version = out[0].split(":")[1]
        sha = out[5].split(":")[1]
        return "-".join([version, sha])
    except Exception, e:
        print e
        return "Not available"
  
        
class Py4JConnectionException(Exception):
    pass
    
class Py4JCLIConnector(CLIConnector):    
    ''' A connector that uses a Py4J gateway server to connect to geogit'''

    def __init__(self):
        self.commandslog = []
        
    
    @staticmethod
    def clone(url, dest, username = None, password = None):            
        commands = ['clone', url, dest]  
        if username is not None and password is not None:
            commands.extend(["--username", username, "--password", password])      
        _runGateway(commands, os.path.dirname(__file__))        
    
    @staticmethod    
    def configglobal(param, value):
        commands = ['config', param, value, '--global']
        _runGateway(commands, os.path.dirname(__file__)) 
        
    @staticmethod    
    def getconfigglobal(param = None):
        if param is None:
            commands = ['config', '--list', '--global']
            output = _runGateway(commands, os.path.dirname(__file__))
            params = {}
            for line in output:
                k,v = line.split('=')
                params[k] = v
            return params
        else:
            commands = ['config', '--get', param]
            return _runGateway(commands, "dummy")
        
    def run(self, commands):
        self.commandslog.append(" ".join(commands))                
        return _runGateway(commands, self.repo.url)

    def setRepository(self, repo):
        '''
        Sets the repository to use when later passing commands to this connector using the "run" method
        '''
        self.repo = repo    
        
    def checkIsAlive(self):
        _connect()
                    
    
    def setGatewayPort(self, port):
        '''
        Sets the port to use for connecting to the gateway.
        '''        
        setGatewayPort(port)
        
        


        
