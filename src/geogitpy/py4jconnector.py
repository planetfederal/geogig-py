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
        _gateway = JavaGateway(start_callback_server=True)       
        _gateway.entry_point.isGeoGitServer()        
    except Exception, e:
        _gateway = None                   
        global _proc
        if os.name == 'nt':
            _proc = subprocess.Popen("geogit-gateway.bat", shell = True, 
                        stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr = subprocess.PIPE)
        else:
            _proc = subprocess.Popen("geogit-gateway", stdout=subprocess.PIPE, stdin=subprocess.PIPE)

        time.sleep(3) #improve this and wait until the "server started" string is printed out        
        try:            
            _gateway = JavaGateway(start_callback_server=True)
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
    print output
    output = output.strip("\r\n").split("\n")
    output = [s.strip("\r\n") for s in output]        
    if returncode:                                
        raise GeoGitException("\n".join(output))
    logging.info("Executed " + command + "\n" + " ".join(output[:5]))      
    return output    

    
class Py4JCLIConnector(CLIConnector):    
    ''' A connector that uses a Py4J gateway server to connect to geogit'''

    def __init__(self):
        self.commandslog = []
        
    def silentProgress(self, int):
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

    def setProgressListener(self, listenerFunc):
        class Listener(object):
            def __init__(self, listener):
                self.listener = listener
            
            def setProgress(self, i):
                listener.setProgress(i)

            class Java:
                implements = ['org.geogit.cli.GeoGitPy4JProgressListener']
        
        _javaGateway().entry_point.setProgressListener(Listener(listenerFunc))

        
