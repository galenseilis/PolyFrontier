import abc

from typing import Optional, List, Any, Callable


class PipelineInterruption(Exception):
    pass


class AbstractPipelineProcess(abc.ABC):

    def __init__(self):
        self.pipeline = None

    def __call__(self, *args, **kwargs):
        return self.process(args[0])

    def __str__(self):
        return self.__class__.__name__

    def __repr__(self):
        return str(self)

    @abc.abstractmethod
    async def process(self, element):
        pass


OPT_PROCESSES_TYPE = Optional[List[Callable]]


class Pipeline:

    def __init__(self, init_param: Any, success_msg: str = 'ok', failure_msg: str = None,
                 processes: OPT_PROCESSES_TYPE = None):
        self.init_param: Any = init_param
        self.success_msg: str = success_msg
        self.failure_msg: Optional[str] = failure_msg
        self.processes: OPT_PROCESSES_TYPE = processes or []

    def __call__(self, *args, **kwargs):
        return self.execute()

    def __rshift__(self, other: Callable):
        self.processes.append(other)
        other.pipeline = self
        return self

    def __str__(self):
        return f"{self.__class__.__name__} [{'->'.join(str(p) for p in self.processes)}]"

    def __repr__(self):
        return str(self)

    async def execute(self):
        last_res = self.init_param
        for i, p in enumerate(self.processes):
            print(f"Processing task n°{i} / {p}")
            try:
                last_res = await p(last_res)
                print(f"Task n°{i} done.")
            except PipelineInterruption as e:
                print(f"Task n°{i} interrupted.")
                return str(self.failure_msg if self.failure_msg is not None else e), last_res
        return self.success_msg, last_res
