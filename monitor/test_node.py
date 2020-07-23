import sys
import os
import subprocess
import time
import requests
import shutil

resume_count = 0
waiting_time = 0
sleep_time = 0

# Error codes
connection_error = 111
http_error = 404
fail= 500
success = 200
other_exception = 300


def check_storage():
	print("\nGetting memory usage...")
	total, used, free = shutil.disk_usage("/")

	total_memory = (total // (2**30))
	used_memory = (used // (2**30))
	free_memory = (free // (2**30))

	print("Total: %d GiB" % total_memory)
	print("Used: %d GiB" % used_memory)
	print("Free: %d GiB" % free_memory)

	if free_memory > 5:
		return success
	print("Memory is filled...")
	return fail


def get_node_status(api_url, total_node):
	try:
		print("\nGetting grafana api response")
		response = requests.get(api_url)
		response_data = response.json()
		# print(response_data)
		result_array = response_data["data"]["result"]
		print("\nResponse length: %d" % len(result_array))
		if (len(result_array)) != total_node:
			print("\nStopping.....")
			subprocess.call(["./stop.sh"])
			time.sleep(sleep_time)
			global resume_count
			if resume_count < 2:
				print("\nResuming.......")
				subprocess.call(["./resume.sh"])
				resume_count = resume_count+1
				time.sleep(waiting_time)
				return success
			else:
				resume_count = 0
				return fail
		return success
	except requests.exceptions.ConnectionError as conn_err:
		print("Connection error", conn_err)
		resume_count = 0
		return connection_error
	except requests.exceptions.HTTPError as http_err:
		print("Http Error:", http_err)
		return http_error
	except Exception as exception:
		print("Exception:", exception)
		return other_exception


def run_script(api_url, total_node):

	while True:
		storage_status = check_storage()
		node_status = get_node_status(api_url, total_node)
		if storage_status == fail or node_status == fail or node_status == connection_error:
			print("\nRemoving.......\n")
			subprocess.call(["./remove.sh"])
			time.sleep(sleep_time)
			print("\nReinstalling......\n")
			subprocess.call(["./run-privacy.sh"])
			time.sleep(waiting_time)
		elif node_status == http_error or node_status == other_exception:
			print("Terminating the program")
			break
		time.sleep(sleep_time)


if __name__ == "__main__":

	# Passing arg from command line:
	# Command to run: python3 test_node.py /root/besu/besu-sample-networks/ 0 180 10 6
	# First arg: location
	# Second arg: resume_count
	# Third arg: waiting_time
	# Fourth arg: sleep_time
	# Fifth arg: total_nodes

	directory_location = sys.argv[1]
	resume_count = int(sys.argv[2])
	waiting_time = int(sys.argv[3])
	sleep_time = int(sys.argv[4])
	total_nodes = int(sys.argv[5])
	url = "http://localhost:3000/api/datasources/proxy/1/api/v1/query?query=sum%20by%20(instance)%20(ethereum_blockchain_height%7Binstance%3D~%22bootnode%3A9545%7Cminernode%3A9545%7Cnode1%3A9545%7Cnode2%3A9545%7Cnode3%3A9545%7Crpcnode%3A9545%22%7D)"

	os.chdir(directory_location)

	run_script(url, total_nodes)
