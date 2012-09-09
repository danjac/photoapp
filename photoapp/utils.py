import functools
import transaction


class DataManager(object):
    """
    Basic transactional manager
    """
    transaction_manager = transaction.manager

    def __init__(self, callable, on_abort=None, *args, **kwargs):
        self.callable = callable
        self.args = args
        self.kwargs = kwargs
        self.on_abort = on_abort

    def commit(self, transaction):
        pass

    def abort(self, transaction):
        if self.on_abort:
            self.on_abort()

    def tpc_begin(self, transaction):
        pass

    def tpc_vote(self, transaction):
        pass

    def tpc_finish(self, transaction):
        self.callable(*self.args, **self.kwargs)

    tpc_abort = abort


def on_commit(func, data_manager_cls=DataManager, on_abort=None):
    """
    Decorator for managing transactions
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        manager = data_manager_cls(func, on_abort, *args, **kwargs)
        transaction.get().join(manager)
    return wrapper
