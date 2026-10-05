# Electra Smart Integration Fix — `KeyError: 'deviceToken'`

> **This is a fork / derivative work** of the `electrasmart` integration from [home-assistant/core](https://github.com/home-assistant/core/tree/2026.9.4/homeassistant/components/electrasmart) (version 2026.9.4), distributed under the same license — **Apache License 2.0** (see [LICENSE](LICENSE) and [NOTICE](NOTICE)). Most files are an **unmodified** copy of the original; only `__init__.py` was changed, and the change is documented at the top of that file as required by the license.

## The problem

Since late September 2026, many users of the **Electra Smart** integration in Home Assistant have reported that all their AC units become `unavailable` and fail to reload, with the following error in the log:

```
KeyError: 'deviceToken'
File ".../electrasmart/device/__init__.py", line 20, in __init__
    self.token: str = data["deviceToken"]
```

**Root cause:** Electra's public API (`GET_DEVICES`) stopped returning a `deviceToken` field for some devices. The `pyElectra` library the integration depends on doesn't handle this gracefully and crashes — and that single crash takes down the **entire** account (all AC units, not just the affected one).

Also reported in the Israeli community ([Facebook post](https://www.facebook.com/groups/homeassistant.co.il)) and on the official GitHub:
- https://github.com/home-assistant/core/issues/183846
- https://github.com/home-assistant/core/issues/183829

**Status (as of 2026-10-05):** An official fix is in progress but **not yet merged** — [home-assistant/core PR #184187](https://github.com/home-assistant/core/pull/184187) switches the integration to a maintained fork of the client library. Until that PR is merged and released, the custom integration below is the only working fix.

## The fix

This is a local copy (`custom_components`) of the official integration, identical to the original source (Home Assistant 2026.9.4) — **except for one targeted change**: `__init__.py` contains a monkey-patch that makes `deviceToken` an optional field instead of crashing on it. If a device is missing the token, it's registered with a log warning and keeps working (status reads and, in most cases, sending commands continue to work); all other devices on the account are unaffected.

## Installation

### Option A: via HACS (recommended)
1. In HACS → three dots at the top → **Custom repositories**
2. Paste this repo's URL, category **Integration**
3. Search for "Electra Smart (deviceToken fix)" and install
4. **Restart Home Assistant** (custom_components are not picked up by a hot reload)

### Option B: manual
1. Copy the `custom_components/electrasmart` folder from this repo to `/config/custom_components/electrasmart` on your HA server
2. Restart Home Assistant

### If the integration is already configured
No need to re-add it — just drop the files in place and restart. Your existing config entry will keep working as-is.

## Good to know

- This is a **temporary client-side workaround**, not an official fix. Once Home Assistant/Electra fix the issue in the official core release, **this custom_components will keep "winning" and shadowing the official fix** until you remove it manually:
  ```
  rm -rf /config/custom_components/electrasmart
  ```
  followed by another restart.
- It's recommended to follow the issues linked above and remove this fix once they're closed.

## Credit and licensing

- **Original code** (all files except the targeted change in `__init__.py`): Home Assistant Core, [home-assistant/core](https://github.com/home-assistant/core), integration codeowner: [@jafar-atili](https://github.com/jafar-atili). License: Apache License 2.0.
- **The change in `__init__.py`**: Itay Abramzon, 2026, under the same license (Apache 2.0) — see [NOTICE](NOTICE) for the exact details of what changed.
- This remains an **unofficial fork**, not affiliated with or endorsed by Home Assistant or Electra.
