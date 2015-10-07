import tempfile, BaseHTTPServer, cgi, os, shutil, SocketServer, time, os
import Queue, threading, csv, sys, itertools, re, glob, dateutil.parser
import ast

p = '.'
if p not in sys.path:
    sys.path.append(p)

import sheet, boes
reload(sheet); reload(boes)

logdirpath = './logs'
if not os.path.isdir(logdirpath):
    os.mkdir(logdirpath)
logname = os.path.join(logdirpath, 'nys-%s.log' % time.ctime().replace(' ', '-'))
logfile = open(logname, 'w')
logqueue = Queue.Queue()
def logwork():
    while True:
        logitem = logqueue.get()
        print >> logfile, logitem
        logfile.flush()
        logqueue.task_done()
# Commit a single thread to logging, so log entries don't overwrite.
logthread = threading.Thread(target=logwork)
logthread.start()
def log(s):
    logqueue.put('%s %s' % (time.ctime(), str(s)))

# Parse the  old logs, to get  the list of processed  voters.  This is
# starting to get ugly.  Probably time to move to a real DB.
processed_voters = set()
for p in glob.glob('logs/*.log'):
    for line in open(p):
        line = line.split()
        try:
            dateutil.parser.parse(' '.join(line[:5]))
        except ValueError:
            raise RuntimeError, 'Failed to parse log line "%s" in file %s' % (line, p)
        logdata = ast.literal_eval(' '.join(line[5:]))
        if logdata[1] in ('FLIERS', 'FACEBOOK'):
            processed_voters.update(set(logdata[-1]))

for line in open('processed.txt'):
    if not line.strip().startswith('#'):
        line = line.split()[0]
        assert re.match('NY\d{18}', line)
        processed_voters.add(line)
        
print '%i voters have already been processed and will be ignored' % len(processed_voters)

field_names = ['LASTNAME', 'FIRSTNAME', 'MIDDLENAME', 'NAMESUFFIX', 'RADDNUMBER', 'RHALFCODE', 'RAPARTMENT', 'RPREDIRECTION', 'RSTREETNAME', 'RPOSTDIRECTION', 'RCITY', 'RZIP5', 'RZIP4', 'MAILADD1', 'MAILADD2', 'MAILADD3', 'MAILADD4', 'DOB', 'GENDER', 'ENROLLMENT', 'OTHERPARTY', 'COUNTYCODE', 'ED', 'LD', 'TOWNCITY', 'WARD', 'CD', 'SD', 'AD', 'LASTVOTEDDATE', 'PREVYEARVOTED', 'PREVCOUNTY', 'PREVADDRESS', 'PREVNAME', 'COUNTYVRNUMBER', 'REGDATE', 'VRSOURCE', 'IDREQUIRED', 'IDMET', 'STATUS', 'REASONCODE', 'INACT_DATE', 'PURGE_DATE', 'SBOEID', 'VoterHistory']

#Database accessor.
database_path = 'targeted_voters_sorted.csv'
def _voterstream(loop=True):
    while True:
        vdb = csv.DictReader(open(database_path),
                             fieldnames=field_names)
        for row in vdb:
            if row['SBOEID'] not in processed_voters:
                yield row
        if not loop:
            break

def voter(csventry):
    csventry['fname'] = csventry['FIRSTNAME'].title()
    csventry['lname'] = csventry['LASTNAME'].title()
    # First get the residential address
    csventry['street'] = ' '.join(
        csventry[n].title() for n in 'RADDNUMBER RHALFCODE RPREDIRECTION RSTREETNAME RPOSTDIRECTION'.split())
    if csventry['RAPARTMENT']:
        csventry['street'] += ' Apt ' + csventry['RAPARTMENT']
    csventry['city'] = csventry['RCITY'].title()
    csventry['state'] = 'NY' # Has to be, I guess?  No state column in db.
    csventry['zip'] = csventry['RZIP5'] + ( '-' + csventry['RZIP4'] if csventry['RZIP4'] else '')
    if csventry['MAILADD1']:
        # OK, there's also a mailing address.  Use that instead.
        addr = filter(None, [csventry['MAILADD%i' % i] for i in range(1, 5)])
        csventry['freeaddr'] = addr
    csventry['boe'] = boes.boes[int(csventry['COUNTYCODE'])-1]
    return csventry

full_voterstream = itertools.imap(voter, _voterstream())
unique_names = set(map(tuple, csv.reader(open(('unique_at_risk_names.txt')))))
def unique_p(v):
    return (v['LASTNAME'], v['FIRSTNAME']) in unique_names
unique_voterstream = itertools.ifilter(unique_p, full_voterstream)

# Get the landing page
form = open('form.html').read()

class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        facebook_targets = []
        vids = []
        template = '<tr><td>%s %s</td><td>%s</td></tr>\n' 
        for voter in itertools.islice(unique_voterstream, 12):
            vinfo = (voter['fname'], voter['lname'], voter['boe']['fname'].replace(' County Board of Elections', ''))
            vids.append(voter['SBOEID'])
            facebook_targets.append(template % vinfo)
        facebook_list = '<table border="1" style="border-collapse: separate; border-spacing: 0.25em;">\n<tr><th>Name</th><th>County</th></tr>\n%s</table>'
        facebook_list %= ''.join(facebook_targets)
        self.wfile.write(form.replace('facebanking_names_go_here', facebook_list))
        log((self.client_address[0], 'FACEBOOK', vids))

def test_generation():
    numfliers = 100
    fromaddr = sheet.myaddr
    toaddrs = list(itertools.islice(
        # must be a generator expression, as voterstream is infinite!
        (v for v in voterstream if 'freeaddr' in v),
        numfliers))
    doc = sheet.makedoc('/tmp/tst.pdf')
    pages = list(itertools.chain(*(
        sheet.addrsheet(fromaddr, toaddr, toaddr['boe'])
        for toaddr in toaddrs)))
    doc.build(pages)
    
class ThreadedHTTPServer(SocketServer.ThreadingMixIn, 
                         BaseHTTPServer.HTTPServer):
    """Handle requests in a separate thread."""

if __name__ == '__main__':
    BaseHTTPServer.test(HandlerClass=RequestHandler,
                        ServerClass=ThreadedHTTPServer
                        )
