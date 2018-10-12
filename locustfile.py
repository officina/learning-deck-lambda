from locust import HttpLocust, TaskSet, task


class UserBehavior(TaskSet):

    @task(2)
    def with_token(self):
        self.client.get("/prod/api/userstatus/player_1?state=READY")

    # @task(1)
    # def without_token(self):
    #     self.client.get("/dev/test/withouttoken")

    tasks = {with_token: 1}


class WebsiteUser(HttpLocust):
    task_set = UserBehavior
    min_wait = 5000
    max_wait = 9000