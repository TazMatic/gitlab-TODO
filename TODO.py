import sys
import os
import glob2
import gitlab
# TODO add multi language support
# TODO exclude todo.py from search


class GitConnect:
    def __init__(self):
        self.host = "".join(["https://", os.getenv("CI_SERVER_HOST")])
        self.projectPath = os.getenv("CI_PROJECT_PATH")
        self.token = os.getenv("PAT")
        if not self.token:
            raise ValueError("Please export a private key with API and write access as PAT")
        self.connection = None
        self.project = None
        self.setup()
        self.issues = self.connection.issues.list(state='opened')

    def setup(self):
        self.connection = gitlab.Gitlab(self.host, self.token, api_version="4")
        self.connection.auth()
        self.project = self.connection.projects.get(self.projectPath)

    def create_issue(self, title, description):
        if self.check_issues(title, description):
            issue = self.project.issues.create({'title': title, 'description': description})
            issue.labels = ["TODO"]
            issue.save()

    def check_issues(self, title, description):
        for issue in self.issues:
            if issue.title == title and issue.description.startswith("Line number:") \
                    and issue.description[12:].split(' ', 1)[1] == description[12:].split(' ', 1)[1]:
                if issue.description[12:].split(' ', 1)[0] == description[12:].split(' ', 1)[0]:
                    return False
                else:
                    # Edit old issue to have new line number
                    editable_issue = self.project.issues.get(issue.iid, lazy=True)
                    editable_issue.description = description
                    editable_issue.save()
                    return False
        return True


class FileToScrape:
    def __init__(self, path):
        self.path = path
        self.name = self.path.split("/")[-1]
        self.lines = []

    def read(self):
        try:
            with open(self.path, "r") as f:
                for line_number, todo_line in enumerate(f):
                    if "TODO" in todo_line:
                        self.lines.append("".join(["Line number:", str(line_number), " ",  todo_line.strip()]))
        except Exception as e:
            print(e)


if __name__ == "__main__":
    files = dict()
    try:
        gl = GitConnect()
    except ValueError as error:
        print(error)
        sys.exit(1)

    for file in glob2.glob("./**/*.py"):
        x = FileToScrape(file)
        if x.name not in sys.argv:
            files[x.name] = x
            x.read()
            for line in x.lines:
                gl.create_issue(x.name, line)
                print(x.name, line)
