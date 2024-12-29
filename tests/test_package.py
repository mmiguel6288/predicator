from __future__ import annotations
import importlib.metadata
import predicator as m
from predicator import PredicatorDict
import pytest
import predicator as m
from predicator import PredicatorDict
import asyncio

def test_version():
    assert importlib.metadata.version("predicator") == m.__version__


# Synchronous tests
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

# Asynchronous tests
@pytest.mark.asyncio
async def test_basic_config_async():
    async def eval_true(_): return True

    config = {'key':'value'}
    pred_dict = PredicatorDict(config, eval_true)
    assert await pred_dict.aget('key') == 'value'

@pytest.mark.asyncio
async def test_simple_predicate_async():
    async def evaluator(pred):
        await asyncio.sleep(0.01) # simulate async work
        return pred == 'condition1'
    config = {
        'setting': {
            'specific': {
                'generic': 50,
                'condition1':100
                }
            }
        }
    pred_dict = PredicatorDict(config, evaluator)
    result = await pred_dict.aget('setting') 
    assert result == 100

@pytest.mark.asyncio
async def test_nested_predicates_async():
    async def evaluator(pred):
        await asyncio.sleep(0.01)
        return pred in ['condition1','condition2']
    config = {
            'setting':{
                'specific':{
                    'generic':50,
                    'condition1':{
                        'generic':100,
                        'condition2':200,
                        }
                    }
                }
            }
    pred_dict = PredicatorDict(config, evaluator)
    assert await  pred_dict.aget('setting') == 200

@pytest.mark.asyncio
async def test_fallback_to_generic_async():
    async def evaluator(pred):
        await asyncio.sleep(0.01)
        return False
    
    config = {
        "setting": {
            "specific": {
                "generic": 50,
                "condition1": 100
            }
        }
    }
    
    pred_dict = PredicatorDict(config, evaluator)
    assert await pred_dict.aget("setting") == 50

@pytest.mark.asyncio
async def test_custom_keys_async():
    async def evaluator(pred):
        await asyncio.sleep(0.01)
        return pred == "condition1"
    
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
    assert await pred_dict.aget("setting") == 100

@pytest.mark.asyncio
async def test_async_iteration():
    async def evaluator(pred):
        await asyncio.sleep(0.01)
        return pred == "condition1"
    
    config = {
        "setting1": {
            "specific": {
                "generic": 50,
                "condition1": 100
            }
        },
        "setting2": {
            "specific": {
                "generic": 60,
                "condition1": 120
            }
        }
    }
    
    pred_dict = PredicatorDict(config, evaluator)
    
    # Test async iteration over keys
    keys = []
    async for key in pred_dict:
        keys.append(key)
    assert sorted(keys) == ["setting1", "setting2"]
    
    # Test async iteration over values
    values = []
    async for value in pred_dict.avalues():
        values.append(value)
    assert sorted(values) == [100, 120]
    
    # Test async iteration over items
    items = {}
    async for key, value in pred_dict.aitems():
        items[key] = value
    assert items == {"setting1": 100, "setting2": 120}

@pytest.mark.asyncio
async def test_sync_access_with_async_predicator():
    async def evaluator(pred):
        await asyncio.sleep(0.01)
        return pred == "condition1"
    
    config = {
        "setting": {
            "specific": {
                "generic": 50,
                "condition1": 100
            }
        }
    }
    
    pred_dict = PredicatorDict(config, evaluator)
    
    # Verify that sync access raises an error with async evaluator
    with pytest.raises(RuntimeError) as exc_info:
        _ = pred_dict["setting"]
    assert "Async predicate evaluator requires using aget() method" in str(exc_info.value)

def test_mixed_structures():
    def evaluator(pred): return pred == "condition1"
    
    config = {
        "metadata": {
            "specific": "some value",
            "generic": "another value"
        },
        "rules": {
            "@rules": {
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

@pytest.mark.asyncio
async def test_mixed_structures_async():
    async def evaluator(pred):
        await asyncio.sleep(0.01)
        return pred == "condition1"
    
    config = {
        "metadata": {
            "specific": "some value",
            "generic": "another value"
        },
        "rules": {
            "@rules": {
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
    
    assert await pred_dict.aget("metadata") == {
        "specific": "some value",
        "generic": "another value"
    }
    assert await pred_dict.aget("rules") == "matched value"
