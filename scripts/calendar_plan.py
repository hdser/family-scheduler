"""Dry run of the calendar sync rules: which calendar entries the board implies.

Usage:
  BOARD_DUMP=db python3 scripts/calendar_plan.py FROM TO [NOW]
  e.g. python3 scripts/calendar_plan.py 2026-10-10 2026-10-18 2026-10-10T12:35

BOARD_DUMP is a folder with events/*.json and routine/*.json (ArtifactData "list"
with out_dir). Names, colours and the board link come from private/family.json
(or FAMILY_CONFIG). The scheduled task (tasks/calendar-sync.md) follows the same rules.
"""
import json,glob,os,datetime as dt,hashlib,sys,pathlib
ROOT=pathlib.Path(__file__).resolve().parent.parent
CFG=json.load(open(os.environ.get('FAMILY_CONFIG',ROOT/'private/family.json')))
D=os.environ.get('BOARD_DUMP','db')
ev={os.path.basename(f)[:-5]:json.load(open(f)) for f in glob.glob(D+'/events/*.json')}
rt={os.path.basename(f)[:-5]:json.load(open(f)) for f in glob.glob(D+'/routine/*.json')}
for k,v in ev.items(): v['id']=k
for k,v in rt.items(): v['id']=k
FROM=dt.date.fromisoformat(sys.argv[1]); TO=dt.date.fromisoformat(sys.argv[2])  # inclusive
TRAIN_TO=FROM+dt.timedelta(days=20)
NOW=dt.datetime.fromisoformat(sys.argv[3]) if len(sys.argv)>3 else dt.datetime.now()
KIDN={k['id']:k['name'] for k in CFG['kids']}; KIDN['both']=CFG['calendar']['family_label']
COLOR={k['id']:k['calendar_color'] for k in CFG['kids']}; COLOR['both']=CFG['calendar']['family_color']
BOARD=CFG['board']['artifact_url']
TZ=CFG['board']['timezone']
def P(s):
    return dt.datetime.fromisoformat(s) if 'T' in s else dt.datetime.fromisoformat(s+'T00:00')
def committed(e):
    return e.get('status')!='tentative' and e.get('attend')!='not' and (not e.get('optional') or e.get('attend')=='going')
items=[]
# dated events
for e in ev.values():
    if e.get('cancelsRoutine') or e.get('overrideRoutine') or e.get('hidden'): continue
    if e.get('status') in ('cancelled','tentative'): continue
    if not committed(e): continue
    s=P(e['start']); timed='T' in e['start']
    if e.get('end'): en=P(e['end']); 
    else: en=None
    if not timed:
        last=(en.date() if en else s.date())
        if last<FROM or s.date()>TO: continue
    else:
        if s.date()<FROM or s.date()>TO: continue
        if en is None: en=s+dt.timedelta(minutes={'match':90,'tournament':300,'training':90,'team':120,'meet':150,'fan':150,'social':120}.get(e.get('kind'),90))
        if en<NOW: continue
    items.append(('ev:'+e['id'],e,'event',s,en,timed))
# routine instances
def routine_day(d):
    dow=d.isoweekday(); ds=d.isoformat().replace('-','')
    out=[]
    marks=[e for e in ev.values() if (e.get('cancelsRoutine') or e.get('overrideRoutine')) and e['start'][:10]==d.isoformat()]
    for r in rt.values():
        if int(r['day'])!=dow: continue
        o=dict(r); o['_s']=P(d.isoformat()+'T'+r['start']); o['_e']=P(d.isoformat()+'T'+r['end'])
        o['_cancel']=any(m.get('cancelsRoutine')==r['id'] for m in marks)
        o['_override']=any(m.get('overrideRoutine')==r['id'] for m in marks)
        out.append(o)
    for o in out:
        if o['_cancel']: continue
        sw=[x for x in out if x.get('yieldsTo')==o['id'] and x['_override'] and not x['_cancel']]
        if sw: o['_cancel']=True; continue
        if o.get('yieldsTo') and not o['_override']:
            w=[x for x in out if x['id']==o['yieldsTo'] and not x['_cancel']]
            if w: o['_cancel']=True
    return [o for o in out if not o['_cancel']]
