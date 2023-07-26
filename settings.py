#機器人token
def TOKEN(): return ""

#ID流水號
def datajson():
    import json, os
    if not(os.path.exists("data.json")):
        data = {"gidnum":0, "tempid":0, "summonid":0}
        with open("data.json", "w", encoding="utf8") as f: json.dump(data, f, ensure_ascii=False)

class GDATA():
    #遺照資料格式
    def data_format(uid:int): 
        import json, os
        from datetime import datetime
        with open("data.json", "r", encoding="utf8") as f: data = json.load(f)
        data2 = data
        data2['gidnum'] += 1
        with open("data.json", "w", encoding="utf8") as f: json.dump(data2, f, ensure_ascii=False)
        return {"grave": data["gidnum"],"user":uid, "sticks":[], "texts":"", "textedit":{"size":50, "pos":400, "color":"black"}, "convertL":True, "opensti":True, "summoned":[], "lastupdate":datetime.now().timestamp()}, data["gidnum"]
    #生成項目資料格式
    def summon_format(cid:int, msgid:int, sid:int): 
        return {"channel": cid, "message_id": msgid, "auto":False, "sid":sid}
    #創建遺照
    def create(path:str, uid:int):
        import json, os
        tjson, gid = GDATA.data_format(uid)
        with open(f"{path}/{str(gid)}.json", "w", encoding="utf8") as f: json.dump(tjson, f, ensure_ascii=False)
    #使用者控制項資料格式
    def toggle(): return {"tfgrave":True}
    #線香資料格式
    def stick(finalpos:int): return {"pos":finalpos, "burn":100}

#墓誌銘字體
def FONTPATH(): return "" 

#遺照: 頭項位置
class POSITION:
    def photopos(): return (120, 140)

class LIMIT():
    #生成項自動更新限制
    #開啟後一個遺照的所有生成項之中只能有一個使用自動更新
    #可依據伺服器性能做調整
    def summonautorefresh(): return True
    #生成項數量限制
    #限制一個遺照最多可以有幾個生成項
    #警告:超過25個可能導致遺照編輯:生成項的選單頁面發生錯誤
    def maxsummon(): return 25

#墓誌銘字體顏色表
def PHOTO_COLORS(): return ["red", "black", "white", "gray", "blue", "green", "pink", "purple", "aqua", "orange", "yellow", "brown"]

#自動刷新週期，單位: 秒
def AUTO_UPDATE_FREQUENCY(): return 300

#版本號
def VERSION(): return "1.0"