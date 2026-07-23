import unittest

from cloudwash.constants import aws_data
from cloudwash.utils import DryData
from cloudwash.utils import print_dry_data
from cloudwash.utils import resourcewise_data


class TestDryData(unittest.TestCase):
    def setUp(self):
        self.dry_data = DryData()

    def test_dry_data_initialization(self):
        self.assertEqual(self.dry_data['PROVIDER'], '')
        self.assertEqual(self.dry_data['REGION'], '')
        self.assertEqual(self.dry_data['GROUP'], '')
        self.assertEqual(self.dry_data['ZONE'], '')
        self.assertEqual(self.dry_data['VMS'], {'delete': [], 'stop': [], 'skip': []})
        self.assertEqual(self.dry_data['CONTAINERS'], {'delete': [], 'stop': [], 'skip': []})
        for resource in ('DISCS', 'NICS', 'IMAGES', 'PIPS', 'RESOURCES', 'STACKS', 'OCPS'):
            self.assertEqual(self.dry_data[resource], {'delete': []})

    def test_dry_data_update(self):
        self.dry_data['PROVIDER'] = 'AWS'
        self.dry_data['REGION'] = 'us-west-2'
        self.assertEqual(self.dry_data['PROVIDER'], 'AWS')
        self.assertEqual(self.dry_data['REGION'], 'us-west-2')

    def test_dry_data_reset_resource_clears_every_sub_list(self):
        # A resource like VMS has delete/stop/skip sub-lists that must all be cleared,
        # otherwise stale VMs from a previous region/zone would leak into the next one.
        self.dry_data['VMS']['delete'] = ['vm1']
        self.dry_data['VMS']['stop'] = ['vm2']
        self.dry_data['VMS']['skip'] = ['vm3']

        self.dry_data.reset_resource('VMS')

        self.assertEqual(self.dry_data['VMS'], {'delete': [], 'stop': [], 'skip': []})

    def test_dry_data_to_dict(self):
        self.dry_data['PROVIDER'] = 'AWS'
        self.dry_data['REGION'] = 'us-west-2'
        data_dict = self.dry_data.to_dict()
        self.assertEqual(data_dict['PROVIDER'], 'AWS')
        self.assertEqual(data_dict['REGION'], 'us-west-2')

    def test_dry_data_instances_are_independent(self):
        dry_data1 = DryData()
        dry_data1['VMS']['delete'] = ['vm1', 'vm2']

        dry_data2 = DryData()
        dry_data2['VMS']['delete'] = ['vm3', 'vm4']

        self.assertNotEqual(dry_data1['VMS']['delete'], dry_data2['VMS']['delete'])

    def _simulate_region_loop(self, regions_vms):
        """Mirrors the region loop in `cloudwash.providers.aws.cleanup`: a single DryData
        instance is reused, reset per region, and each region's snapshot is captured via
        `print_dry_data`, exactly as it happens for every real provider."""
        all_data = []
        for region, vms in regions_vms.items():
            self.dry_data['REGION'] = region
            for resource in aws_data:
                self.dry_data.reset_resource(resource)
            self.dry_data['VMS'].update(vms)
            print_dry_data(self.dry_data, is_dry_run=True, all_data=all_data)
        return all_data

    def test_separate_regions_do_not_conflict_or_repeat(self):
        regions_vms = {
            'us-east-1': {'delete': ['vm-1'], 'stop': ['vm-2'], 'skip': ['vm-3']},
            'us-west-2': {'delete': ['vm-4'], 'stop': ['vm-5'], 'skip': ['vm-6']},
        }
        all_data = self._simulate_region_loop(regions_vms)

        self.assertEqual(len(all_data), len(regions_vms))
        for snapshot, (region, vms) in zip(all_data, regions_vms.items()):
            self.assertEqual(snapshot['REGION'], region)
            self.assertEqual(snapshot['VMS'], vms)

        east_vms = set(sum(all_data[0]['VMS'].values(), []))
        west_vms = set(sum(all_data[1]['VMS'].values(), []))
        self.assertTrue(east_vms.isdisjoint(west_vms), "VMs from different regions must not repeat")

    def test_no_resources_missing_across_regions(self):
        regions_vms = {
            'us-east-1': {'delete': ['vm-1'], 'stop': ['vm-2'], 'skip': ['vm-3']},
            'us-west-2': {'delete': ['vm-4'], 'stop': ['vm-5'], 'skip': ['vm-6']},
        }
        all_data = self._simulate_region_loop(regions_vms)

        reported_vms = set()
        for snapshot in all_data:
            resource_view = resourcewise_data(snapshot)
            reported_vms.update(resource_view['deletable_vms'])
            reported_vms.update(resource_view['stopable_vms'])
            reported_vms.update(resource_view['skipped_vms'])

        expected_vms = {vm for vms in regions_vms.values() for vm_list in vms.values() for vm in vm_list}
        self.assertEqual(reported_vms, expected_vms, "No VM should be dropped from the dry data output")


if __name__ == '__main__':
    unittest.main()
