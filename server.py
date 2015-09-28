import tempfile, BaseHTTPServer, cgi, os, shutil, SocketServer, time
import Queue, threading, csv, sys, itertools, re

p = '.'
if p not in sys.path:
    sys.path.append(p)

import sheet, boes
reload(sheet); reload(boes)

field_names = ['LASTNAME', 'FIRSTNAME', 'MIDDLENAME', 'NAMESUFFIX', 'RADDNUMBER', 'RHALFCODE', 'RAPARTMENT', 'RPREDIRECTION', 'RSTREETNAME', 'RPOSTDIRECTION', 'RCITY', 'RZIP5', 'RZIP4', 'MAILADD1', 'MAILADD2', 'MAILADD3', 'MAILADD4', 'DOB', 'GENDER', 'ENROLLMENT', 'OTHERPARTY', 'COUNTYCODE', 'ED', 'LD', 'TOWNCITY', 'WARD', 'CD', 'SD', 'AD', 'LASTVOTEDDATE', 'PREVYEARVOTED', 'PREVCOUNTY', 'PREVADDRESS', 'PREVNAME', 'COUNTYVRNUMBER', 'REGDATE', 'VRSOURCE', 'IDREQUIRED', 'IDMET', 'STATUS', 'REASONCODE', 'INACT_DATE', 'PURGE_DATE', 'SBOEID', 'VoterHistory']

#Database accessor.
database_path = 'targeted_voters_sorted.csv'
def _voterstream():
    while True:
        vdb = csv.DictReader(open(database_path),
                             fieldnames=field_names)
        for row in vdb:
            yield row

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

voterstream = itertools.imap(voter, _voterstream())

logname = '~/nys-%s.log' % time.ctime().replace(' ', '-')
logname = os.path.expanduser(logname)
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

form = open('form.html').read()

class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(form)
        log((self.client_address[0],))

    def do_POST(self):
        ctype, pdict = cgi.parse_header(self.headers.getheader(
            'content-type'))
        if ctype == 'multipart/form-data':
            postvars = cgi.parse_multipart(self.rfile, pdict)
        elif ctype == 'application/x-www-form-urlencoded':
            length = int(self.headers.getheader('content-length'))
            postvars = cgi.parse_qs(self.rfile.read(length), 
                                    keep_blank_values=1)
        else:
            postvars = {}
        postvars = dict((n, ' '.join(v)) for n, v in postvars.items())
        if 'singlesided' in postvars:
            maxpages = 100
            include_rego = False
        else:
            maxpages = 3
            include_rego = True
        self.send_response(200)
        self.send_header('Content-type', 'application/pdf')
        self.end_headers()
        fromaddr = postvars
        numfliers = min(maxpages, int(postvars['numfliers']))
        toaddrs = list(itertools.islice(voterstream, numfliers))
        log((self.client_address[0], fromaddr, [a['SBOEID'] for a in toaddrs]))
        doc = sheet.makedoc(self.wfile)
        pages = list(itertools.chain(*(
            sheet.addrsheet(fromaddr, toaddr, toaddr['boe'], include_rego)
            for toaddr in toaddrs)))
        doc.build(pages)

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
                        # ServerClass=ThreadedHTTPServer
                        )
