from crs_debuger.core import Database
from pprint import pprint


class Test:
    def test_add_del(self):

        appkey = "huangxiaojunkey"
        appsecret = "huangxiaojunsecret"
        pic = "lion.jpg"

        user = Database(cloud="test", appkey=appkey, appsecret=appsecret)
        # 增加target
        add_result_json = user.add_target(image=pic)
        pprint(add_result_json)
        target_id = add_result_json["result"]["targetId"]
        print(target_id)
        assert target_id
        assert add_result_json["statusCode"] == 0

        # 删除target
        del_result = user.del_target(target_id)
        pprint(del_result)
        assert del_result["statusCode"] == 0
        # 获取target列表

        target_list = user.target_list()
        pprint(target_list)

        assert len(target_list["result"]["targets"]) == 0
