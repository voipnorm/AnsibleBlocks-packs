import copy
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from generate_registry import generate_registry
from generate_pack import option_to_field, generate_module, generate_pack
from validate_packs import validate_pack, validate_repository
from apply_overlay import apply_overlay


class DeliveryTests(unittest.TestCase):
    def setUp(self):
        self.pack = json.loads((ROOT / 'packs/voipnorm-roomos.json').read_text())

    def test_repository_contract(self):
        # Source may advance beyond the last published release. Validate a
        # candidate manifest without advertising unpublished assets on main.
        with tempfile.TemporaryDirectory() as directory:
            candidate = Path(directory) / 'registry.json'
            candidate.write_text(json.dumps(generate_registry(ROOT / 'packs', 'voipnorm/AnsibleBlocks-packs', 'v0.0.0')))
            validate_repository(ROOT, candidate)

    def test_source_validation_does_not_publish_or_rewrite_registry(self):
        published = (ROOT / 'registry.json').read_bytes()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'packs').mkdir()
            updated = copy.deepcopy(self.pack)
            updated['modules'][0]['tooltip'] = 'Unpublished source change'
            (root / 'packs/voipnorm-roomos.json').write_text(json.dumps(updated))
            (root / 'suite-compatibility.json').write_bytes((ROOT / 'suite-compatibility.json').read_bytes())
            candidate = root / 'candidate.json'
            candidate.write_text(json.dumps(generate_registry(root / 'packs', 'voipnorm/AnsibleBlocks-packs', 'v0.0.0')))
            validate_repository(root, candidate)
        self.assertEqual((ROOT / 'registry.json').read_bytes(), published)

    def test_rejects_malicious_ids_and_paths(self):
        for value in ['../escape', 'index', '/absolute']:
            pack = copy.deepcopy(self.pack)
            pack['id'] = value
            with self.assertRaises(Exception):
                validate_pack(pack)
        for value in ['__proto__.x', 'constructor.prototype.x', 'x[999999999].y']:
            pack = copy.deepcopy(self.pack)
            pack['modules'][0]['fields'][0]['yamlPath'] = value
            with self.assertRaises(Exception):
                validate_pack(pack)

    def test_registry_matches_exact_asset_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            packs = Path(directory)
            raw = json.dumps(self.pack).encode()
            (packs / 'voipnorm-roomos.json').write_bytes(raw)
            entry = generate_registry(packs, 'voipnorm/AnsibleBlocks-packs', 'v1.5.0')['packs'][0]
            self.assertEqual(entry['sha256'], hashlib.sha256(raw).hexdigest())
            self.assertEqual(entry['size'], len(raw))
            self.assertEqual(entry['downloadUrl'], 'https://github.com/voipnorm/AnsibleBlocks-packs/releases/download/v1.5.0/voipnorm-roomos.json')

    def test_registry_rejects_tag_injection_and_mismatched_filename(self):
        with tempfile.TemporaryDirectory() as directory:
            packs = Path(directory)
            with self.assertRaises(ValueError):
                generate_registry(packs, 'owner/repo', 'v1.0.0"; echo injected')
            (packs / 'different.json').write_text(json.dumps(self.pack))
            with self.assertRaises(ValueError):
                generate_registry(packs, 'owner/repo', 'v1.0.0')

    def test_boolean_defaults_and_field_ids(self):
        field = option_to_field('free-form', {'type': 'bool', 'default': 'false'})
        self.assertFalse(field['default'])
        self.assertEqual(field['fieldId'], 'FREE_FORM')

    def test_generator_rejects_unsafe_collection_before_running_tools(self):
        with self.assertRaises(ValueError):
            generate_pack('../escape', '#123456')

    def test_wrapped_fields_get_distinct_ids_and_unset_defaults(self):
        result = generate_module('test.custom.module', {'doc': {'options': {
            'state': {'type': 'str', 'choices': ['present', 'absent'], 'default': 'none'},
            'config': {'type': 'dict', 'suboptions': {'state': {'type': 'str'}, 'free-form': {'type': 'str'}}},
        }}})
        ids = [field['fieldId'] for field in result['fields']]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertIn('TOP_STATE', ids)
        self.assertIn('FREE_FORM', ids)
        self.assertNotIn('default', result['fields'][0])
        self.assertTrue(result['supportsRawParams'])

    def test_overlay_reordering_keeps_duplicate_yaml_keys(self):
        pack = copy.deepcopy(self.pack)
        module = pack['modules'][0]
        field = copy.deepcopy(module['fields'][0])
        field['fieldId'] += '_OTHER'
        field['topLevel'] = True
        module['fields'].append(field)
        result = apply_overlay(pack, {'modules': {module['fqcn']: {'fieldOrder': [field['key']]}}})
        self.assertEqual(len(result['modules'][0]['fields']), len(module['fields']))

    def test_overlay_does_not_mutate_original(self):
        original = copy.deepcopy(self.pack)
        result = apply_overlay(self.pack, {'name': 'Changed'})
        self.assertEqual(self.pack, original)
        self.assertEqual(result['name'], 'Changed')


if __name__ == '__main__':
    unittest.main()
