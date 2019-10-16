import sys
import os
import gitlab
# TODO setup a test to make sure everything is working
# TODO add support for multi-line comments
accepted_file_types = {'.py': ['#todo', '# todo'],
                       '.c': ['//todo', '// todo'],
                       '.cpp': ['//todo', '// todo'],
                       '.js': ['//todo', '// todo', '// fixme', '//fixme'],
                       '.java': ['//todo', '// todo', '// fixme', '//fixme'],
                       '.php': ['//todo', '// todo', '// fixme', '//fixme'],
                       '.swift': ['//todo', '// todo', '// fixme', '//fixme'],
                       '.cs': ['//todo', '// todo'],
                       '.kt': ['fun todo', '//todo', '// todo'],
                       '.go': ['//todo', '// todo', '// fixme', '//fixme']}


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
    def __init__(self, name, path):
        self.path = path
        self.name = name
        self.lines = []

    def read(self, file_type):
        try:
            with open(self.path, "r") as f:
                for line_number, todo_line in enumerate(f):
                    for todo_style in accepted_file_types.get(file_type):
                        if todo_style in todo_line.lower():
                            self.lines.append("".join(["Line number:", str(line_number+1), " ",  todo_line.strip()]))
        except Exception as e:
            print(e)


if __name__ == "__main__":
    files = dict()
    try:
        gl = GitConnect()
    except ValueError as error:
        print(error)
        sys.exit(1)
    for root, _, files in os.walk('.', topdown=False):
        for filename in files:
            file_path = os.path.join(root, filename)
            for accepted_file_type in accepted_file_types.keys():
                if accepted_file_type in filename:
                    file = FileToScrape(filename, file_path)
                    if file.name not in sys.argv:
                        file.read(accepted_file_type)
                        for line in file.lines:
                            gl.create_issue(file.name, line)
                            print(file.name, line)
