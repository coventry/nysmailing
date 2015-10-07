import csv, server
reload(server)

def get_names():
    field_names = ['LASTNAME', 'FIRSTNAME', 'MIDDLENAME', 'NAMESUFFIX', 'RADDNUMBER', 'RHALFCODE', 'RAPARTMENT', 'RPREDIRECTION', 'RSTREETNAME', 'RPOSTDIRECTION', 'RCITY', 'RZIP5', 'RZIP4', 'MAILADD1', 'MAILADD2', 'MAILADD3', 'MAILADD4', 'DOB', 'GENDER', 'ENROLLMENT', 'OTHERPARTY', 'COUNTYCODE', 'ED', 'LD', 'TOWNCITY', 'WARD', 'CD', 'SD', 'AD', 'LASTVOTEDDATE', 'PREVYEARVOTED', 'PREVCOUNTY', 'PREVADDRESS', 'PREVNAME', 'COUNTYVRNUMBER', 'REGDATE', 'VRSOURCE', 'IDREQUIRED', 'IDMET', 'STATUS', 'REASONCODE', 'INACT_DATE', 'PURGE_DATE', 'SBOEID', 'VoterHistory']

    f = csv.DictReader(open('/play/coventry/bernie/AllNYSVoters.txt'), fieldnames=field_names)

    names = [ddict(int)]

    atrisk = [set()]
    for count, line in enumerate(f):
        nametuple = (line['LASTNAME'], line['FIRSTNAME'])
        names[-1][nametuple] += 1
        if (line['STATUS'] in ('PREREG', 'ACTIVE')) and (line['ENROLLMENT'] not in ('REP', 'DEM')):
            atrisk[-1].add(nametuple)
        if count % 100000 == 0:
            print count, len([v for v,c in names[-1].items() if v in atrisk[-1] and c == 1])
            names.append(ddict(int))
            atrisk.append(set())
    allatrisk = set()
    for atrisk_ in atrisk:
        allatrisk.update(atrisk_)
    allnames = ddict(int)
    for names_, atrisk_ in zip(names, atrisk):
        print len(allnames), len([v for v,c in allnames.items() if c == 1 and v in allatrisk])
        for name, count in names_.items():
            allnames[name] += count

def count_all_names(names, atrisk):
    # Save a list of actually unique names here:
    output = open('~/bernie/outreach/nys/unique_names.txt', 'w')
    for i, names_ in enumerate(names):
        if not names_:
            continue
        pruned = set()
        unique_here = set(n for n, c in names_.items() if c == 1 and n in atrisk)
        for j, names2 in list(enumerate(names)):
            if j == i: continue
            print i, j
            unique_here = unique_here.difference(set(names2))
        print >> output, '\n'.join('"%s","%s"' % n for n in unique_here)
        print len(unique_here)

def count_names():
    # Save a list of at-risk unique names
    vcount = count = 0
    seen = set()
    for v in server.voterstream:
        nametuple = (v['LASTNAME'], v['FIRSTNAME'])
        if nametuple in server.unique_names:
            vcount += 1
            assert nametuple not in seen
            seen.add(nametuple)
        if count % 100000 == 0:
            print count, vcount, (v['LASTNAME'], v['FIRSTNAME'])
        count += 1
    print >> open('~/bernie/outreach/nys/nysmailing/unique_at_risk_names.txt', 'w'), '\n'.join('"%s","%s"' % n for n in seen)

count_names()
