# coding: utf-8
# Copyright (c) Pymatgen Development Team.
# Distributed under the terms of the MIT License.

from __future__ import unicode_literals

import unittest2 as unittest

import os

import numpy as np

from pymatgen.io.feff.inputs import Atoms, Header, Tags, Potential
from pymatgen.io.cif import CifParser


test_dir = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..",
                        'test_files')

header_string = """* This FEFF.inp file generated by pymatgen
TITLE comment: From cif file
TITLE Source:  CoO19128.cif
TITLE Structure Summary:  Co2 O2
TITLE Reduced formula:  CoO
TITLE space group: (Cmc2_1), space number:  (36)
TITLE abc:  3.297078   3.297078   5.254213
TITLE angles: 90.000000  90.000000 120.000000
TITLE sites: 4
* 1 Co     0.666666     0.333332     0.496324
* 2 Co     0.333333     0.666667     0.996324
* 3 O     0.666666     0.333332     0.878676
* 4 O     0.333333     0.666667     0.378675"""


class HeaderTest(unittest.TestCase):

    def test_init(self):
        filepath = os.path.join(test_dir, 'HEADER')
        header = Header.header_string_from_file(filepath)
        h = header.splitlines()
        hs = header_string.splitlines()
        for i, line in enumerate(h):
            self.assertEqual(line, hs[i])
        self.assertEqual(header_string.splitlines(), header.splitlines(),
                         "Failed to read HEADER file")

    def test_from_string(self):
        header = Header.from_string(header_string)
        self.assertEqual(header.struct.composition.reduced_formula, "CoO",
                         "Failed to generate structure from HEADER string")

    def test_get_string(self):
        cif_file = os.path.join(test_dir, 'CoO19128.cif')
        h = Header.from_cif_file(cif_file)
        head = str(h)
        self.assertEqual(head.splitlines()[3].split()[-1],
                         header_string.splitlines()[3].split()[-1],
                         "Failed to generate HEADER from structure")

    def test_as_dict_and_from_dict(self):
        file_name = os.path.join(test_dir, 'HEADER')
        header = Header.from_file(file_name)
        d = header.as_dict()
        header2 = Header.from_dict(d)
        self.assertEqual(str(header), str(header2),
                         "Header failed to and from dict test")


class FeffAtomsTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        r = CifParser(os.path.join(test_dir, "CoO19128.cif"))
        structure = r.get_structures()[0]
        cls.atoms = Atoms(structure, "O", 10.0)

    def test_absorber_line(self):
        atoms_lines = self.atoms.get_lines()
        # x
        self.assertAlmostEqual(float(atoms_lines[0][0]), 0.0)
        # y
        self.assertAlmostEqual(float(atoms_lines[0][1]), 0.0)
        # z
        self.assertAlmostEqual(float(atoms_lines[0][2]), 0.0)
        # ipot
        self.assertEqual(int(atoms_lines[0][3]), 0)
        # atom symbol
        self.assertEqual(atoms_lines[0][4], 'O')
        # distance
        self.assertAlmostEqual(float(atoms_lines[0][5]), 0.0)
        # id
        self.assertEqual(int(atoms_lines[0][6]), 0)

    def test_distances(self):
        atoms_1 = self.atoms.get_lines()
        distances_1 = [float(a[5]) for a in atoms_1]
        atoms_2 = Atoms.atoms_string_from_file(os.path.join(test_dir, "ATOMS"))
        atoms_2 = atoms_2.splitlines()[3:]
        distances_2 = [float(a.split()[5]) for a in atoms_2]
        np.testing.assert_allclose(distances_1, distances_2)

    def test_atoms_from_file(self):
        filepath = os.path.join(test_dir, 'ATOMS')
        atoms = Atoms.atoms_string_from_file(filepath)
        self.assertEqual(atoms.splitlines()[3].split()[4], 'O',
                         "failed to read ATOMS file")

    def test_get_string(self):
        header = Header.from_string(header_string)
        struc = header.struct
        central_atom = 'O'
        a = Atoms(struc, central_atom, radius=10.)
        atoms = str(a)
        self.assertEqual(atoms.splitlines()[3].split()[4], central_atom,
                         "failed to create ATOMS string")

    def test_as_dict_and_from_dict(self):
        file_name = os.path.join(test_dir, 'HEADER')
        header = Header.from_file(file_name)
        struct = header.struct
        atoms = Atoms(struct, 'O', radius=10.)
        d = atoms.as_dict()
        atoms2 = Atoms.from_dict(d)
        self.assertEqual(str(atoms), str(atoms2),
                         "Atoms failed to and from dict test")

    def test_cluster_from_file(self):
        self.atoms.write_file("ATOMS_test")
        mol_1 = Atoms.cluster_from_file("ATOMS_test")
        mol_2 = Atoms.cluster_from_file(os.path.join(test_dir, "ATOMS"))
        self.assertEqual(mol_1.formula, mol_2.formula)
        self.assertEqual(len(mol_1), len(mol_2))
        os.remove("ATOMS_test")


class FeffTagsTest(unittest.TestCase):

    def test_init(self):
        filepath = os.path.join(test_dir, 'PARAMETERS')
        parameters = Tags.from_file(filepath)
        parameters["RPATH"] = 10
        self.assertEqual(parameters["COREHOLE"], "Fsr",
                         "Failed to read PARAMETERS file")
        self.assertEqual(parameters["LDOS"], [-30., 15., .1],
                         "Failed to read PARAMETERS file")

    def test_diff(self):
        filepath1 = os.path.join(test_dir, 'PARAMETERS')
        parameters1 = Tags.from_file(filepath1)
        filepath2 = os.path.join(test_dir, 'PARAMETERS.2')
        parameters2 = Tags.from_file(filepath2)
        self.assertEqual(Tags(parameters1).diff(parameters2),
                         {'Different': {},
                          'Same': {'CONTROL': [1, 1, 1, 1, 1, 1],
                                   'MPSE': [2],
                                   'OPCONS': '',
                                   'SCF': [6.0, 0, 30, .2, 1],
                                   'EXCHANGE': [0, 0.0, 0.0, 2],
                                   'S02': [0.0],
                                   'COREHOLE': 'Fsr',
                                   'FMS': [8.5, 0],
                                   'XANES': [3.7, 0.04, 0.1],
                                   'EDGE': 'K',
                                   'PRINT': [1, 0, 0, 0, 0, 0],
                                   'LDOS': [-30., 15., .1]}})

    def test_as_dict_and_from_dict(self):
        file_name = os.path.join(test_dir, 'PARAMETERS')
        tags = Tags.from_file(file_name)
        d=tags.as_dict()
        tags2 = Tags.from_dict(d)
        self.assertEqual(tags, tags2,
                         "Parameters do not match to and from dict")


class FeffPotTest(unittest.TestCase):

    def test_init(self):
        filepath = os.path.join(test_dir, 'POTENTIALS')
        feffpot = Potential.pot_string_from_file(filepath)
        d, dr = Potential.pot_dict_from_string(feffpot)
        self.assertEqual(d['Co'], 1, "Wrong symbols read in for Potential")

    def test_as_dict_and_from_dict(self):
        file_name = os.path.join(test_dir, 'HEADER')
        header = Header.from_file(file_name)
        struct = header.struct
        pot = Potential(struct, 'O')
        d=pot.as_dict()
        pot2 = Potential.from_dict(d)
        self.assertEqual(str(pot), str(pot2),
                         "Potential to and from dict does not match")


if __name__ == '__main__':
    unittest.main()
