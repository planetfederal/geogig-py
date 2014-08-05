import json

class OSMMappingRule(object):
           
    def __init__(self, name):
        self.name = name
        self.fields = {}
        self.filter = {}
        self.exclude = {}
    
    def addfield(self, tagname, fieldname, fieldtype):
        d = {"name" : fieldname, "type" : fieldtype}
        self.fields[tagname] = d
        
    def addfilter(self, name, *tags):
        self.filter[name] = tags
        
    def addexclusion(self, name, *tags):
        self.filter[name] = tags
        
    def asjson(self):        
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True)
    
    
class OSMMapping(object):        
    
    def __init__(self):
        self.rules = []
        
    def addrule(self, rule):    
        self.rules.append(rule)
        
    def asjson(self):
        return json.dumps(self, default=lambda o: o.__dict__,sort_keys=True)

  