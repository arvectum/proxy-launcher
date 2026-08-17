from types import SimpleNamespace

from qa.collect_macos_network_state import collect_state
from qa.compare_macos_network_state import compare_states


class FakeReadOnlyClient:
    def __init__(self):
        self.calls = []

    def list_services(self):
        self.calls.append(("list",))
        return (
            SimpleNamespace(name="Wi-Fi", enabled=True),
            SimpleNamespace(name="Disabled", enabled=False),
        )

    def get_auto_proxy(self, service):
        self.calls.append(("get_auto", service))
        return SimpleNamespace(enabled=True, url="http://127.0.0.1:8082/proxy.pac")

    def get_bypass_domains(self, service):
        self.calls.append(("get_bypass", service))
        return ("localhost", "127.0.0.1")

    def __getattr__(self, name):
        if name.startswith("set_"):
            raise AssertionError("collector must never access a network mutation method")
        raise AttributeError(name)


def test_collect_state_is_read_only_and_skips_disabled_services():
    client = FakeReadOnlyClient()
    payload = collect_state(client)

    assert payload == {
        "schema_version": 1,
        "services": {
            "Wi-Fi": {
                "auto_proxy": {
                    "enabled": True,
                    "url": "http://127.0.0.1:8082/proxy.pac",
                },
                "bypass_domains": ["localhost", "127.0.0.1"],
            }
        },
    }
    assert client.calls == [
        ("list",),
        ("get_auto", "Wi-Fi"),
        ("get_bypass", "Wi-Fi"),
    ]


def test_compare_state_accepts_bypass_order_and_case_only_changes():
    before = {
        "schema_version": 1,
        "services": {
            "Wi-Fi": {
                "auto_proxy": {"enabled": False, "url": ""},
                "bypass_domains": ["LOCALHOST", "127.0.0.1"],
            }
        },
    }
    after = {
        "schema_version": 1,
        "services": {
            "Wi-Fi": {
                "auto_proxy": {"enabled": False, "url": ""},
                "bypass_domains": ["127.0.0.1", "localhost"],
            }
        },
    }

    assert compare_states(before, after) == []


def test_compare_state_reports_owned_dimensions_and_service_set_changes():
    before = {
        "schema_version": 1,
        "services": {
            "Wi-Fi": {
                "auto_proxy": {"enabled": False, "url": "https://old/pac"},
                "bypass_domains": ["localhost"],
            }
        },
    }
    after = {
        "schema_version": 1,
        "services": {
            "Ethernet": {
                "auto_proxy": {"enabled": True, "url": "https://new/pac"},
                "bypass_domains": [],
            }
        },
    }

    differences = compare_states(before, after)
    assert "service missing after rollback: Wi-Fi" in differences
    assert "unexpected enabled service after rollback: Ethernet" in differences
