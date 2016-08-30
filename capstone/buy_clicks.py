import global_vars
import random
import numpy as np
import datetime
import os

def writeBuyClicksCSV(startTime, dayDuration):
	#get users who are playing and their buying probabilities
	teamAssignments = global_vars.globalTeamAssignments
	userSessions	= global_vars.globalUSessions
	assignmentsList = global_vars.globalTeamAssignments
	totalUsers 		= []
	buyProbabilities = []

	#numberOfItems = 30

	# price distributions for each platform
	platformBuyPriceDist = { 
		'iphone': [0, .05, .05, .15, .30, .45],
		'mac': [.10, .50, .15, .10, .10, .05],
		#'mac': [.05, .05, .15, .50, .15, .10],
		'android' : [.10, .10, .60, .10, .05, .05 ],
		'windows': [ .70, .10, .10, .05, .03, .02 ],
		'linux': [.90, .05, .02, .01, .01, .01] 
    }

	buyPrices = [1.00, 2.00, 3.00, 5.00, 10.00, 20.00]
	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~GENERATE buy database if global variable is None
	if(global_vars.buyDatabase is None):
		# NOTE: if you change the number of elements in buyPrices,
		# need to change all the distributions in platformBuyPriceDist.
		#pickCategories=np.random.choice(buyPrices, numberOfItems)
		buyDatabase = zip(range(0,len(buyPrices)), buyPrices) #each member is a tuple (buyID, category)
		global_vars.buyDatabase = buyDatabase
	else:
		buyDatabase = global_vars.buyDatabase

	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~GET list1= (teamid,userid) list2=buyfactor for each user currently playing

	addition = 0
	for s in userSessions:
		#GET ASSIGNMENT FOR THIS SESSION
		for assgn in assignmentsList:
			if(assgn['assignmentid'] == s['assignmentid']):
				teamid = assgn['teamid']
				userid = assgn['userid']
		buyfactor = global_vars.globalUsers[userid]['tags']['purchbeh']
		totalUsers.append((teamid, userid, s['userSessionid'], s['platformType'])) #list
		buyProbabilities.append(buyfactor) #list
		addition += buyfactor

	buyProbabilities = [x/addition for x in buyProbabilities]

	#pick 0-1% users for clicking based on their click probabilities
	factor = random.uniform(0, 0.01)

	if len(totalUsers) <= 0:
		return

	#print factor
	buyUsers = np.random.choice(range(0, len(totalUsers)), int(factor*len(totalUsers)), replace=True, p=buyProbabilities).tolist()
	buyclicks = []

	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~GENERATE buyclicks from these users
	for indx in buyUsers:
		buyEvent = {}
		buyEvent['txid'] = global_vars.counter
		global_vars.counter += 1

		buyEvent['timeStamp'] = startTime + datetime.timedelta(hours=random.uniform(0, dayDuration.seconds // 3600))
		buyEvent['teamid'] = totalUsers[indx][0]
		buyEvent['userid'] = totalUsers[indx][1]
		buyEvent['userSessionid'] = totalUsers[indx][2]
		platform = totalUsers[indx][3]
		pickABuy = np.random.choice(len(buyPrices), 1, p=platformBuyPriceDist[platform])[0]
		#if platform == 'linux':
		#	print pickABuy, buyDatabase[pickABuy][1], buyDatabase
		buyEvent['buyID'] = buyDatabase[pickABuy][0]
		buyEvent['buyPrice'] = buyDatabase[pickABuy][1]
		buyclicks.append(buyEvent)
		#print '%s %s' % (platform, buyEvent['buyPrice'])

		# increase accuracy based on price of item bought
		accuracy = global_vars.globalUsers[buyEvent['userid']]['tags']['gameaccuracy'] + buyEvent['buyPrice']/1000
		# see if accuracy too high
		if accuracy > global_vars.max_accuracy:
			accuracy = global_vars .max_accuracy
		global_vars.globalUsers[buyEvent['userid']]['tags']['gameaccuracy'] = accuracy

		#print 'userid %s accuracy %s price %f' % (buyEvent['userid'],
			#global_vars.globalUsers[buyEvent['userid']]['tags']['gameaccuracy'], buyEvent['buyPrice'])



	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~APPEND to file
	for b in sorted(buyclicks, key=lambda a: a['timeStamp']):
		global_vars.buy_clicks.write("%s,%s,%s,%s,%s,%s,%s\n" %
			(b['timeStamp'].strftime(global_vars.timestamp_format), b['txid'], b['userSessionid'],
			b['teamid'], b['userid'], b['buyID'], b['buyPrice']))
	#buyLog.close()
