# src/predicator/core.py
from typing import Any, Callable, Dict, Tuple, Iterator, ItemsView, KeysView, ValuesView, List
from collections.abc import Mapping

PredicateEvaluator = Callable[[str], bool]

class PredicatorDict(Mapping):
    def __init__(
        self, 
        config: Dict, 
        predicate_evaluator: PredicateEvaluator
    ) -> None:
        self._config = config
        self._predicate_evaluator = predicate_evaluator

    def __getitem__(self, key) -> Any:
        value = self._config[key]
        if isinstance(value,dict) and 'specific' in value and isinstance(specific := value['specific'],dict) and 'generic' in specific:
            specific = value
            generic = specific['generic']
            if isinstance(generic,dict):
                generic = PredicatorDict(generic,self._predicate_evaluator)
            resolved, value = self._resolve_specific(specific,generic)
            #if resolved is false, it just means the generic value is used
        return value

    def _resolve_specific(self, specific: Any, generic: Any) -> Tuple[bool,Any]:
        for pred_condition, pred_value in specific.items():
            if pred_condition == "generic":
                #ignore the generic since it was already grabbed
                continue

            if self._predicate_evaluator(pred_condition):
                if isinstance(pred_value, dict):
                    if 'generic' in pred_value:
                        current_generic = pred_value['generic']
                        if isinstance(current_generic,dict):
                            current_generic = PredicatorDict(current_generic,self._predicate_evaluator)
                        end_here = True #if the next level down fails to resolve, then we commit to the next level down's generic
                    else:
                        current_generic = generic
                        end_here = False #if the next level down fails to resolve, then we move on to the next predicate at this level
                    resolved,value = self._resolve_specific(pred_value, current_generic)
                    if resolved or end_here:
                        return True, value
                else:
                    return True, pred_value

        return False, generic

    def __contains__(self, key) -> bool:
        return key in self._config
    def __iter__(self) -> Iterator:
        return iter(self._config)
    def __len__(*self) -> int:
        return len(self._config)
    def get(self, key, default=None) -> Any:
        if key not in self._config:
            return default
        return self[key]
    def keys(self) -> KeysView:
        return self._config.keys()
    def values(self) -> Iterator[Any]:
        return (self[key] for key in self)
    def items(self) -> Iterator[Tuple[Any,Any]]:
        return ((key,self[key]) for key in self)
