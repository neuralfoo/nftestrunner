import dbops 
from loguru import logger
import traceback 
from bson.objectid import ObjectId
import api_controller
import datetime
from collections import defaultdict
import json 

'''
parse request
fetch all test cases
hit api
compare response with expected response
update passed/failed cases
calculate accuracies
'''


if __name__=="__main__":

	import sys

	try:

		testID = sys.argv[1]
		logger.info(f"Received testID {testID}")

		test_details = dbops.get_test(testID)
		logger.info(f"Test object fetched {test_details}")

		request_list = api_controller.extract_requests_from_testboard(test_details["testboard"])
		logger.info(f"Request list generated")

		testboardID = test_details["testboard"]["testboardID"]

		testcases_list = dbops.list_accuracy_testcases(test_details["testboard"]["testboardID"])
		logger.info(f"Testcases received")

		callbacksEnabled = test_details["testboard"]["callbacksEnabled"]

		passed_cases_count = 0
		failed_cases_count = 0

		correct_occurrence = defaultdict(lambda:0)
		total_occurrence = defaultdict(lambda:0)

		average_accuracy = 0

		for testcase in testcases_list:
		
			try:
				api_hit_result = api_controller.accuracy_api_runner(testcase,request_list,callbacksEnabled,testboardID)

			except Exception as e:
				logger.error(e)
				traceback.print_exc()

				api_hit_result = {}
				api_hit_result["testcaseID"] = str(testcase["_id"])
				api_hit_result["result"] = False
				api_hit_result["totalResponseTime"] = 0
				api_hit_result["individualResponseTimes"] = [0]
				api_hit_result["remarks"] = "Error while executing request, fix testcase."
				
				api_hit_result["expectedResponseVariables"] = "{}"
				api_hit_result["receivedResponseVariables"] = "{}"
				# accuracy will be determined based on equality of these two dictionaries
				
				api_hit_result["requestVariables"] = "{}"


				for j in range(1,len(request_list)+1):
					api_hit_result["requestBody"+str(j)] = "{}"
					api_hit_result["responseBody"+str(j)] = "{}"
					api_hit_result["responseCode"+str(j)] = "-"


			api_hit_result["testID"] = testID

			dbops.insert_api_hit(api_hit_result)


			responseVariables = json.loads(api_hit_result["expectedResponseVariables"]) 

			print(responseVariables)

			for key in responseVariables:
				total_occurrence[key] += 1


			if api_hit_result["result"] == True:
				passed_cases_count += 1

				for key in api_hit_result["accuracy_dict"]:

					correct_occurrence[key] += api_hit_result["accuracy_dict"][key]


			if api_hit_result["result"] == False:
				failed_cases_count += 1

			logger.info("api_hit_result")
			logger.info(api_hit_result)

			logger.info(f"Passed test cases: {passed_cases_count}")
			logger.info(f"Failed test cases: {failed_cases_count}")

			dbops.update_test(testID,"passedCasesCount",passed_cases_count)
			dbops.update_test(testID,"failedCasesCount",failed_cases_count)
			
			dbops.update_test(testID,"correctOccurrence",correct_occurrence)
			dbops.update_test(testID,"totalOccurrence",total_occurrence)

			i = 0
			total_acc = 0
			for key in correct_occurrence:

				total_acc += ((correct_occurrence[key]/total_occurrence[key])*100)
				i += 1

			average_accuracy = total_acc/(i+0.00000001)

			dbops.update_test(testID,"averageAccuracy",average_accuracy)


		end_time = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")

		dbops.update_test(testID,"endTime",end_time)

		lastrunon = datetime.datetime.now().strftime("%d %b '%y %H:%M:%S")
		dbops.update_testboard(test_details["testboard"]["testboardID"],"apiLastRunOn",lastrunon)
		
		dbops.update_test(testID,"testStatus","completed")

	except Exception as e:

		traceback.print_exc()
		dbops.update_test(testID,"testStatus","error")


