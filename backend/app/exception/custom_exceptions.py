class Not_Authorized(Exception):
    def __init__(self,msg):
        self.message=msg

class Content_Not_Found(Exception):
    def __init__(self,msg):
        self.message=msg

class Bad_Request(Exception):
    def __init__(self,msg):
        self.message=msg