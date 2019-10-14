import sys
import os
import glob2
import gitlab


class GitConnect:
    def __init__(self):
        self.host = "".join(["https://", os.getenv("CI_SERVER_HOST")])
        self.projectPath = os.getenv("CI_PROJECT_PATH")
        self.token = os.getenv("PAT")
        self.connection = None
        self.project = None
        self.setup()

    def setup(self):
        self.connection = gitlab.Gitlab(self.host, self.token, api_version="4")
        self.connection.auth()
        self.project = self.connection.projects.get(self.projectPath)

    def create_issue(self, title, description):
        issue = self.project.issues.create({'title': title, 'description': description})
        issue.labels = ["TODO"]
        issue.save()


class FileToScrape:
    def __init__(self, path):
        self.path = path
        self.name = self.path.split("/")[-1]
        self.lines = None

    def read(self):
        try:
            with open(self.path, "r") as f:
                self.lines = [line for line in f.readlines() if "TODO" in line]
        #TODO fix this shit asshole
        except Exception as e:
            print(e)


if __name__ == "__main__":
    files = dict()
    gl = GitConnect()
    for file in glob2.glob("./**/*.py"):
        x = FileToScrape(file)
        files[x.name] = x
        x.read()
        for line in x.lines:
            gl.create_issue(x.name, line.strip())
            print(x.name, line.strip())
