# predicator

[![Actions Status][actions-badge]][actions-link]
[![Documentation Status][rtd-badge]][rtd-link]

[![PyPI version][pypi-version]][pypi-link]
[![Conda-Forge][conda-badge]][conda-link]
[![PyPI platforms][pypi-platforms]][pypi-link]

[![GitHub Discussion][github-discussions-badge]][github-discussions-link]

<!-- SPHINX-START -->

<!-- prettier-ignore-start -->
[actions-badge]:            https://github.com/mmiguel6288/predicator/workflows/CI/badge.svg
[actions-link]:             https://github.com/mmiguel6288/predicator/actions
[conda-badge]:              https://img.shields.io/conda/vn/conda-forge/predicator
[conda-link]:               https://github.com/conda-forge/predicator-feedstock
[github-discussions-badge]: https://img.shields.io/static/v1?label=Discussions&message=Ask&color=blue&logo=github
[github-discussions-link]:  https://github.com/mmiguel6288/predicator/discussions
[pypi-link]:                https://pypi.org/project/predicator/
[pypi-platforms]:           https://img.shields.io/pypi/pyversions/predicator
[pypi-version]:             https://img.shields.io/pypi/v/predicator
[rtd-badge]:                https://readthedocs.org/projects/predicator/badge/?version=latest
[rtd-link]:                 https://predicator.readthedocs.io/en/latest/?badge=latest

<!-- prettier-ignore-end -->

# Predicator

Predicator is a Python package that provides a flexible way to handle hierarchical conditional configurations. It allows you to define configurations that can adapt based on runtime conditions, without sacrificing readability or maintainability.

## Features

- Wraps standard Python dictionaries, YAML, or JSON configurations
- Allows conditional logic at any nesting level
- Uses an intuitive "specific"/"generic" pattern for clear hierarchy
- Maintains backwards compatibility with simple configs
- Flexible predicate evaluation system

## Installation

Install using pip:

```bash
pip install git+https://github.com/mmiguel6288/predicator.git
```

## Basic Usage

Here's a simple example of using Predicator:

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

pool_size = settings["database_pool_size"]  # Works the same way
```

## Advanced Usage

### Nested Conditions

You can nest conditions to create more complex logic. When using custom keys, they must be consistent throughout the structure:

```python
# Using default keys
config_default = {
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

# Using custom keys
config_custom = {
    "api_rate_limit": {
        "@rules": {
            "@default": 100,
            "premium_user": {
                "@default": 500,
                "high_usage_period": 1000
            }
        }
    }
}

def predicate_evaluator(predicate):
    conditions = {
        "premium_user": True,
        "high_usage_period": False
    }
    return conditions.get(predicate, False)

# Choose your preferred key style
settings = PredicatorDict(
    config_custom, 
    predicate_evaluator,
    specific_key="@rules",
    generic_key="@default"
)
rate_limit = settings["api_rate_limit"]  # Returns 500
```

### Feature Flags

Perfect for feature flag systems:

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
```

### Discord Bot Configuration

Example for Discord bot settings:

```python
config = {
    "command_prefix": {
        "specific": {
            "generic": "!",  # Default prefix
            "guild_123": {
                "generic": "?",  # Default for specific guild
                "premium_tier_3": "$"  # Special prefix for premium tier
            }
        }
    }
}
```

## How It Works

1. When accessing a configuration value, Predicator checks if it contains a "specific" structure
2. The "generic" key provides the default value if no conditions match
3. Other keys in the "specific" dictionary are treated as predicates
4. Predicates are evaluated using the provided predicate_evaluator function
5. Nested predicates create AND logic (all conditions must be true)
6. The most specific matching value is returned

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
