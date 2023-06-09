from abc import ABC, abstractmethod

class Service(ABC):
  ...


class ServiceNotDispatched(Exception):
  ...