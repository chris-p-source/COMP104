from datetime import datetime
from pydriller import repository

dt1 = datetime(2021, 12, 1)
dt2 = datetime.now()

for commit in repository.Repository("repos/hbase", since=dt1).traverse_commits():
    for modified in commit._get_modifications():
        print(modified.diff)
