from locust import HttpLocust, TaskSet, task


class UserBehavior(TaskSet):

    @task(2)
    def with_token(self):
        # self.client.get("/api/userstatus/player_1?state=READY")

        self.client.get("/admin/players/006138fcc80e4e4dac0eb363ba6a915e?access_token=Y2E2M2QzNDctMTFhYy00Y2VkLWJlYTYtZTBlOGE0ODI4NmM4")
        self.client.get("/runtime/leaderboards/progressione_personale?access_token=Y2E2M2QzNDctMTFhYy00Y2VkLWJlYTYtZTBlOGE0ODI4NmM4&player_id=006138fcc80e4e4dac0eb363ba6a915e&"
                        "cycle=alltime&entity_id=006138fcc80e4e4dac0eb363ba6a915e&radius=0&sort=descending&ranking=relative")


    # @task(1)
    # def without_token(self):
    #     self.client.get("/dev/test/withouttoken")

    tasks = {with_token: 1}


class WebsiteUser(HttpLocust):
    task_set = UserBehavior
    min_wait = 5000
    max_wait = 9000