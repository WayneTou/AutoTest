import requests

class Testclass:
    def test_fun(self):
        res = requests.get('https://www.baidu.com')
        assert res.status_code == 200
