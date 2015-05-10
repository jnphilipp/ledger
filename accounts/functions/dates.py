from dateutil.relativedelta import relativedelta
from itertools import count

def daterange(start, end, execution=1):
	if execution == 1:
		step = 1
	elif execution == 2:
		step = 3
	elif execution == 3:
		step = 6
	elif execution == 4:
		step = 12
	else:
		step = execution

	c = start
	dates = []
	for i in count(step=step):
		if c == end:
			break;
		c = start + relativedelta(months=+i)
		dates.append(c)
	return dates