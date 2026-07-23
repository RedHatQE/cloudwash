# Dry Data Refactor

This document summarizes the refactor of Cloudwash's "dry data" tracking (the
in-memory record of resources that are eligible for deletion/stop/skip during a
`--dry-run`) and the centralization of its printing/reporting logic.

## Motivation

Previously, `dry_data` was a single module-level dictionary in `cloudwash/utils.py`,
shared by every provider and resource entity via a plain `from cloudwash.utils import
dry_data` import. This had a few problems:

- **Duplicate instantiation**: every resource entity (`CleanVMs`, `CleanDiscs`, ...)
  reached into the same module-level dict directly, so there was no single owner of
  the dry data's lifecycle.
- **Cross-region/zone leakage risk**: providers that iterate over multiple
  regions/zones (AWS, Azure, GCE) reset the dict in-place between iterations
  (`dry_data[items]['delete'] = []`). Sub-lists like `VMS.stop` and `VMS.skip` were
  never reset, so stale entries from a previous region could leak into the next
  region's dry-run report.
- **Repeated printing boilerplate**: every provider's `cleanup()` had its own
  `if is_dry_run: echo_dry(dry_data); all_data.append(deepcopy(dry_data))` block.

## Changes

### 1. `DryData` class (`cloudwash/utils.py`)

The module-level `dry_data` dict was replaced with a `DryData` class that
encapsulates the same structure (`VMS`, `CONTAINERS`, `DISCS`, `NICS`, `PIPS`,
`OCPS`, `RESOURCES`, `STACKS`, `IMAGES`, `PROVIDER`, `REGION`, `GROUP`, `ZONE`):

```python
class DryData:
    def __init__(self):
        self._data = {...}  # same layout as the old module-level dict

    def __getitem__(self, key): ...
    def __setitem__(self, key, value): ...
    def get(self, key, default=None): ...
    def update(self, other_dict): ...
    def reset_resource(self, resource_key): ...
    def to_dict(self): ...
```

`__getitem__`/`__setitem__` keep the existing `dry_data['VMS']['delete']` call
sites working unchanged, so no consumer needed dict-vs-object gymnastics.

Each provider's `cleanup()` now creates its **own** `DryData()` instance and passes
it down to the provider/resource entities instead of relying on a shared singleton.
This means concurrent/sequential regions or zones (and, in principle, concurrent
provider runs) never share mutable state.

### 2. `reset_resource()` clears every sub-list, not just `delete`

The old reset logic only cleared `delete`:

```python
dry_data[items]['delete'] = []
```

`stop`/`skip` (used by `VMS` and `CONTAINERS`) were never cleared between
regions/zones. `DryData.reset_resource()` now clears every sub-key of a resource:

```python
def reset_resource(self, resource_key):
    if resource_key in self._data:
        for sub_key in self._data[resource_key]:
            self._data[resource_key][sub_key] = []
```

This is what actually guarantees two regions/zones can't conflict or repeat
resources in the dry-run output; it's covered by
`tests/test_dry_data.py::test_dry_data_reset_resource_clears_every_sub_list`.

### 3. `dry_data` propagated through entities instead of re-imported

- `cloudwash/entities/providers.py`: `providerCleanup.__init__` now accepts an
  optional `dry_data` and stores it as `self.dry_data`; every resource property
  (`vms`, `discs`, `nics`, `pips`, `images`, `stacks`, `ocps`, `containers`) passes
  `dry_data=self.dry_data` down to the resource-entity constructor. The
  `AzureCleanup`/`AWSCleanup`/`GCECleanup`/`VMWareCleanup`/`PodmanCleanup`
  subclasses no longer need to redeclare an identical `__init__`.
- `cloudwash/entities/resources/*.py` (`vms.py`, `discs.py`, `nics.py`, `pips.py`,
  `images.py`, `stacks.py`, `ocps.py`, `containers.py`): each `Clean*` class now
  accepts `dry_data=None` and falls back to its own `DryData()` if not provided
  (keeps the class usable standalone, e.g. in unit tests), using `self.dry_data`
  in `_set_dry()` instead of the removed module-level import.

### 4. Centralized dry-data printing: `print_dry_data()`

Every provider previously repeated:

```python
if is_dry_run:
    echo_dry(dry_data)
    all_data.append(deepcopy(dry_data))
```

This is now a single utility function:

```python
def print_dry_data(dry_data, is_dry_run, all_data):
    """Centralized function to print dry data and append it to all_data if in dry run mode."""
    if is_dry_run:
        echo_dry(dry_data.to_dict())
        all_data.append(deepcopy(dry_data.to_dict()))
```

`cloudwash/providers/{aws,azure,gce,podman,vmware}.py` all call
`print_dry_data(dry_data, is_dry_run, all_data)` at the end of each
region/zone/group iteration instead of duplicating the check/echo/append logic.

### 5. `resourcewise_data()` / `echo_dry()` operate on plain dicts

`resourcewise_data()` is invoked both with dry-run snapshots (plain dicts stored in
`all_data`) and from `create_html()` (also plain dicts). It no longer assumes its
argument is a `DryData` instance; it treats `dry_data` as the plain dict produced by
`DryData.to_dict()`, with `None` falling back to a fresh `DryData().to_dict()`.

## Tests (`tests/test_dry_data.py`)

- `test_dry_data_initialization` / `test_dry_data_update` / `test_dry_data_to_dict`:
  basic `DryData` behavior.
- `test_dry_data_instances_are_independent`: two `DryData()` instances don't share
  state.
- `test_dry_data_reset_resource_clears_every_sub_list`: `reset_resource` clears
  `delete`/`stop`/`skip` together.
- `test_separate_regions_do_not_conflict_or_repeat` and
  `test_no_resources_missing_across_regions`: simulate the exact region-loop
  pattern used by `cloudwash/providers/aws.py` (reuse one `DryData` instance,
  `reset_resource()` between regions, capture snapshots via `print_dry_data()`),
  then assert:
  - each captured snapshot only contains that region's resources (no
    conflicting/repeating resources between regions), and
  - the union of all snapshots contains every resource from every region (nothing
    is silently dropped from the cleanup/dry-data output).

## Requirements satisfied

- [x] Introduced a `DryData` class and instantiate/pass it explicitly wherever
      dry data is read or written, removing the shared module-level singleton.
- [x] Removed duplicate `DryData`/dry-data-dict instantiation across providers and
      resource entities by threading a single instance through
      `providerCleanup` → resource entities.
- [x] Centralized the repeated dry-run printing/reporting logic into
      `print_dry_data()`, used identically by all five providers.
- [x] Fixed the underlying region/zone isolation bug (`reset_resource` not
      clearing `stop`/`skip`) that could have caused conflicting/repeated
      entries across regions or zones.
- [x] Added tests verifying two regions/zones produce disjoint, non-repeating
      dry data and that no resource is missing from the aggregated cleanup/dry
      data output.
