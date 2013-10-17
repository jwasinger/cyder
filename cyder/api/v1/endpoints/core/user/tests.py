from django.contrib.auth.models import User
from cyder.api.v1.tests.base import APITests


class UserAPI_Test(APITests):
    __test__ = True
    model = User
    url = "core/user"

    def create_data(self):
        return self.model.objects.get_or_create(username="test_user")[0]
