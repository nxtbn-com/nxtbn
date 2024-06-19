try:
    from nxtbn.plugins.sources import currency_Backend
except ImportError:
    from nxtbn.core.currency.abstract_base_currency import CurrencyBackend as currency_Backend


if not currency_Backend:
    raise ImportError("Currency backend could not be initialized. Please check your plugin.")
