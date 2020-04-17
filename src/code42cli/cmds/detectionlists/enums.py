class DetectionLists(object):
    DEPARTING_EMPLOYEE = u"departing-employee"
    HIGH_RISK_EMPLOYEE = u"high-risk-employee"


class BulkCommandType(object):
    ADD = u"add"

    def __iter__(self):
        return iter([self.ADD])


class DetectionListUserKeys(object):
    CLOUD_ALIAS = u"cloud_alias"
    USERNAME = u"username"
    NOTES = u"notes"
    RISK_TAG = u"risk_tag"
