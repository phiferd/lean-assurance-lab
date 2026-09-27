import copy
import unittest
from lib import lazy_reduction_execute as e
from lib import lazy_reduction_pilot as p

class MatrixTests(unittest.TestCase):
    def test_capability_contract_fails_on_scope_expansion(self):
        m=dict(item_id=p.ITEM,stage='CAPABILITY',cells=e.CAPABILITY_CELLS,
               artifacts={'control':e.CONTROL,'candidate':e.CANDIDATE},environment={**p.ENV,'LL_KAM_MODE':'3'},
               exact_rejection=e.REJECTION,keep_going=False,jobs=1,launch_owner='lazy_lead',timeout_seconds=120,memory_bytes=2147483648)
        e.validate_capability(m)
        for field,value in [('cells',e.CAPABILITY_CELLS*2),('jobs',2),('keep_going',True),('stage','SCIENCE'),
                            ('environment',{**p.ENV,'LL_KAM_MODE':'2'}),('artifacts',{'control':e.CONTROL})]:
            altered=copy.deepcopy(m); altered[field]=value
            with self.assertRaises(ValueError): e.validate_capability(altered)

if __name__=='__main__': unittest.main()
