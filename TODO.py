import sys
import os
import gitlab

'''
PARAM1: Gitlab Host
PARAM2: job_token
PARAM3: Project ID
PARAM4: Project Directory
'''

class file_to_scrape:
  def __init__(self, name, path):
    self.name = name
    self.path = path
    self.todo_lines = []

if len(sys.argv) != 5:
	sys.exit("Missing parameters:\n"
	"	PARAM1: Gitlab Host\n"
	"	PARAM2: job_token\n"
	"	PARAM3: Project ID\n"
	"	PARAM4: Project Directory\n")


host = sys.argv[1]
proj_job_token = sys.argv[2]
proj_ID = sys.argv[3]
files_found = []

directory = sys.argv[4]
if not os.path.isdir(directory):
	sys.exit("Directory is not accessible or is not a directory")


# Find all python files
for root, _, files in os.walk(directory, topdown=False):
	for filename in files:
		file_path = os.path.join(root, filename)
		# TODO support more than python files
		if os.path.isfile(file_path) and file_path.endswith('.py'):
			file = file_to_scrape(filename, file_path)
			files_found.append(file)

# Create a list of lines containing # TODO
# TODO Add try around here encase the file is not ASCII
for file in files_found:
	for line in open(file.path, "rt"):
		if "# TODO" in line or "#TODO" in line:
			file.todo_lines.append(line.strip())
# Display todo_lines
for file in files_found:
		print(file.name)
		for line in file.todo_lines:
			print("	", line)
		
# Connect to gitlab
git = gitlab.Gitlab(host, job_token = proj_job_token, ssl_verify=False)
if not git:
    sys.exit("Failed to connect")

# Display all projects
projects = git.projects.list()
for project in projects:
    print(project)
	
# Display all files
project = git.projects.get(proj_ID)
f = project.repository_tree()
for x in f:
	print(x)

