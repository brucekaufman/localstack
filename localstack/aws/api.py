import inspect
from typing import Any, Callable, Type, TypedDict, Dict

from botocore.model import OperationModel, ServiceModel


class ServiceRequest(TypedDict):
    pass


class ServiceException(Exception):
    pass


Operation = Type[ServiceRequest]


class RequestContext:
    service: ServiceModel
    operation: OperationModel
    region: str
    account: str
    request: Any

    @property
    def headers(self):
        return self.request["headers"]


class ServiceRequestHandler:
    fn: Callable
    operation: str
    context: RequestContext
    expand_parameters: bool = True
    pass_context: bool = True

    def __init__(
            self,
            fn: Callable,
            operation: str,
            pass_context: bool = True,
            expand_parameters: bool = False,
    ):
        self.fn = fn
        self.operation = operation
        self.pass_context = pass_context
        self.expand_parameters = expand_parameters

    def __call__(self, context: RequestContext, request: ServiceRequest):
        args = []
        kwargs = {}

        if self.pass_context:
            args.append(self.context)

        if self.expand_parameters:
            # todo
            pass
        else:
            args.append(request)

        return self.fn(*args, **kwargs)


DispatchTable = Dict[str, ServiceRequestHandler]


def handler(operation: str = None, context: bool = True, expand: bool = True):
    def wrapper(fn):

        return ServiceRequestHandler(
            fn=fn, operation=operation, pass_context=context, expand_parameters=expand
        )

    return wrapper


class Skeleton:
    service: ServiceModel
    delegate: Any
    dispatch_table: DispatchTable

    def __init__(self, service: ServiceModel, delegate: Any):
        self.service = service
        self.delegate = delegate
        self.dispatch_table: DispatchTable = dict()

        for name, obj in inspect.getmembers(delegate):
            if isinstance(obj, ServiceRequestHandler):
                self.dispatch_table[obj.operation] = obj

    def invoke(self, request: RequestContext):
        pass

