###
# File:   src\logic\pattern\observer.py
# Date:   2025-02-05 / 10:32
# Author: alexrjs
###


# imports


# constants


# variables


# functions/classes
# class Observer(dict):
#     """Observer class"""

#     def __init__(self, observable, callback) -> None:
#         """Constructor"""

#         observable.register(self)
#         self["callback"] = callback

#     def receive(self, *args, **kwargs) -> None:
#         """Notify the observer"""

#         print("Got", args, kwargs)


class Observable():
    """Observable class"""

    observers: dict = {}

    def __init__(self, name) -> None:
        """Constructor"""
        
        self.name = name if name else "Observable"

    def register(self, observer) -> None:
        """Register an observer"""

        Observable.observers.setdefault(self.name, []).append(observer)

    def unregister(self, observer) -> None:
        """Unregister an observer"""

        del Observable.observers[observer]

    def notify(self, *args, **kwargs) -> None:
        """Notify the observers"""

        if self.name not in Observable.observers:
            return
        
        for obs in self.observers[self.name]:
            if obs:
                obs(self.name, *args, **kwargs)


class ObservablesList(dict):

    def __init__(self, category:str) -> None:
        self.category = category

    def register(self, subject:str) -> Observable:
        if subject in self.keys():
            return self[subject]

        self[subject] = Observable(subject)
        return self[subject]