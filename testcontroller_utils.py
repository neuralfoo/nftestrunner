import os
import utils
import dbops 
import json
import datetime
import traceback
from loguru import logger

def start_accuracy_test(testboardID,userID):
	
	try:
		testboard_snapshot 	= utils.get_snapshot_of_testboard(testboardID)
		start_time 			= datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
		end_time 			= None
		average_accuracy 	= None
		correct_occurrence 	= {}
		total_occurrence 	= {}
		test_status 		= "running"
		test_type 			= "accuracytest"
		num_test_cases 		= len(dbops.list_accuracy_testcases(testboardID))
		machineid 			= os.environ['MACHINE_ID']
		remarks 			= ""
		passed_cases_count 	= 0
		failed_cases_count 	= 0

		testID = dbops.insert_accuracytest(
			userID,testboard_snapshot,
			start_time,end_time,
			num_test_cases,test_type,test_status,
			average_accuracy,correct_occurrence,total_occurrence,
			passed_cases_count,failed_cases_count,
			machineid,remarks)

		retval = os.system(f"pm2 start accuracytest_driver.py --interpreter python3.8 --name {testID} --no-autorestart -- {testID}")

		return True,"Accuracy test started"

	except Exception as e:
		logger.error(e)
		traceback.print_exc()
		return False,str(e)


def start_functional_test(testboardID,userID):
	
	try:		
		testboard_snapshot 	= utils.get_snapshot_of_testboard(testboardID)
		start_time 			= datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
		end_time 			= None
		# accuracy 			= None
		# confusion_matrix 	= None
		passed_cases_count	= 0
		failed_cases_count	= 0
		total_cases_count	= len(dbops.list_functional_testcases(testboardID))
		remarks 			= ""
		test_status 		= "running"
		test_type 			= "functionaltest"

		testID = dbops.insert_functionaltest(
			userID,
			testboard_snapshot,
			start_time,end_time,
			total_cases_count,passed_cases_count,failed_cases_count,
			remarks,test_type,test_status)

		retval = os.system(f"pm2 start functionaltest_driver.py --interpreter python3.8 --name {testID} --no-autorestart -- {testID}")

		return True,"Functional test started"

	except Exception as e:
		logger.error(e)
		traceback.print_exc()
		return False,str(e)



def start_imageclassification_accuracy_test(testboardID,userID):

	try:	
		testboard_snapshot 	= utils.get_snapshot_of_testboard(testboardID)
		start_time 			= datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
		end_time 			= None
		accuracy 			= None
		confusion_matrix 	= None
		test_status 		= "running"
		test_type 			= "imageclassification_accuracytest"
		num_test_images 	= len(dbops.get_images_for_testboard(testboardID))

		testID = dbops.insert_imageclassification_accuracytest(
			userID,
			testboard_snapshot,
			start_time,end_time,num_test_images,
			test_type,test_status,accuracy,confusion_matrix)

		retval = os.system(f"pm2 start imageclassification_accuracy_test_driver.py --interpreter python3.8 --name {testID} --no-autorestart -- {testID}")
		# print(retval)
		return True,"Accuracy test started"

	except Exception as e:
		logger.error(e)
		traceback.print_exc()
		return False,str(e)


def stop_test(testID):

	try:
		retval = os.system(f"pm2 delete {testID}")
		dbops.update_test(testID,"testStatus","stopped")
		return True,"Accuracy test stopped"

	except Exception as e:
		logger.error("Error while stopping test")
		traceback.print_exc()
		return False,"Error while stopping test"



