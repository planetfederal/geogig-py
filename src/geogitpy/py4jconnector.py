from py4j.java_gateway import JavaGateway
import logging
from geogitexception import GeoGitException
from cliconnector import CLIConnector
import subprocess
import os
import time

_proc = None
_gateway = None

def _connect():
    global _gateway    
    try: 
        _gateway = JavaGateway()       
        _gateway.entry_point.isGeoGitServer()        
    except Exception, e:
        _gateway = None                   
        global _proc
        _proc = subprocess.Popen("geogit-gateway.bat", stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        time.sleep(3) #improve this and wait until the "server started" string is printed out        
        try:            
            _gateway = JavaGateway()
            _gateway.entry_point.isGeoGitServer()                   
        except Exception, e:
            _gateway = None
            raise Exception("Cannot start GeoGit gateway server")               

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
            print _proc.pid
            subprocess.Popen("TASKKILL /F /PID " + str(_proc.pid) + " /T", stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        else:
            pass #TODO        
        _proc = None
        
def _runGateway(command, url):     
    command = " ".join(command)
    command = command.replace("\r", "")
    _javaGateway().entry_point.setRepository(url)    
    returncode = _javaGateway().entry_point.runCommand(command)
    output = _javaGateway().entry_point.lastOutput()    
    output = output.strip("\r\n").split("\n")
    output = [s.strip("\r\n") for s in output]        
    if returncode:                        
        logging.error("Error running " + command + "\n" + " ".join(output))
        raise GeoGitException(output)
    logging.info("Executed " + command + "\n" + " ".join(output[:5]))      
    return output    

    
class Py4JCLIConnector(CLIConnector):    
    ''' A connector that uses a Py4J gateway server to conenct to geogit'''

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
        self.repo = repo          
        
