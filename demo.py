from crs_debuger.core import Database
from pprint import pprint


if __name__ == "__main__":

    appkey = "huangxiaojunkey"
    appsecret = "huangxiaojunsecret"
    pic = "lion.jpg"

    db = Database(host="10.10.51.111", appkey=appkey, appsecret=appsecret)

    # 增加target
    # add_result_json = db.add_target(image=pic)
    # pprint(add_result_json)
    # target_id = add_result_json["result"]["targetId"]
    # print(target_id)

    # 删除target
    # del_result = db.del_target(target_id)
    # pprint(del_result)

    # 获取target列表
    # target_list = db.target_list()
    # pprint(target_list)

    # 扫描
    result = db.search(pic, notracking=True)
    pprint(result)
