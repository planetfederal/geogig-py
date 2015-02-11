import subprocess
import os
import tempfile
import logging
import geogig
from collections import defaultdict
from feature import Feature
from tree import Tree
from commit import Commit
import datetime
from diff import Diffentry, ATTRIBUTE_DIFF_MODIFIED
from connector import Connector
from commitish import Commitish
from geogigpy.geogigexception import GeoGigException, GeoGigConflictException, UnconfiguredUserException
from geometry import Geometry
from copy import deepcopy
from geogigexception import GeoGigException

def _run(command, addcolor = True):         
    command = ['geogig'] + command
    if addcolor:
        command.extend(["--color", "never"])
    commandstr = " ".join(command)
    if os.name != 'nt':
        command = commandstr
    output = []   
    proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, 
                            stdin=subprocess.PIPE,stderr=subprocess.STDOUT, universal_newlines=True)
    for line in iter(proc.stdout.readline, ""):        
        line = line.strip("\n")
        output.append(line)            
    proc.wait()
    returncode = proc.returncode  
    if returncode:                        
        logging.error("Error running " + commandstr + "\n" + " ".join(output))
        raise GeoGigException(output)
    logging.info("Executed " + commandstr + "\n" + " ".join(output[:5]))      
    return output

    
class CLIConnector(Connector):
    ''' A connector that calls the CLI version of geogig and parses CLI output'''
    
    def __init__(self):
        self.commandslog = []        

    def setRepository(self, repo):
        self.repo = repo                     

    def createdat(self):
        return datetime.datetime.fromtimestamp(os.stat(os.path.join(self.repo.url, ".geogig")).st_ctime)
    
    @staticmethod
    def clone(url, dest, username = None, password = None):        
        commands = ['clone', url, dest]
        if username is not None and password is not None:
            commands.extend(["--username", username, "--password", password])
        _run(commands)    

    def geogigversion(self):
        output = self.run(["--version"])
        return output[0].split(":")[1].strip()    
                
    def run(self, command):   
        os.chdir(self.repo.url)         
        self.commandslog.append(" ".join(command))
        return _run(command)        

    def revparse(self, rev):
        commands = ['rev-parse', rev]
        output = self.run(commands)
        id = output[0].strip()
        if len(id) != 40:
            raise GeoGigException("Cannot resolve the provided reference")        
        return id
    
    def head(self):
        self.checkisrepo()
        headfile = os.path.join(self.repo.url, '.geogig', 'HEAD')
        f = open(headfile)
        line = f.readline()
        f.close()
        ref = line.strip().split()[-1]
        if ref.startswith("refs/heads/"):
            ref = ref[len("refs/heads/"):]
        return Commitish(self.repo, ref)           

    def isrebasing(self):
        self.checkisrepo()
        headfile = os.path.join(self.repo.url, '.geogig', 'ORIG_HEAD')
        branchfile =  os.path.join(self.repo.url, '.geogig', 'rebase-apply', 'branch')
        return os.path.exists(headfile) and os.path.exists(branchfile) 
    
    def ismerging(self):
        self.checkisrepo()
        headfile = os.path.join(self.repo.url, '.geogig', 'ORIG_HEAD')
        mergeheadfile = os.path.join(self.repo.url, '.geogig', 'MERGE_HEAD')        
        return os.path.exists(headfile) and os.path.exists(mergeheadfile)    
        
    def mergemessage(self):
        msgfile = headfile = os.path.join(self.repo.url, '.geogig', 'MERGE_MSG')
        if os.path.exists(msgfile):
            with open(msgfile) as f:
                lines = f.readlines()
            return "".join(lines)
        else:            
            return "" 
        
    def checkisrepo(self):
        if not os.path.exists(os.path.join(self.repo.url, '.geogig')):
            raise GeoGigException("Not a valid GeoGig repository: " + self.repo.url)
        
    
    def children(self, ref = geogig.HEAD, path = None, recursive = False):
        children = []    
        if path is None:
            fullref = ref
        else:
            fullref = ref + ':' + path 
        commands = ['ls-tree', fullref, "-v"]
        if recursive:
            commands.append("-r")
        output = self.run(commands)    
        for line in output:
            if line != '':                
                tokens = line.split(" ")
                if tokens[1] == "feature":
                    children.append(Feature(self.repo, ref, tokens[3]))
                elif tokens[1] == "tree":
                    try:
                       size = int(tokens[5])
                    except:
                       size = None
                    children.append(Tree(self.repo, ref, tokens[3], size))
        return children   
    
    def commitFromString(self, lines):                
        message = False
        messagetext = []
        parents = None
        commitid = None
        for line in lines:
            tokens = line.split(' ')
            if message:
                if line.startswith("\t") or line.startswith(" "):
                    messagetext.append(line.strip())
                else:
                    message = False            
            else:                
                if tokens[0] == 'commit':
                    commitid = tokens[1]
                if tokens[0] == 'tree':
                    tree = tokens[1]                    
                if tokens[0] == 'parent':                    
                    if len(tokens) > 1:
                        parents = [t for t in tokens[1:] if t != ""]                    
                elif tokens[0] == 'author':
                    author = " ".join(tokens[1:-3])
                    authordate = datetime.datetime.fromtimestamp((int(tokens[-2]) - int(tokens[-1]))//1000)                
                elif tokens[0] == 'committer':
                    committer = tokens[1]
                    committerdate = datetime.datetime.fromtimestamp((int(tokens[-2]) - int(tokens[-1]))//1000)
                elif tokens[0] == 'message':
                    message = True                
            
        if commitid is not None:            
            c = Commit(self.repo, commitid, tree, parents, "\n".join(messagetext), author, authordate, committer, committerdate)
            return c
        else:
            return None

    def addremote(self, name, url, username, password):
        if username and password:
            commands = ["remote", "add", "-u", username, "--password", password, name, url]
        else:
            commands = ["remote", "add", name, url]
        self.run(commands)
        
    def removeremote(self, name):
        commands = ["remote", "rm", name]
        self.run(commands)     
        
    def remotes(self):
        commands = ["remote", "list", "-v"]
        output = self.run(commands)
        remotes = {}        
        for line in output:
            tokens = line.split()
            if len(tokens) != 3:
                continue
            if tokens[0] not in remotes:
                remotes[tokens[0]] =  tokens[1]                
        return remotes        
        
    def log(self, tip, sincecommit = None, until = None, since = None, path = None, n = None):
        commits = []             
        param = tip if sincecommit is None else (sincecommit + ".." + tip)   
        commands = ['rev-list', param]        
        if path:
            if isinstance(path, list):
                commands.append("-p")
                commands.extend(path)
            else:
                commands.extend(["-p", path])
        if until is not None:
            commands.extend(["--until", until])
        if since is not None:
            commands.extend(["--since", since])            
        if n is not None:
            commands.extend(["-n", str(n)])            
        try:
            output = self.run(commands)
        except GeoGigException, e:
            if "HEAD does not resolve" in e.args[0]: #empty repo
                return []
            else:
                raise e                
        commitlines = []
        for line in output:
            if line == '':
                commit = self.commitFromString(commitlines)
                if commit is not None:
                    commits.append(commit)
                    commitlines = []
            else:
                commitlines.append(line)            
            
        if commitlines:
            commit = self.commitFromString(commitlines)
            if commit is not None:
                commits.append(commit)
        return commits 
    
    def conflicts(self):
        conflictsfile = os.path.join(self.repo.url, ".geogig","conflicts")        
        try:
            if os.path.getsize(conflictsfile) == 0:
                return {}
        except Exception:
            return {} 
        
        commands = ["conflicts", "--refspecs-only"]
        lines = self.run(commands)
        _conflicts = {}
        for line in lines:
            if line.startswith("No elements need merging"):
                return {}
            tokens = line.split(" ")
            _conflicts[tokens[0]] = (tokens[1][:40], tokens[2][:40], tokens [3][:40])
        return _conflicts
            
    def solveconflicts(self, paths, version = geogig.OURS):
        commands = ["checkout"]        
        if version == geogig.OURS:
            commands.append("--ours")
        elif version == geogig.THEIRS:
            commands.append("--theirs")
        else:
            raise GeoGigException("Unknown option:" + version)        
        commands.append("-p")
        commands.extend(paths)
        self.run(commands)   
        self.add(paths)         
        
    def checkout(self, ref, paths = None, force = False):        
        commands = ['checkout', ref]
        if paths is not None and len(paths) > 0:            
            commands.append("-p")
            commands.extend(paths)
        elif force:
            commands.append("--force")        
        self.run(commands)
        
    def reset(self, ref, mode = 'hard', path = None):
        if path is None:
            self.run(['reset', ref, "--" + mode])
        else:
            command =['reset', ref, '-p']
            command.append(path) 
            self.run(command)                    
        
    def _refs(self, prefix):
        refs = {}
        output = self.run(['show-ref'])
        for line in output:                 
            tokens = line.strip().split(" ")
            if tokens[1].startswith(prefix):
                refs[tokens[1][len(prefix):]] = tokens[0]
        return refs

    def branches(self):    
        return self._refs("refs/heads/")
        
    def tags(self):
        return self._refs("refs/tags/")        
    
    def createbranch(self, ref, name, force = False, checkout = False):
        commands = ['branch', name, ref]
        if force:
            commands.append('-f')
        if checkout:
            commands.append('-c')            
        self.run(commands)

    def deletebranch(self, name):        
        self.run(['branch', '-d', name])     

    def createtag(self, ref, name, message):        
        self.run(['tag', name, ref, '-m', message])

    def deletetag(self, name):   
        self.run(['tag', '-d', name])        
       
    def add(self, paths = []):
        if paths:
            for path in paths:      
                self.run(['add', path])
        else:
            self.run(['add'])
            
    def commit(self, message, paths = []):
        commands = ['commit', '-m']
        commands.append('"%s"' % message)
        commands.extend(paths)
        try:
            self.run(commands)
        except GeoGigException, e:
            if "user.name not found" in e.args[0] or "user.email not found" in e.args[0]: 
                raise UnconfiguredUserException()
            else:
                raise e
                           
             
    def diffentryFromString(self, oldcommitref, newcommitref, line):
        tokens = line.strip().split(" ")
        path = " ".join(tokens[0:-2])
        oldref = tokens[-2]
        newref = tokens[-1]
        return Diffentry(self.repo, oldcommitref, newcommitref, oldref, newref, path) 
    
    
    def diff(self, refa, refb, path = None): 
        diffs = []        
        commands = ['diff-tree', refa, refb]
        if path is not None:
            commands.extend(["--", path])
        output = self.run(commands) 
        for line in output:
            if line != '':
                diffs.append(self.diffentryFromString(refa, refb, line))
        return diffs
    
    def difftreestats(self, refa, refb):
        output = self.run(['diff-tree', refa, refb, "--tree-stats"])
        stats = {}
        for line in output:            
            tokens = line.split(" ")
            if len(tokens) == 4: 
                stats[tokens[0]] = tuple(int(t) for t in tokens[1:])
        return stats

    def treediff(self, path, refa, refb):
        attribs = None
        try:
            ftypea = self.featuretype(refa, path)
        except GeoGigException:
            ftypea = {}
        try:
            ftypeb = self.featuretype(refb, path)
        except GeoGigException:
            ftypeb = {}
        attribs = deepcopy(ftypea)
        attribs.update(ftypeb)   # we assume that there are no repeated attrib names with different type
        
        commands = ['diff-tree', refa, refb, "--", path, "--describe"]
        lines = self.run(commands) 
        features = []
        difflines = []
        i = 0
        previousLine = None
        while i < len(lines):
            line = lines[i]
            if line == '':
                if difflines:                
                    changes = self.difffromstring(difflines, attribs)
                    features.append(changes)
                    difflines = []                                    
            else: 
                if difflines:
                    difflines.append(line)
                    tokens = line.split(" ")
                    i += 1
                    difflines.append(lines[i])
                    if tokens[0] == ATTRIBUTE_DIFF_MODIFIED:
                        i += 1
                        difflines.append(lines[i])                        
                else:
                    difflines.append(line)
            i += 1             
            
        if difflines:
            changes = self.difffromstring(difflines, attribs)
            features.append(changes)
        return attribs, features

    def difffromstring(self, lines, attribs):
        i = 1
        changes = {}
        while i < len(lines):
            tokens = lines[i].split(" ")
            attribute = tokens[1]
            changeType = tokens[0]
            i += 1
            if changeType == ATTRIBUTE_DIFF_MODIFIED:
                value = self.valuefromstring(lines[i], attribs[attribute])
                i += 1
                value2 = self.valuefromstring(lines[i], attribs[attribute])
                changes[attribute] = (changeType, value, value2)
            else:
                value = self.valuefromstring(lines[i], attribs[attribute])
                changes[attribute] = (changeType, value)
            i += 1                
        orderedchanges = []
        for attrib in attribs:
            orderedchanges.append(changes[attrib])
        return orderedchanges
 
    
    def importosm(self, osmfile, add = False, mappingfile = None):
        commands = ["osm", "import", osmfile]        
        if add:
            commands.extend(["--add"])
        if mappingfile is not None:
            commands.extend(["--mapping", mappingfile])
        self.run(commands)
        
    def exportosm(self, osmfile, ref = None, bbox = None):
        commands = ["osm", "export", osmfile]
        if ref is not None:
            commands.append(ref)
        if bbox is not None:
            commands.extend(bbox)  
    
    def exportosmchangeset(self, osmfile, changesetid = None, refa = None, refb = None):
        commands = ["osm", "create-changeset", "-f" , osmfile]
        if refa is not None:
            commands.append(refa) 
        if refb is not None:
            commands.append(refb)
        if id is not None:
            commands.extend(["--id", changesetid])
        self.run(commands)                    
        
    def downloadosm(self, osmurl, bbox, mappingfile = None):
        commands = ["osm", "download", osmurl, "--bbox"]
        commands.extend([str(c) for c in bbox])         
        if mappingfile is not None:
            commands.extend(["--mapping", mappingfile])       
        self.run(commands)        
        
    def maposm(self, mappingfile):
        commands = ["osm", "map", mappingfile]
        self.run(commands) 
        
    def importgeojson(self, geojsonfile, add = False, dest = None, idAttribute = None, geomName = None, force=False):
        commands = ["geojson", "import", geojsonfile]
        if dest is not None:
            commands.extend(["--dest", dest])
        if idAttribute is not None:
            commands.extend(["--fid-attrib", idAttribute])            
        if geomName is not None:
            commands.extend(["--geom-name", geomName])            
        if add:
            commands.append("--add")
        if force:
            commands.append("--force-featuretype")            
        self.run(commands)
        
    def importshp(self, shapefile, add = False, dest = None, idAttribute = None, force=False):
        commands = ["shp", "import", shapefile]
        if dest is not None:
            commands.extend(["--dest", dest])
        if idAttribute is not None:
            commands.extend(["--fid-attrib", idAttribute])            
        if add:
            commands.append("--add")
        if force:
            commands.append("--force-featuretype")            
        self.run(commands)
    
    def importpg(self, database, user = None, password = None, table = None, 
                 schema = None, host = None, port = None, add = False, dest = None,
                 force = False, idAttribute = None):
        commands = ["pg", "import", "--database",database]
        if user is not None:
            commands.extend(["--user", user])
        if password is not None:
            commands.extend(["--password", password])
        if schema is not None:
            commands.extend(["--schema", schema])            
        if port is not None:
            commands.extend(["--port", str(port)])            
        if dest is not None:
            commands.extend(["--dest", dest])
        if table is not None:
            commands.extend(["--table", table])
        else:
            commands.append("--all")
        if host is not None:
            commands.extend(["--host", host])
        if idAttribute is not None:
            commands.extend(["--fid-attrib", idAttribute])            
        if add:
            commands.append("--add")
        if force:
            commands.append("--force-featuretype")             
        self.run(commands)
        
    def importsl(self, database, table, add = False, dest = None):         
        commands = ["sl", "import", "--database",database]                    
        if dest is not None:
            commands.extend(["--dest", dest])        
        commands.extend(["--table", table])        
        if add:
            commands.append("--add")
        self.run(commands)
        
    def exportpg(self, ref, path, table, database, user, password = None, schema = None, host = None, port = None,  overwrite = False):
        table = table or path
        refandpath = ref + ":" + path
        commands = ["pg", "export", refandpath, table, "--database", database]                
        if user is not None:
            commands.extend(["--user", user])
        if password is not None:
            commands.extend(["--password", password])
        if schema is not None:
            commands.extend(["--schema", schema])  
        if port is not None:
            commands.extend(["--port", str(port)])                    
        if host is not None:
            commands.extend(["--host", host])
        if overwrite:
            commands.append("-o")
        self.run(commands)
        
    def exportshp(self, ref, path, shapefile):
        refandpath = ref + ":" + path
        self.run(["shp", "export", refandpath, shapefile, "-o", "--defaulttype"])
        
    def exportsl(self, ref, path, database, user = None, table = None):
        table = table or path
        refandpath = ref + ":" + path
        commands = ["sl", "export", refandpath,  "--database", database, path]
        if user is not None:
            commands.extend(["--user", user])
        self.run(commands)
        
    def exportdiffs(self, commit1, commit2, path, filepath, old = False, overwrite = False):
        commands = ["shp", "export-diff", commit1, commit2, path, filepath]
        if old:
            commands.append("--old")
        if overwrite:
            commands.append("-o")            
        self.run(commands)
       
    def featuredata(self, ref, path):  
        refandpath = ref + ":" + path      
        output = self.run(["show", "--raw", refandpath])  
        return self.parseattribs(output[2:]) 

    def cat(self, reference):
        return "\n".join(self.run(["cat", reference]))
        
    def parseattribs(self, lines):
        attributes = {}
        iterator = iter(lines)
        while True:
            try:
                name = iterator.next()
                attribtype = iterator.next()
                value = iterator.next()
                value = self.valuefromstring(value, attribtype)
                attributes[name] = (value, attribtype)
            except StopIteration:
                return attributes 
        
    def valuefromstring(self, value, valuetype):  
        if value == "[NULL]":
            return None      
        tokens = valuetype.split(" ")        
        try:
            if valuetype == "BOOLEAN":
                return str(value).lower() == "true"
            elif valuetype in ["BYTE","SHORT","INTEGER","LONG"]:
                return int(value)
            elif valuetype in ["FLOAT","DOUBLE"]:
                return float(value)
            elif (valuetype in ["POINT","LINESTRING","POLYGON","MULTIPOINT","MULTILINESTRING","MULTIPOLYGON"] 
                    or len(tokens) > 1):                                    
                crs = " ".join(tokens[1:]) if len(tokens) > 1 else None
                return Geometry(value, crs)        
            else:
                return value
        except:
            return value 

    def featuresdata(self, refs):
        features = {}
        commands = ["show", "--raw"]
        commands.extend(refs);
        output = self.run(commands)        
        iterator = iter(output)
        lines = []    
        name = None    
        while True:
            try:
                line = iterator.next()
                if line == "":                
                    features[name] = self.parseattribs(lines)   
                    lines = []
                    name = None 
                else:
                    if name is None:
                        name = line
                        iterator.next() #consume id line
                    else: 
                        lines.append(line)   
            except StopIteration:
                break
        if lines:
            features[name] = self.parseattribs(lines)     
        return features

    def featuretype(self, ref, tree):
        show = self.show(ref + ":" + tree)
        ftypeid = show.splitlines()[3].split(" ")[-1]
        show = self.show(ftypeid)
        attribs = {}
        for line in show.splitlines()[3:]:
            tokens = line.split(":")
            attribs[tokens[0]] = tokens[1].strip()[1:-1]
        return attribs
    
    def featurediff(self, ref, ref2, path):
        try:
            data = self.featuredata(ref, path)
        except GeoGigException:
            data = None
        try:
            data2 = self.featuredata(ref2, path)
        except GeoGigException:
            data2 = None         
                
        if data is None:
            if data2 is None:
                return {}
            else:
                return dict(( (k, (None, v[0])) for k,v in data2.iteritems() ))
        elif data2 is None:
            return dict(( (k, (v[0], None)) for k,v in data.iteritems() ))
        
        diffs = {}
        for attr in data:
            if attr in data2:
                v = data[attr][0]
                v2 = data2[attr][0]
                equal = v == v2                
                if not equal:
                    diffs[attr] =(data[attr][0], data2[attr][0])
            else:
                diffs[attr] = (data[attr][0], None)
        for attr in data2:
            if attr not in data:                
                diffs[attr] = (None, data2[attr][0])
        return diffs
            
    def blame(self, path):
        attributes = {}
        output = self.run(["blame", path, "--porcelain"])  
        for line in output:
            tokens = line.split(" ")
            name = tokens[0]
            value = " ".join(tokens[6:])
            commitid = tokens[1]
            authorname = tokens[2]
            attributes[name]=(value, commitid, authorname)   
        return attributes 
    
    def commonancestor(self, refa, refb):
        commands = ["merge-base", refa, refb]        
        try:
            output = self.run(commands)            
            return Commitish(self.repo, output[0].strip())
        except GeoGigException, e:                    
            if "No common ancestor" in e.args[0]:
                return None
            else:
                raise e 
            
    def merge (self, ref, nocommit = False, message = None):        
        commands = ["merge", ref]
        if nocommit:
            commands.append("--no-commit")
        elif message is not None:
            commands.append("-m")
            commands.apend(message)
        try:
            self.run(commands) 
        except GeoGigException, e:            
            if "conflict" in e.args[0]:
                raise GeoGigConflictException(e.args[0])
            else:
                raise e

        
    def rebase(self, commitish):
        commands = ["rebase", commitish]
        try:
            self.run(commands) 
        except GeoGigException, e:
            if "conflict" in e.args[0]:
                raise GeoGigConflictException(e.args[0])
            else:
                raise e            
    
    def continue_(self):
        if self.isrebasing():
            commands = ["rebase", "--continue"]
            self.run(commands)
            if self.isrebasing():
                raise GeoGigException("Could not continue rebasing")
        
    def abort(self):
        if self.isrebasing():
            commands=["rebase", "--abort"]
            self.run(commands)            
        elif self.ismerging():
            self.reset(geogig.HEAD)        
            
    def cherrypick(self, commitish):
        commands = ["cherry-pick", commitish]
        self.run(commands)
    
    def init(self, initParams = None):
        if initParams is None: initParams = {}    
        commands = ["init"]
        if initParams is not None:
            commands.append(",".join([k + "=" + v for k,v in initParams.iteritems()]))            
        self.run(commands)
        
    def insertfeatures(self, features):               
        s = ""
        for path, attrs in features.iteritems():            
            s += path + "\n"            
            for attrName, attrValue in attrs.iteritems():  
                if attrValue is not None:                                   
                    s += attrName + "\t" + _tostr(attrValue) + "\n"
            s +="\n"
        try:
            f = tempfile.NamedTemporaryFile(delete = False)                           
            f.write(s)              
            f.close()
            commands = ["insert", "-f", f.name]
            self.run(commands)            
        finally:
            f.close() 
            try:                    
                pass#os.remove(f.name)
            except:
                pass   
                                             
    def removepaths(self, paths, recursive = False):
        paths.insert(0, "rm")
        if recursive:
            paths.append("-r")
        self.run(paths)
        
    def applypatch(self, patchfile):
        self.run(["apply", patchfile])   
        
    def show(self, ref):
        return "\n".join(self.run(["show", ref]))    
    
    def config(self,param, value, global_ = False):
        commands = ["config", param, value]
        if global_:
            commands.append("--global")
        self.run(commands) 
        
    def getconfig(self, param):
        value =  self.run(["config", "--get", param])
        value = value[0] if value else None
        return value
        
    def pull(self, remote, branch, rebase = False):
        commands = ["pull", remote, branch]
        if rebase:
            commands.append("--rebase")
        try:
            self.run(commands)
        except GeoGigException, e:
            if "conflict" in e.args[0]:
                raise GeoGigConflictException(e.args[0])
            else:
                raise e
        
    def push(self, remote, branch = None, all = False):
        if all:
            commands = ["push", remote, "--all"]
        else:
            commands = ["push", remote, branch]        
        self.run(commands)
        
def _tostr(v):
    try:
        d = float(v)
        if d.is_integer():
            return str(int(d))
        return str(d)
    except:
        return str(v)
