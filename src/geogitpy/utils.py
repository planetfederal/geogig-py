import os
import datetime

def mkdir(newdir):
    newdir = newdir.strip('\n\r ')
    if os.path.isdir(newdir):
        pass
    else:
        (head, tail) = os.path.split(newdir)
        if head and not os.path.isdir(head):
            mkdir(head)
        if tail:
            os.mkdir(newdir)

def prettydate(d):
    diff = datetime.datetime.now() - d
    s = ''
    secs = diff.seconds
    if diff.days == 1:
        s = "1 day ago"
    elif diff.days > 1:
        s = "{} days ago".format(diff.days)
    elif secs < 120:
        s = "1 minute ago"
    elif secs < 3600:
        s = "{} minutes ago".format(secs/60)
    elif secs < 7200:
        s = "1 hour ago"
    else:
        s = '{} hours ago'.format(secs/3600)
    
    s += d.strftime(' [%x %H:%M]')
    return s 