class __Autonomy__(object):
    """
    ??????write??
    """
    def __init__(self):
        """
        init
        """
        self._buff = ""
 
    def write(self, out_stream):
        """
        :param out_stream:
        :return:
        """
        self._buff += out_stream


