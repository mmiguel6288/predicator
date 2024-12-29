# predicator

[![Actions Status][actions-badge]][actions-link]
[![GitHub Discussion][github-discussions-badge]][github-discussions-link]

<!-- SPHINX-START -->

<!-- prettier-ignore-start -->
[actions-badge]:            https://github.com/mmiguel6288/predicator/workflows/CI/badge.svg
[actions-link]:             https://github.com/mmiguel6288/predicator/actions
[github-discussions-badge]: https://img.shields.io/static/v1?label=Discussions&message=Ask&color=blue&logo=github
[github-discussions-link]:  https://github.com/mmiguel6288/predicator/discussions

<!-- prettier-ignore-end -->

# Predicator

Predicator is a Python package that provides a flexible way to handle hierarchical conditional configurations. It allows you to define configurations that can adapt based on runtime conditions, without sacrificing readability or maintainability. It supports both synchronous and asynchronous predicate evaluation.

## Features

- Wraps standard Python dictionaries, YAML, or JSON configurations
- Allows conditional logic at any nesting level
- Uses an intuitive "specific"/"generic" pattern for clear hierarchy
- Maintains backwards compatibility with simple configs
- Flexible predicate evaluation system
- Supports both synchronous and asynchronous predicate evaluation
- Full async iteration support

## Installation

Install using pip:

```bash
pip install git+https://github.com/mmiguel6288/predicator.git
```

## Basic Usage

### Synchronous Usage

Here's a simple example using synchronous predicates:

```python
from predicator import PredicatorDict

# Define your config
config = {
    "database_pool_size": {
        "specific": {
            "generic": 10,  # Default value
            "production": 100,  # Used when in production
            "testing": 5  # Used when in testing
        }
    }
}

# Define your predicate evaluator
def environment_checker(predicate):
    current_env = "production"  # This would normally come from your environment
    return predicate == current_env

# Create a PredicatorDict
settings = PredicatorDict(config, environment_checker)

# Access values - they'll be resolved based on your predicate evaluator
pool_size = settings["database_pool_size"]  # Returns 100 if in production
```

### Asynchronous Usage

For scenarios where predicate evaluation needs to be asynchronous (e.g., database lookups, API calls):

```python
import asyncio
from predicator import PredicatorDict

# Define your config
config = {
    "database_pool_size": {
        "specific": {
            "generic": 10,
            "high_load": 100
        }
    }
}

# Async predicate evaluator
async def load_checker(predicate):
    # Simulate checking system metrics asynchronously
    await asyncio.sleep(0.1)
    return predicate == "high_load"

async def main():
    settings = PredicatorDict(config, load_checker)
    
    # Use aget() for async access
    pool_size = await settings.aget("database_pool_size")
    
    # Async iteration
    async for key in settings:
        value = await settings.aget(key)
        print(f"{key}: {value}")
    
    # Alternative async iterations
    async for value in settings.avalues():
        print(value)
    
    async for key, value in settings.aitems():
        print(f"{key}: {value}")

asyncio.run(main())
```

### Custom Predicate Keys

If your configuration needs to use "specific" or "generic" as actual data keys, you can customize the predicate keys:

```python
# Using custom keys
config = {
    "database_pool_size": {
        "@rules": {  # Custom predicate key
            "@default": 10,  # Custom default key
            "production": 100,
            "testing": 5
        }
    }
}

# Specify custom keys in constructor
settings = PredicatorDict(
    config, 
    environment_checker,
    specific_key="@rules",
    generic_key="@default"
)

# Sync access
pool_size = settings["database_pool_size"]

# Async access
pool_size = await settings.aget("database_pool_size")
```

## Advanced Usage

### Nested Conditions

You can nest conditions to create more complex logic:

```python
config = {
    "api_rate_limit": {
        "specific": {
            "generic": 100,  # Default rate limit
            "premium_user": {
                "generic": 500,  # Default for premium users
                "high_usage_period": 1000  # Premium users during high usage
            }
        }
    }
}

# Async predicate evaluator
async def check_conditions(predicate):
    conditions = {
        "premium_user": await check_premium_status(),
        "high_usage_period": await check_usage_metrics()
    }
    return conditions.get(predicate, False)

async def main():
    settings = PredicatorDict(config, check_conditions)
    rate_limit = await settings.aget("api_rate_limit")
```

### Feature Flags

Perfect for feature flag systems with async checks:

```python
config = {
    "ui_theme": {
        "specific": {
            "generic": "light",
            "dark_mode_enabled": "dark",
            "holiday_season": {
                "generic": "festive",
                "dark_mode_enabled": "festive-dark"
            }
        }
    }
}

async def feature_checker(predicate):
    if predicate == "dark_mode_enabled":
        return await check_user_preferences()
    if predicate == "holiday_season":
        return await check_holiday_dates()
    return False
```

## How It Works

1. When accessing a configuration value, Predicator checks if it contains a "specific" structure
2. The "generic" key provides the default value if no conditions match
3. Other keys in the "specific" dictionary are treated as predicates
4. Predicates are evaluated using the provided predicate_evaluator function (sync or async)
5. Nested predicates create AND logic (all conditions must be true)
6. The most specific matching value is returned
7. When using async predicates, all access must use async methods (aget, aiter, etc.)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
