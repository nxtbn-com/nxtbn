try:
    from nxtbn.plugins.sources.currency_Backend import plugin as currency_Backend
except (ImportError, ModuleNotFoundError):
    from nxtbn.core.currency.abstract_base_currency import CurrencyBackend as currency_Backend
    

if not currency_Backend:
    raise ImportError("Currency backend could not be initialized. Please check your plugin.")
