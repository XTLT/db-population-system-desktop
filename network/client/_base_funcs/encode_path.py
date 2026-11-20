"""把 path 编码成能放进 HTTP 请求行的形式。

http.client 生成请求行时只接受 ASCII（`request.encode('ascii')`），而人员
id / 户号这类值可能来自库里的历史数据、含中文（例如 id 就是姓名"池旭霞"），
直接拼进 path 会让 putrequest 抛
    UnicodeEncodeError: 'ascii' codec can't encode characters in position ...
请求根本发不出去，界面只会显示"修改失败：无法连接服务器: ..."。

只编码必要字符：路径段保留 "/" 和已有的 %xx，查询串保留 "&="，
这样调用方已经做过 quote 的值（如 api_search 里 quote(name)）不会被二次编码。
服务端 Flask 路由会自动把 %xx 解回原文，语义不变。

所有自己拼 URL 的入口（_request / _request_raw / _download_file /
照片上传下载删除）都必须经过这里，否则库里的中文 id 会把请求行写崩。
"""

from urllib.parse import quote


def encode_path(path: str) -> str:
    if "?" in path:
        p, q = path.split("?", 1)
        return quote(p, safe="/%") + "?" + quote(q, safe="&=%")
    return quote(path, safe="/%")
