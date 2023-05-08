class CompilerError(Exception):
    def __init__(self, *args, **kwargs):
        super(CompilerError, self).__init__(*args, **kwargs)
