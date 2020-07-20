import subprocess
import os
import requests
import time

# stores besu-sample-networks folder location.
directoryLocation = "../../../Documents/besu-sample-networks/"


# stores grafana api url
url = "http://localhost:3000/api/datasources/proxy/1/api/v1/query?query=sum%20by%20(instance)%20(ethereum_blockchain_height%7Binstance%3D~%22bootnode%3A9545%7Cminernode%3A9545%7Cnode1%3A9545%7Cnode2%3A9545%7Cnode3%3A9545%7Crpcnode%3A9545%22%7D)"

# Count to store how many times container is tried to resume. If count exceeds 2 times then the container is removed 
# and it is reinstalled again.
resumeCount =0

# waiting time for grafana to start.
waitingTime = 180


# interval time between two process
sleepTime =10

# command to navigate to desired location
os.chdir(directoryLocation)

while (True):
	print("Getting api status..... \n")
	try:
		response = requests.get(url)
		responseData = response.json()
		print(responseData)
		resultArray = responseData["data"]["result"]
		print(len(resultArray))
		if len(resultArray)!=6:
			print("\nStopping.....")
			# remove first parameter sudo if docker does not need sudo to perform
			subprocess.call(["sudo","./stop.sh"])
			time.sleep(sleepTime)
			if resumeCount<2:
				print("\nResuming.......")
				# remove first parameter sudo if docker does not need sudo to perform
				subprocess.call(["sudo","./resume.sh"])
				resumeCount = resumeCount+1
				time.sleep(waitingTime)
	except:
		resumeCount=0
		print("\nRemoving.......\n")
		# remove first parameter sudo if docker does not need sudo to perform
		subprocess.call(["sudo","./remove.sh"])
		time.sleep(sleepTime)
		print("\nReinstalling......\n")
		# remove first parameter sudo if docker does not need sudo to perform
		subprocess.call(["sudo","./run-privacy.sh"])
		time.sleep(waitingTime)

	time.sleep(sleepTime)
	
