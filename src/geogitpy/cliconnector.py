import subprocess
import os
import tempfile
import logging
import geojson
import geogit
from collections import defaultdict
from feature import Feature
from tree import Tree
from commit import Commit
import datetime
from diff import Diffentry
from commitish import Commitish
from geogitpy.geogitexception import GeoGitException, GeoGitConflictException
from shapely.wkt import loads
from shapely.geometry import mapping
from shapely.geometry.base import BaseGeometry

def _run(command):         
    command = ['geogit'] + command
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
        raise GeoGitException(output)
    logging.info("Executed " + commandstr + "\n" + " ".join(output[:5]))      
    return output
    
class CLIConnector(object):
    ''' A connector that calls the CLI version of geogit and parses CLI output'''
    
    def __init__(self):
        self.commandslog = []        

    def setRepository(self, repo):
        self.repo = repo                     

    @staticmethod
    def clone(url, dest):        
        commands = ['clone', url, dest]
        _run(commands)    

    def geogitversion(self):
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
            raise GeoGitException("Cannot resolve the provided reference")        
        return id
    
    def head(self):
        self.checkisrepo()
        headfile = os.path.join(self.repo.url, '.geogit', 'HEAD')
        f = open(headfile)
        line = f.readline()
        f.close()
        ref = line.strip().split()[-1]
        if ref.startswith("refs/heads/"):
            ref = ref[len("refs/heads/"):]
        return Commitish(self.repo, ref)           

    def isrebasing(self):
        self.checkisrepo()
        headfile = os.path.join(self.repo.url, '.geogit', 'ORIG_HEAD')
        branchfile =  os.path.join(self.repo.url, '.geogit', 'rebase-apply', 'branch')
        return os.path.exists(headfile) and os.path.exists(branchfile) 
    
    def ismerging(self):
        self.checkisrepo()
        headfile = os.path.join(self.repo.url, '.geogit', 'ORIG_HEAD')
        mergeheadfile = os.path.join(self.repo.url, '.geogit', 'MERGE_HEAD')        
        return os.path.exists(headfile) and os.path.exists(mergeheadfile)    
        
    def mergemessage(self):
        msgfile = headfile = os.path.join(self.repo.url, '.geogit', 'MERGE_MSG')
        if os.path.exists(msgfile):
            with open(msgfile) as f:
                lines = f.readlines()
            return "".join(lines)
        else:            
            return "" 
        
    def checkisrepo(self):
        if not os.path.exists(os.path.join(self.repo.url, '.geogit')):
            raise GeoGitException("Not a valid GeoGit repository: " + self.repo.url)
        
    
    def children(self, ref = 'HEAD', path = None, recursive = False):
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
                    children.append(Tree(self.repo, ref, tokens[3]))
        return children   
    
    def commitFromString(self, lines):                
        message = False
        messagetext = None
        parent = None
        commitid = None
        for line in lines:
            tokens = line.split(' ')
            if message:
                if line.startswith("\t") or line.startswith(" "):
                    messagetext = line.strip() if messagetext is None else messagetext + "\n" + line.strip()
                else:
                    message = False            
            else:                
                if tokens[0] == 'commit':
                    commitid = tokens[1]
                if tokens[0] == 'tree':
                    tree = tokens[1]                    
                if tokens[0] == 'parent':
                    if len(tokens) == 2 and tokens[1] != "":
                        parent = tokens[1]                    
                elif tokens[0] == 'author':
                    author = " ".join(tokens[1:-3])
                    authordate = datetime.datetime.fromtimestamp((int(tokens[-2]) - int(tokens[-1]))//1000)                
                elif tokens[0] == 'committer':
                    committer = tokens[1]
                    committerdate = datetime.datetime.fromtimestamp((int(tokens[-2]) - int(tokens[-1]))//1000)
                elif tokens[0] == 'message':
                    message = True                
            
        if commitid is not None:
            c = Commit(self.repo, commitid, tree, parent, messagetext, author, authordate, committer, committerdate)
            return c
        else:
            return None

    def addremote(self, name, url):
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
        
    def log(self, tip, until = None, since = None, path = None, n = None):
        commits = []        
        commands = ['rev-list', tip]        
        if path is not None:
            commands.extend(["-p", path])
        if until is not None:
            commands.extend(["--until", until])
        if since is not None:
            commands.extend(["--since", since])            
        if n is not None:
            commands.extend(["-n", str(n)])            
        try:
            output = self.run(commands)
        except GeoGitException, e:
            if "HEAD does not resolve" in unicode(e, errors = 'ignore'): #empty repo
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
        commands = ["conflicts", "--refspecs-only"]
        lines = self.run(commands)
        _conflicts = {}
        for line in lines:
            if line.startswith("No elements need merging"):
                return {}
            tokens = line.split(" ")
            _conflicts[tokens[0]] = (tokens[1][:40], tokens[2][:40], tokens [3][:40])
        return _conflicts
            
    def solveconflicts(self, paths, version = geogit.OURS):
        commands = ["checkout"]        
        if version == geogit.OURS:
            commands.append("--ours")
        elif version == geogit.THEIRS:
            commands.append("--theirs")
        else:
            raise GeoGitException("Unknown option:" + version)        
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
        self.run(commands)               
             
    def diffentryFromString(self, oldcommitref, newcommitref, line):
        tokens = line.strip().split(" ")
        path = tokens[0]
        oldref = tokens[1]
        newref = tokens[2]
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
    
    def importosm(self, osmfile, add = False, mappingfile = None):
        commands = ["osm", "import", osmfile]        
        if add:
            commands.extend(["--add"])
        if mappingfile is not None:
            commands.extend(["--mapping", mappingfile])
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
        
    def importgeojson(self, geojsonfile, add = False, dest = None, idAttribute = None):
        commands = ["geojson", "import", geojsonfile]
        if dest is not None:
            commands.extend(["--dest", dest])
        if idAttribute is not None:
            commands.extend(["--fid-attrib", idAttribute])            
        if add:
            commands.append("--add")
        self.run(commands)
        
    def importshp(self, shapefile, add = False, dest = None, idAttribute = None):
        commands = ["shp", "import", shapefile]
        if dest is not None:
            commands.extend(["--dest", dest])
        if idAttribute is not None:
            commands.extend(["--fid-attrib", idAttribute])            
        if add:
            commands.append("--add")
        self.run(commands)
    
    def importpg(self, database, user = None, password = None, table = None, 
                 schema = None, host = None, port = None, add = False, dest = None):
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
        if add:
            commands.append("--add")
        self.run(commands)

    def exportpg(self, ref, path, table, database, user, password = None, schema = None, host = None, port = None):
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
        self.run(commands)
        
    def exportshp(self, ref, path, shapefile):
        refandpath = ref + ":" + path
        self.run(["shp", "export", refandpath, shapefile, "-o"])
        
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
        return self.run(["cat", reference])
        
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
        tokens = valuetype.split(" ")        
        try:
            if valuetype == "BOOLEAN":
                return str(value).lower() == "true"
            elif valuetype in ["BYTE","SHORT","INTEGER","LONG"]:
                return int(value)
            elif valuetype in ["FLOAT","DOUBLE"]:
                return float(value)
            elif (valuetype in ["POINT","LINESTRING","POLYGON","MULTIPOINT","MULTILINESTRING","MULTIPOLYGON"] 
                    or len(tokens) == 2):                    
                geom = loads(value)
                if len(tokens) == 2:
                    geom.crs = tokens[1]
                return geom        
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
        except GeoGitException:
            data = None
        try:
            data2 = self.featuredata(ref2, path)
        except GeoGitException:
            data2 = None         
                
        if data is None:
            if data2 is None:
                return {}
            else:
                return {k: (None, v[0]) for k,v in data2.iteritems()}
        elif data2 is None:
            return {k: (v[0], None) for k,v in data.iteritems()}
        
        diffs = {}
        for attr in data:
            if attr in data2:
                v = data[attr][0]
                v2 = data2[attr][0]
                if isinstance(v, BaseGeometry):
                    equal = v.to_wkt() == v2.to_wkt()
                else:
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
    
    def merge (self, ref, nocommit = False, message = None):        
        commands = ["merge", ref]
        if nocommit:
            commands.append("--no-commit")
        elif message is not None:
            commands.append("-m")
            commands.apend(message)
        try:
            self.run(commands) 
        except GeoGitException, e:
            msg = unicode(e, error='ignore')
            if "conflict" in msg:
                raise GeoGitConflictException(msg)
            else:
                raise e

        
    def rebase(self, commitish):
        commands = ["rebase", commitish]
        try:
            self.run(commands) 
        except GeoGitException, e:
            msg = unicode(e, error='ignore')
            if "conflict" in msg:
                raise GeoGitConflictException(msg)
            else:
                raise e
            
    
    def continue_(self):
        if self.isrebasing():
            commands = ["rebase", "--continue"]
            self.run(commands)
            if self.isrebasing():
                raise GeoGitException("Could not continue rebasing")
        elif self.ismerging():
            commands = ["merge", "--continue"]
            self.run(commands)
            if self.ismerging():
                raise GeoGitException("Could not continue merging")
        
    def abort(self):
        if self.isrebasing():
            commands=["rebase", "--abort"]
            self.run(commands)            
        elif self.ismerging():
            self.reset(geogit.HEAD)        
            
    def cherrypick(self, commitish):
        commands = ["cherry-pick", commitish]
        self.run(commands)
    
    def init(self, initParams = None):
        if initParams is None: initParams = {}    
        commands = ["init"]
        for k,v in initParams.iteritems():
            commands.append(k)     
            commands.append(v)
        self.run(commands)
        
    def insertfeatures(self, paths, geoms, attributes):
        trees = defaultdict(list)
        if len(paths) != len(geoms) or len(geoms) != len(attributes):
            raise Exception("The provided lists do not have the same length")
        for path,geom,attrs in zip(paths, geoms, attributes):
            dest = os.path.dirname(path)
            fid = os.path.basename(path)        
            geommap = mapping(geom)            
            trees[dest].append(geojson.Feature(id=fid, geometry=geommap, properties=attrs))
        for tree, features in trees.iteritems():
            fco = geojson.FeatureCollection(features=features)
            json = geojson.dumps(fco)        
            try:
                f = tempfile.NamedTemporaryFile(delete = False)                           
                f.write(json)              
                f.close()
                self.importgeojson(f.name, add = True, dest = tree)            
            finally:
                f.close() 
                try:
                    os.remove(f.name)
                except:
                    pass 
                             
    def removefeature(self, path):
        self.run(["rm", path])
        
    def modifyfeature(self, path, attributes):
        self.removefeature(path)
        self.addfeature(path, attributes)

    def applypatch(self, patchfile):
        self.run(["apply", patchfile])   
        
    def show(self, ref):
        return "\n".join(self.run(["show", ref, "--color", "never"]))    
    
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
        except GeoGitException, e:
            msg = unicode(e, error='ignore')
            if "conflict" in msg:
                raise GeoGitConflictException(msg)
            else:
                raise e

        
    def push(self, remote, branch):
        commands = ["push", remote, branch]        
        self.run(commands)
