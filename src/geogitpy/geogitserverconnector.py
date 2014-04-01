import requests
from connector import Connector
from commit import Commit
import xml.etree.ElementTree as ET
from geogitexception import GeoGitException

class GeoGitServerConnector(Connector):
    ''' A connector that connects to a geogit repo through a geogit-server instance'''

    def log(self, tip, until = None, since = None, path = None, n = None):                
        url = self.url + "/commits"
        r = requests.get(url)
        commits = r.json()['commits']
        log = []
        for c in commits:
            commit = Commit(self.repo, c['sha'], None, c['parent'], c['[message]'], 
                            c['author']['name'], c['author']['date'], c['committer']['name'], c['committer']['date'])
            log.append(commit)
        return log
    
    def checkisrepo(self):
        try:
            url = self.url + '/commits'
            r = requests.get(self.url)
            response = r.json()
            return 'currentBranch' in reponse
        except:            
            return False
        
    def revparse(self, rev):
        try:
            url = self.url + '/refparse'
            r = requests.get(self.url, params = {'name' : rev})
            root = ET.fromstring(r.text)            
            id = root.iter('objectId').next().text
            return id   
        except:
            raise GeoGitException("Reference %s ot found" % rev)