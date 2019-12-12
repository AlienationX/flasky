# coding=utf-8
# python3


class StatusCode:
    http_code = {}  # http code
    api_code = {}  # api code

    # HTTP状态码
    http_code[100] = "Continue"

    http_code[200] = "OK"
    http_code[201] = "Created"
    http_code[202] = "Accepted"
    http_code[204] = "No Content"

    http_code[400] = "Bad Request"
    http_code[401] = "Unauthorized"
    http_code[403] = "Forbidden"
    http_code[404] = "Not Found"
    http_code[405] = "Method Not Allowed"

    http_code[500] = "Internal Server Error"
    http_code[502] = "Bad Gateway"
    http_code[500] = "Service Unavailable"

    # API自定义的返回信息

    # 参数型错误
    api_code[1000] = "未知错误"
    api_code[1001] = "参数不能为空"
    api_code[1002] = "非法参数"
    api_code[1003] = "参数类型错误"
    api_code[1004] = "参数格式错误"
    api_code[1005] = "参数必须为整数"
    api_code[1006] = "参数值超出范围"
    api_code[1007] = "参数长度超出限制"

    # 身份验证相关
    api_code[2001] = "缺少参数"
    api_code[2002] = "Token错误"
    api_code[2003] = "签名值错误"
    api_code[2004] = "请求时间戳过期"
    api_code[2005] = "非法请求"
    api_code[2006] = "身份验证失败"
    api_code[2100] = "已经登录"
    api_code[2101] = "该用户不存在"
    api_code[2102] = "非登录状态"
    api_code[2103] = "该用户已存在"
    api_code[2104] = "用户信息需要完善"
    api_code[2105] = "用户名或密码错误"
    api_code[2106] = "没有权限"

    # 路由相关
    api_code[3001] = "指定模块不存在"
    api_code[3002] = "请求方法不存在"

    # 内容相关
    api_code[4001] = "没有数据"

    # 数据库相关
    api_code[5001] = "数据库连接错误"
    api_code[5101] = "没有数据库表格式定义"
    api_code[5102] = "数据库表格式定义错误"
    api_code[5103] = "数据项不符合数据库表字段类型"
    api_code[5104] = "数据库表非空字段没有传值"
    api_code[5105] = "数据项值不是可用的枚举值"
    api_code[5106] = "数据项值小于允许的最小值"
    api_code[5107] = "数据项值大于允许的最大值"
    api_code[5201] = "没有获取到数据"
    api_code[5203] = "数据库插入失败"
    api_code[5204] = "数据库更新失败"
    api_code[5205] = "数据库删除失败"
    api_code[5206] = "数据库查询失败"
    api_code[5207] = "数据读取发生异常"
    api_code[5208] = "数据写入发生异常"
    api_code[5209] = "数据更新发生异常"
    api_code[5210] = "数据删除发生异常"
    api_code[5211] = "数据没有更新"
    api_code[5212] = "重复操作"

    # 自动接口错误
    api_code[6001] = "中间层查询失败"
    api_code[6002] = "RPC框架返回有误"
    api_code[6003] = "数据源类型不一致"
    api_code[6004] = "中间件层请求已超时"

    # 队列缓存相关
    api_code[7001] = "进入队列失败"
    api_code[7001] = "缓存失败"

    # 其它
    api_code[8000] = "发送验证码失败"
    api_code[8100] = "找不到上传文件"
    api_code[8101] = "文件大小超出限制"
    api_code[8102] = "文件上传不完整"
    api_code[8103] = "找不到上传文件"
    api_code[8104] = "临时文件夹错误"
    api_code[8105] = "保存失败"
    api_code[8106] = "文件上传中止"

    """下面的处理感觉没啥必要啊"""

    # @staticmethod
    # def get_http_message(code):
    #     if not StatusCode.http_code.has_key(code):
    #         return "未知错误"
    #     return StatusCode.http_code[code]
    #
    # @staticmethod
    # def get_api_message(code):
    #     if not StatusCode.api_code.has_key(code):
    #         return "未知api错误"
    #     return StatusCode.api_code[code]
