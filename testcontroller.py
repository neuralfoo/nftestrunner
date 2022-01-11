import utils
import traceback 
from loguru import logger
from bson.objectid import ObjectId
from flask import Blueprint,request
import testcontroller_utils as functions
import global_vars as g

profile = Blueprint('testcontroller', __name__)


@profile.route(g.start_test_url,methods=["POST"])
def testcontroller_start():

    endpoint = g.start_test_url

    try:

        #### request authentication ####
        userID,organizationID = utils.authenticate(request.headers.get('Authorization'))
        if userID is None:
            logger.error("Invalid auth token sent for"+endpoint)
            return utils.return_401_error("Session expired. Please login again.")


        #### request body sanity checks ####
        data = request.json
        
        if utils.check_params(
            ["testboardID","testType"],[str,str],data) == False:
            message = "Invalid params sent in request body for "+endpoint
            logger.error(message+":"+str(data))
            return utils.return_400_error(message)


        #### sanity checks completed and we can now proceed to run accuracy test ####

        testType = data["testType"]
        testboardID = data["testboardID"]


        access_granted,msg = utils.check_permissions("testboards",ObjectId(testboardID),userID)
        if not access_granted:
            logger.error(f"Invalid access rights for {endpoint} by {userID}")
            return utils.return_403_error("You do not have access priviliges for this page.")


        logger.info(f"Test controller START {testType} attempt by user {userID}: "+str(data) )


        result,msg = None,None

        if testType == "accuracytest":
            result,msg = functions.start_accuracy_test(testboardID,userID)

        if testType == "functionaltest":
            result,msg = functions.start_functional_test(testboardID,userID)
        
        if testType == "imageclassification_accuracytest":
            result,msg = functions.start_imageclassification_accuracy_test(testboardID,userID)

        if result == False:
            message = "Unexpected error occurred."
            return utils.return_400_error(message)

        logger.info(f"{testType} test successfully started")

        return utils.return_200_response({"message":msg,"status":200})
    

    except Exception as e:

        message = "Unexpected error"
        logger.error(message+":"+str(e))
        traceback.print_exc()

        return utils.return_400_error(message)



@profile.route(g.stop_test_url,methods=["POST"])
def testcontroller_stop():

    endpoint = g.stop_test_url

    try:

        #### request authentication ####
        userID,organizationID = utils.authenticate(request.headers.get('Authorization'))
        if userID is None:
            logger.error("Invalid auth token sent for"+endpoint)
            return utils.return_401_error("Session expired. Please login again.")


        #### request body sanity checks ####
        data = request.json
        
        if utils.check_params(
            ["testboardID","testID"],[str,str],data) == False:
            message = "Invalid params sent in request body for "+endpoint
            logger.error(message+":"+str(data))
            return utils.return_400_error(message)


        #### sanity checks completed and we can now proceed to run accuracy test ####

        testID = data["testID"]
        testboardID = data["testboardID"]


        access_granted,msg = utils.check_permissions("testboards",ObjectId(testboardID),userID)
        if not access_granted:
            logger.error(f"Invalid access rights for {endpoint} by {userID}")
            return utils.return_403_error("You do not have access priviliges for this page.")


        logger.info(f"Test controller STOP attempt by user {userID}: "+str(data) )
        
        result,msg = functions.stop_test(testID)
        
        if result == False:
            message = "Unexpected error occurred."
            return utils.return_400_error(message)

        logger.info(f"Test {testID} successfully stopped")

        return utils.return_200_response({"message":msg,"status":200})
    

    except Exception as e:

        message = "Unexpected error"
        logger.error(message+":"+str(e))
        traceback.print_exc()

        return utils.return_400_error(message)


