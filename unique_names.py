import csv

field_names = ['LASTNAME', 'FIRSTNAME', 'MIDDLENAME', 'NAMESUFFIX', 'RADDNUMBER', 'RHALFCODE', 'RAPARTMENT', 'RPREDIRECTION', 'RSTREETNAME', 'RPOSTDIRECTION', 'RCITY', 'RZIP5', 'RZIP4', 'MAILADD1', 'MAILADD2', 'MAILADD3', 'MAILADD4', 'DOB', 'GENDER', 'ENROLLMENT', 'OTHERPARTY', 'COUNTYCODE', 'ED', 'LD', 'TOWNCITY', 'WARD', 'CD', 'SD', 'AD', 'LASTVOTEDDATE', 'PREVYEARVOTED', 'PREVCOUNTY', 'PREVADDRESS', 'PREVNAME', 'COUNTYVRNUMBER', 'REGDATE', 'VRSOURCE', 'IDREQUIRED', 'IDMET', 'STATUS', 'REASONCODE', 'INACT_DATE', 'PURGE_DATE', 'SBOEID', 'VoterHistory']

f = csv.DictReader(open('/play/coventry/bernie/AllNYSVoters.txt'), fieldnames=field_names)

names = ddict(int)

for count, line in enumerate(f):
    if (line['STATUS'] in ('PREREG', 'ACTIVE')) and (line['ENROLLMENT'] not in ('REP', 'DEM')) and (line['ENROLLMENT'] in ('GRE', 'WOR')):
        names[(line['LASTNAME'], line['FIRSTNAME'])] += 1
    if count % 10000 == 0:
        print count

print sum(c for n, c in names.items() if c == 1)
        
