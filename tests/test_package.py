from __future__ import annotations

import importlib.metadata

import predicator as m

from predicator import PredicatorDict


import pytest

def test_version():
    assert importlib.metadata.version("predicator") == m.__version__

def test_basic_config():
    def eval_true(_): return True
    
    config = {"key": "value"}
    pred_dict = PredicatorDict(config, eval_true)
    assert pred_dict["key"] == "value"

def test_simple_predicate():
    def evaluator(pred): return pred == "condition1"
    
    config = {
        "setting": {
            "specific": {
                "generic": 50,
                "condition1": 100
            }
        }
    }
    
    pred_dict = PredicatorDict(config, evaluator)
    assert pred_dict["setting"] == 100

def test_nested_predicates():
    def evaluator(pred): return pred in ["condition1", "condition2"]
    
    config = {
        "setting": {
            "specific": {
                "generic": 50,
                "condition1": {
                    "generic": 100,
                    "condition2": 200
                }
            }
        }
    }
    
    pred_dict = PredicatorDict(config, evaluator)
    assert pred_dict["setting"] == 200

def test_fallback_to_generic():
    def evaluator(pred): return False
    
    config = {
        "setting": {
            "specific": {
                "generic": 50,
                "condition1": 100
            }
        }
    }
    
    pred_dict = PredicatorDict(config, evaluator)
    assert pred_dict["setting"] == 50

def test_custom_keys():
    def evaluator(pred): return pred == "condition1"
    
    # Using @rules/@default as custom keys
    config = {
        "setting": {
            "@rules": {
                "@default": 50,
                "condition1": 100
            }
        }
    }
    
    pred_dict = PredicatorDict(
        config, 
        evaluator,
        specific_key="@rules",
        generic_key="@default"
    )
    assert pred_dict["setting"] == 100

def test_nested_custom_keys():
    def evaluator(pred): return pred in ["condition1", "condition2"]
    
    config = {
        "setting": {
            "@rules": {
                "@default": 50,
                "condition1": {
                    "@default": 100,
                    "condition2": 200
                }
            }
        }
    }
    
    pred_dict = PredicatorDict(
        config, 
        evaluator,
        specific_key="@rules",
        generic_key="@default"
    )
    assert pred_dict["setting"] == 200

def test_mixed_structures():
    def evaluator(pred): return pred == "condition1"
    
    # A config that actually needs to use "specific" as a legitimate key
    config = {
        "metadata": {
            "specific": "some value",  # This is actual data
            "generic": "another value"  # This is actual data
        },
        "rules": {
            "@rules": {  # Using different keys for predicator logic
                "@default": "default value",
                "condition1": "matched value"
            }
        }
    }
    
    pred_dict = PredicatorDict(
        config, 
        evaluator,
        specific_key="@rules",
        generic_key="@default"
    )
    
    assert pred_dict["metadata"] == {
        "specific": "some value",
        "generic": "another value"
    }
    assert pred_dict["rules"] == "matched value"
