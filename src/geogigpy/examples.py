import geogig
from geogigpy.commit import Commit
import os
import time
from geogigpy.repo import Repository

def squash_latest(repo, n, message = None):
    '''
    Squashes the latest n commits into a single one.
    If a message is passed, it uses it for the resulting commit.
    Otherwise, it uses the messages from the squashed commits
    ''' 
    if n < 1:
        raise Exception("Cannot squash less than 2 commits")    
    log = repo.log()
    if len(log) < n:
        raise Exception("Not enough commits in history")        
    message = message or "\n".join([commit.message for commit in log[:n]])
    repo.reset(log[n].ref, geogig.RESET_MODE_MIXED)
    repo.add()
    repo.commit(message)
    
def squash(repo, refa, refb, message = None):
    '''
    Squashes all the commits between two given ones, 'refa' and 'refb'.
    Commits are passed as a string with the corresponding commit id
    If a message is passed, it uses it for the resulting commit.
    Otherwise, it uses the messages from the squashed commits
    '''
    head = repo.head
    
    commita = Commit.fromref(repo, refa);
    commitb = Commit.fromref(repo, refb);    
    
    if commita.committerdate > commitb.committerdate:
        refa, refb = refb, refa
        commita, commitb = commitb, commita
        
    #store the commits after the last one to squash
    commits = []
    c = head
    commitid = c.id   
    while commitid != refb:
        commits.append(commitid)
        c = c.parent
        commitid = c.id  
                
    #squash the selected commmits        
    repo.reset(refb, geogig.RESET_MODE_HARD)
    repo.reset(commita.parent.id, geogig.RESET_MODE_MIXED)
    
    if message is None:
        messages = []
        c = commitb
        messages.append(c.message)
        while c.ref != refa:
            c = c.parent
            messages.append(c.message)
            
        message = "+".join(messages)

    repo.add()
    repo.commit(message)
    
    #And now add the remaining commits that we previously stored      
    for c in reversed(commits):
        repo.cherrypick(c)
            
    
    
def blame(repo):
    '''
    Returns a dict with tree names ids as keys and the name of the last 
    person to edit each tree as values
    '''
    authors = {}    
    for tree in repo.trees:
        path = tree.path
        log = repo.log(path)
        authors[path] = log[0].authorname 
    return authors
            
def export_tp_pg(repo, host, user, password, port, database, schema = "public"):
    for tree in repo.trees:
        path = tree.path
        repo.exportpg(geogig.HEAD, path, path, database, user, password, schema, host, port)
    

def getTempPath():
    return os.path.join(os.path.dirname(__file__), "temp", str(time.time())).replace('\\', '/')

def getClonedRepo(): 
    repo = Repository(os.path.join(os.path.dirname(__file__), '../test/data/testrepo'))
    dst = getTempPath()
    return repo.clone(dst) 
    
    
if __name__ == '__main__':
    #===========================================================================
    # repo = getClonedRepo()
    # log = repo.log()
    # print len(log)
    # squashLatest(repo, 2, "new_message")
    # log = repo.log()
    # print len(log)
    # print log[0].message
    # 
    #===========================================================================
    repo = getClonedRepo()
    log = repo.log()
    print len(log)
    squash(repo, log[2].ref, log[1].ref)
    log = repo.log()
    print len(log)
    print log[0].message
    print log[1].message
    
    
    