"""
crs_debuger.exceptions
~~~~~~~~~~~~~~~~~~~

This module contains the set of exceptions.
"""


class ClassInitError(BaseException):
    """实例初始化失败"""


class GetTunnelIDError(BaseException):
    """获取Tunnel ID失败"""