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

def setGeoGitPath(path):
    global _geogitPath
    _geogitPath = path
    
def setGatewayPort(port):
    global _geogitPort, __gateway
    if _geogitPort != port:
        _geogitPort = port
        shutdownServer()

def _connect():    
    global _gateway
    try: 
        if _geogitPort is None:
            _gateway = JavaGateway()
        else:
            _gateway = JavaGateway(GatewayClient(port = _geogitPort))       
        _gateway.entry_point.isGeoGitServer()        
    except Exception, e:        
        _logger.debug("GeoGit gateway not started. Will try to start it")
        _gateway = None                   
        global _proc, _geogitPath
        if _geogitPath is None:
            _logger.debug("geogitPath not set, using GEOGIT_HOME env variable")            
        geogitPath = _geogitPath or os.getenv("GEOGIT_HOME", "")
        try:         
            _logger.debug("Trying to start gateway at %s" % (geogitPath))   
            if os.name == 'nt':
                _proc = subprocess.Popen([os.path.join(geogitPath , "geogit-gateway.bat")], shell = True)
            else:
                _proc = subprocess.Popen(os.path.join(geogitPath, "geogit-gateway"), stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    
            time.sleep(3) #improve this and wait until the "server started" string is printed out                            
            if _geogitPort is None:
                _gateway = JavaGateway()
            else:
                _gateway = JavaGateway(GatewayClient(port = _geogitPort))
            _gateway.entry_point.isGeoGitServer()                   
        except Exception, e:
            _logger.error("Could not start gateway (%s)" % (str(e))) 
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
        _logger.debug("Killing gateway process")
        if os.name == 'nt':            
            subprocess.Popen("TASKKILL /F /PID " + str(_proc.pid) + " /T", shell = True)
        else:
            os.kill(_proc.pid, signal.SIGKILL)        
        _proc = None
        
def _runGateway(commands, url):     
    gc.collect()    
    commands.extend(["--color", "never"])
    command = " ".join(commands)
    command = command.replace("\r", "")   
    _logger.debug("Running GeoGit command: " + command)     
    strclass = _javaGateway().jvm.String
    array = _javaGateway().new_array(strclass,len(commands))
    for i, c in enumerate(commands):
        array[i] = c
    returncode = _javaGateway().entry_point.runCommand(url, array)
    output = _javaGateway().entry_point.lastOutput()            
    output = output.strip("\n\r").replace("\r\n", "\n").replace("\r", "\n").split("\n")
    output = [s.strip("\r\n") for s in output]        
    if returncode:                             
        errormsg = "\n".join(output)
        _logger.error("Error running command '%s': %s" % (command, errormsg))
        raise GeoGitException("\n".join(output))
    logging.info("Executed " + command + "\n" + " ".join(output[:5]))      
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
    
class Py4JConnectionException(Exception):
    pass
    
class Py4JCLIConnector(CLIConnector):    
    ''' A connector that uses a Py4J gateway server to connect to geogit'''

    def __init__(self):
        self.commandslog = []
        
    
    @staticmethod
    def clone(url, dest):            
        commands = ['clone', url, dest]
        _runGateway(commands, url) 
        
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
                    
    def setGeoGitPath(self, path):
        '''
        Sets the path to GeoGit, to be used in case the gateway is not started, to try to run it
        '''
        setGeoGitPath(path)
    
    def setGatewayPort(self, port):
        '''
        Sets the port to use for connecting to the gateway.
        
        If a connection has already been made using this connector, the existing gateway client 
        object will be deleted
        
        If when creating that connection it was necessary to start the geogit-gateway (that is, if
        geogit-gateway was not started manually but automatically by this connector), the gateway server
        will be shutdown
        
        If the passed port is equal to the previous port, this method will do nothing, and all the above 
        does not apply 
        '''        
        setGatewayPort(port)
        
        


        
