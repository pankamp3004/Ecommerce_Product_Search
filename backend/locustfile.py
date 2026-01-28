import json
from locust import HttpUser, task, between


class APIUser(HttpUser):
    wait_time = between(1, 2)

    @task(3)
    def call_search(self):
        params = {
            "q": "campus shoes under 2000"
        }
        self.client.get("/search", params=params)

    @task(1)
    def call_root(self):
        self.client.get("/")
