# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html

from icalendar import Calendar, Event, vDatetime
from datetime import datetime, time, date, timedelta, tzinfo
import os

def display(cal):
	return cal.as_string().replace('\r\n','\n').strip()
class SGT(tzinfo):
	def utcoffset(self,dt):
		return timedelta(hours=8)
	def tzname(self,dt):
		return "SGT"
	def dst(self,dt):
		return timedelta(0)

SEM_START = datetime(2012,1,9,0,0,tzinfo=SGT())
RECESS_WEEK = 7
TOTAL_WEEKS = 14
WEEK2ACTUAL=[1,2,3,4,5,6,8,9,10,11,12,13,14]
WEEKDAY=['MO','TU','WE','TH','FR','SA','SU']

week = timedelta(days=7)
day = timedelta(days=1)
hour = timedelta(hours=1)
minute = timedelta(minutes=1)

_,startweek,_ = SEM_START.isocalendar()




class CorsPipeline(object):
	def process_item(self, item, spider):
		cal = Calendar()
		cal.add('calscale','GREGORIAN')
		cal.add('version','2.0')
		cal['method'] = 'PUBLISH'
		cal['x-wr-calname'] = item['code']
		cal['x-wr-caldesc'] = '%s : \\r\\n%s' % (item['name'],item['desc'])
		if item['exam'] != 'null':
			exam = Event()
			exam.add('summary', '%s exam %s'%(item['code'],item['exam']['time']))
			starttime = datetime.combine(
					item['exam']['date'], time() 
					if item['exam']['time']=='AM'
					else time(12,0)
			).replace(tzinfo=SGT())

			setstartend(
				exam,
				starttime,
				starttime + 12*hour
			)	
			cal.add_component(exam)

		if item['lecture_time_table'] != 'null':
			for l in item['lecture_time_table']:
				for lec in l['sessions']:
					dow = lec['day']
					ts = int(lec['starttime'])
					te = int(lec['endtime'])
					ts_hr,ts_min = ts/100, ts%100
					te_hr,te_min = te/100, te%100
					
					combstr = ','.join([str(WEEK2ACTUAL[i-1]+startweek-1) for i in lec['occurence']])

					lectureday = SEM_START + (dow-1)*day 
					lecture = Event()
					lecture.add('summary', '%s %s'%(item['code'],l['name']))
					setstartend(lecture,
							lectureday + ts_hr*hour + ts_min*minute,
							lectureday + te_hr*hour + te_min*minute)
					lecture['rrule'] = 'FREQ=YEARLY;BYWEEKNO=%s;BYDAY=%s' % (combstr,WEEKDAY[lec['day']-1])
					lecture['location'] = lec['location']
					cal.add_component(lecture)

		if item['tutorial_time_table'] != 'null':
			for t in item['tutorial_time_table']:
				for tut in t['sessions']:
					dow = tut['day']
					ts = int(tut['starttime'])
					te = int(tut['endtime'])
					ts_hr,ts_min = ts/100, ts%100
					te_hr,te_min = te/100, te%100

					combstr = ','.join([str(WEEK2ACTUAL[i-1]+startweek-1) for i in tut['occurence'] if i!=1 ]) #precautionary check

					tutday = SEM_START + (dow-1)*day + (WEEK2ACTUAL[
						(tut['occurence'][0] if tut['occurence'][0] != 1 else tut['occurence'][1]) - 1 #another stupid check, tutorials really shouldn't start on 1st week.
					]-1)*week
					tutorial = Event()
					tutorial.add('summary', '%s %s' % (item['code'],t['name']))
					setstartend(tutorial,
							tutday + ts_hr*hour + ts_min*minute,
							tutday + te_hr*hour + te_min*minute)
					tutorial['rrule'] = 'FREQ=YEARLY;BYWEEKNO=%s;BYDAY=%s' % (combstr,WEEKDAY[tut['day']-1])
					tutorial['location'] = tut['location']
					cal.add_component(tutorial)

		f = open(os.path.join('ics',('%s.ics'%item['code'].split()[0])),'wb')
		f.write(cal.as_string())
		f.close()
		return item
def setstartend(event,start,end):
	event['dtstart'] = vDatetime(start).ical()
	event['dtend'] = vDatetime(end).ical()
	event['dtstamp'] = vDatetime(datetime.now()).ical()
	#event['uid'] = '%s/shawn@wtf.sg'%vDatetime(datetime.now()).ical()
	event['sequence'] = 0

