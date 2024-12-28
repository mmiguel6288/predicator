from typing import Any, Callable, Dict, Tuple, Iterator, ItemsView, KeysView, ValuesView, List, Optional
from collections.abc import Mapping
from dataclasses import dataclass

PredicateEvaluator = Callable[[str], bool]

@dataclass
class Resolution:
    """Represents the result of resolving a specific value."""
    resolved: bool
    value: Any

class PredicatorDict(Mapping):
    """A dictionary-like object that supports predicate-based value resolution."""
    
    SPECIFIC_KEY = "specific"
    GENERIC_KEY = "generic"
    
    def __init__(
        self, 
        config: Dict, 
        predicate_evaluator: PredicateEvaluator
    ) -> None:
        """
        Initialize a PredicatorDict.
        
        Args:
            config: The configuration dictionary
            predicate_evaluator: Callable that evaluates predicate conditions
        """
        self._config = config
        self._predicate_evaluator = predicate_evaluator
        
    def __getitem__(self, key: str) -> Any:
        value = self._config[key]
        if not self._is_predicator_dict(value):
            return value
            
        specific = value[self.SPECIFIC_KEY]
        generic = self._wrap_generic(specific[self.GENERIC_KEY])
        resolution = self._resolve_specific(specific, generic)
        return resolution.value
    
    def _is_predicator_dict(self, value: Any) -> bool:
        """Check if a value represents a predicator dictionary structure."""
        return (
            isinstance(value, dict) 
            and self.SPECIFIC_KEY in value 
            and isinstance(value[self.SPECIFIC_KEY], dict)
            and self.GENERIC_KEY in value[self.SPECIFIC_KEY]
        )
    
    def _wrap_generic(self, generic: Any) -> Any:
        """Wrap generic value in PredicatorDict if needed."""
        return (
            PredicatorDict(generic, self._predicate_evaluator) 
            if isinstance(generic, dict) 
            else generic
        )

    def _resolve_specific(self, specific: Dict, generic: Any) -> Resolution:
        """
        Resolve the most specific applicable value.
        
        Args:
            specific: Dictionary containing predicates and values
            generic: Default value if no predicates match
            
        Returns:
            Resolution object containing resolved status and value
        """
        for pred_condition, pred_value in specific.items():
            if pred_condition == self.GENERIC_KEY:
                continue

            if not self._predicate_evaluator(pred_condition):
                continue
                
            if not isinstance(pred_value, dict):
                return Resolution(True, pred_value)
                
            current_generic = pred_value.get(self.GENERIC_KEY, generic)
            current_generic = self._wrap_generic(current_generic)
            end_here = self.GENERIC_KEY in pred_value
            
            resolution = self._resolve_specific(pred_value, current_generic)
            if resolution.resolved or end_here:
                return resolution

        return Resolution(False, generic)

    # Mapping interface implementations
    def __contains__(self, key: str) -> bool:
        return key in self._config
        
    def __iter__(self) -> Iterator[str]:
        return iter(self._config)
        
    def __len__(self) -> int:
        return len(self._config)
        
    def get(self, key: str, default: Any = None) -> Any:
        return self[key] if key in self else default
        
    def keys(self) -> KeysView:
        return self._config.keys()
        
    def values(self) -> Iterator[Any]:
        return (self[key] for key in self)
        
    def items(self) -> Iterator[Tuple[str, Any]]:
        return ((key, self[key]) for key in self)