d=FROM
while d<=min(TO,TRAIN_TO):
    for r in routine_day(d):
        if r['_e']<NOW: continue
        items.append(('r:%s:%s'%(r['id'],d.isoformat()),r,'routine',r['_s'],r['_e'],True))
    d+=dt.timedelta(days=1)
def reminders(kind,start,timed,typ):
    if not timed: return [{'method':'popup','minutes':6*60}]
    if typ=='routine' or kind=='training': return [{'method':'popup','minutes':60}]
    eve=dt.datetime.combine(start.date()-dt.timedelta(days=1),dt.time(19,0))
    return [{'method':'popup','minutes':int((start-eve).total_seconds()//60)},{'method':'popup','minutes':60}]
out=[]
for key,x,typ,s,en,timed in sorted(items,key=lambda i:i[3]):
    kid=x.get('kid','both')
    if typ=='routine':
        title='%s · %s'%(KIDN[kid],x.get('label'))
        start=s; end=en; place=x.get('place',''); kind='training'
        desc=[]
        if x.get('note'): desc.append(x['note'])
    else:
        t=x.get('title'); 
        title='%s · %s'%(KIDN[kid],t)
        kind=x.get('kind'); place=x.get('place','')
        start=s; end=en
        if timed and x.get('meet'):
            m=P(s.date().isoformat()+'T'+x['meet'])
            if m<s: start=m
        desc=[]
        if x.get('meet') and timed: desc.append('Meet (samling): %s · starts %s'%(x['meet'],s.strftime('%H:%M')))
        if x.get('team'): desc.append('Team: '+x['team'])
        if x.get('games'): desc.append('Games: '+'; '.join('%s %s – %s'%(g.get('time',''),g.get('home',''),g.get('away','')) for g in x['games']))
        if x.get('notes'): desc.append(x['notes'])
        if x.get('attend')=='going': desc.append('✓ Going (on the board)')
        if x.get('rsvpUrl'): desc.append('<a href="%s">Answer the club</a>'%x['rsvpUrl'])
        if x.get('sourceUrl') and 'mail.google' in x.get('sourceUrl',''): desc.append('<a href="%s">Original email</a>'%x['sourceUrl'])
    desc.append('<a href="%s">Open the Team Sheet</a>'%BOARD)
    desc.append('<small>[team-sheet:%s]</small>'%key)
    body={'summary':title,'location':place,'description':'<br>'.join(desc),'colorId':COLOR.get(kid,'8'),'availability':'AVAILABILITY_FREE','notificationLevel':'NONE','timeZone':TZ,'overrideReminders':reminders(kind,start,timed,typ)}
    if timed:
        body['startTime']=start.strftime('%Y-%m-%dT%H:%M:%S'); body['endTime']=end.strftime('%Y-%m-%dT%H:%M:%S')
    else:
        last=(en.date() if en else s.date())
        body['allDay']=True; body['startTime']=s.date().isoformat()+'T00:00:00'; body['endTime']=(last+dt.timedelta(days=1)).isoformat()+'T00:00:00'
    h=hashlib.sha1(json.dumps(body,sort_keys=True,ensure_ascii=False).encode()).hexdigest()[:12]
    out.append({'key':key,'hash':h,'body':body})
json.dump(out,open(os.environ.get('PLAN_OUT','calendar_plan.json'),'w'),ensure_ascii=False,indent=1)
for o in out: b=o['body'];print(o['key'].ljust(34),b['startTime'][:16],b.get('endTime','')[11:16],b['summary'],'|',b['location'][:25],'|',[r['minutes'] for r in b['overrideReminders']])
