class User(object):
    def __init__(self, email, account_id):
        self.email = email
        self.account_id = account_id

    def __str__(self):
        return 'User(accountId={0}, emailAddress={1})'.format(
            self.account_id, self.account_id)


class Issue(object):
    def __init__(self, key, fields={}):
        self.key = key
        self.fields = Fields(fields)

    def __str__(self):
        return 'Issue(key={})'.format(self.key)


class Project(object):
    def __init__(self, _id, key, name, issue_types={}):
        self.id = _id
        self.key = key
        self.name = name
        self.issueTypes = []
        for issue_type in issue_types:
            self.issueTypes.append(
                IssueType(issue_type['id'], issue_type['name'])
            )

    def __str__(self):
        return 'Project(id={0},key={1},name={2})'.format(self.id, self.key,
                                                         self.name)


class IssueType(object):
    def __init__(self, _id, name):
        self.id = _id
        self.name = name

    def __str__(self):
        return 'IssueType(id={0}, name={1})'.format(self.id, self.name)


class Fields(object):
    def __init__(self, fields):
        for field in fields:
            if field == 'issueType':
                fields[field] = IssueType(
                    fields[field]['id'], fields[field]['name']
                )
            elif field == 'parent' and fields.get('parent'):
                fields[field] = Issue(
                    fields[field]['key'], fields[field]['fields']
                )
            elif field == 'project' and fields.get('project'):
                fields[field] = Project(
                    fields[field]['id'],
                    fields[field]['key'],
                    fields[field]['name']
                )
            elif field == 'creator' and fields.get('creator'):
                fields[field] = User(
                    fields[field].get('emailAddress'),
                    fields[field]['accountId']
                )
            elif field == 'assignee' and fields.get('assignee'):
                fields[field] = User(
                    fields[field].get('emailAddress'),
                    fields[field]['accountId']
                )
            elif field == 'reporter' and fields.get('reporter'):
                fields[field] = User(
                    fields[field].get('emailAddress'),
                    fields[field]['accountId']
                )
            self.__setattr__(field, fields[field])
