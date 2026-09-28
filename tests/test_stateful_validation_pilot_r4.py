import copy
import unittest
from lib import stateful_validation_pilot_r4 as r4

class GenerationIdentityRepairTests(unittest.TestCase):
    def test_original_actual_manifest_and_twelve_fixtures_are_retained(self):
        r4.validate_generation_manifest(r4.p.read(r4.GEN))
        _,record=r4.original_artifacts()
        self.assertEqual(len(record['rows']),12)
        self.assertEqual(sum(len(r['audit']['requests']) for r in record['rows']),25)

    def test_wrong_stage_item_and_canonical_bindings_fail(self):
        original=r4.p.read(r4.GEN)
        mutations=[('item_id','other'),('stage','EXECUTION')]
        for key,value in mutations:
            changed=copy.deepcopy(original); changed[key]=value
            with self.assertRaises(ValueError): r4.validate_generation_manifest(changed)
        for key in ['contract','source','scientific_review','tooling_review']:
            changed=copy.deepcopy(original); changed[key]['sha256']='0'*64
            with self.assertRaises(ValueError): r4.validate_generation_manifest(changed)
        changed=copy.deepcopy(original); changed['tooling']=changed['tooling'][:-1]
        with self.assertRaises(ValueError): r4.validate_generation_manifest(changed)
        changed=copy.deepcopy(original); changed['cells'].reverse()
        with self.assertRaises(ValueError): r4.validate_generation_manifest(changed)
        changed=copy.deepcopy(original); changed['extra']=True
        with self.assertRaises(ValueError): r4.validate_generation_manifest(changed)

    def test_adoption_inventory_and_no_regeneration(self):
        original=r4.adoption_value(); r4.validate_adoption_manifest(original)
        for key in ['compile_result','original_generation','original_artifact_audit','incident']:
            changed=copy.deepcopy(original); changed[key]['sha256']='0'*64
            with self.assertRaises(ValueError): r4.validate_adoption_manifest(changed)
        changed=copy.deepcopy(original); changed['fixtures'][0]['sha256']='0'*64
        with self.assertRaises(ValueError): r4.validate_adoption_manifest(changed)
        with self.assertRaises(ValueError): r4.p.generate()

if __name__=='__main__': unittest.main()
