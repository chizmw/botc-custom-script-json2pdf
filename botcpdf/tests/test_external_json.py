"""Tests to make sure that the external JSON data we use is processed
correctly."""

import json
import os

from botcpdf.roledata import RoleData

DATA_FILE = "data/imported/roles-combined.json"


class TestJsonData:
    """Tests for the contents of the external JSON data."""

    def test_data_file_exists(self):
        """Test that the data file exists."""
        assert os.path.exists(DATA_FILE)

    def test_top_level_keys(self):
        """Test that the top-level keys in the data file are as expected."""

        # open the data file
        with open(DATA_FILE, "r", encoding="utf-8") as data_file:
            # load the data
            data = json.load(data_file)
            # check that the keys are as expected
            assert set(data.keys()) == set(
                [
                    "character_by_id",
                    "editions",
                    "jinxes",
                    "role_list",
                    "teams",
                ]
            )

    def test_some_values(self):
        """Test that some of the values in the data file are as expected."""

        # open the data file
        with open(DATA_FILE, "r", encoding="utf-8") as data_file:
            # load the data
            data = json.load(data_file)
            # check that the values are as expected

            # we expect DAWN, DEMON, DUSK, acrobat, highpriestess, knight,
            # vizier, recluse as a subset of the keys in character_by_id; we
            # don't care about extra keys, we're just looking for these ones
            # for now
            assert set(
                [
                    "DAWN",
                    "DEMON",
                    "DUSK",
                    "acrobat",
                    "highpriestess",
                    "knight",
                    "recluse",
                    "vizier",
                ]
            ).issubset(set(data["character_by_id"].keys()))

            # we expect _exactly_ these keys in editions
            # "", "_meta" "bmr" "ks" "snv" "tb"
            assert set(["experimental", "_meta", "bmr", "ks", "snv", "tb"]) == set(
                data["editions"].keys()
            )

            # some of the keys in the experimental edition are: acrobat, goblin,
            # highpriestess, organgrinder, widow
            assert set(
                [
                    "acrobat",
                    "goblin",
                    "highpriestess",
                    "organgrinder",
                    "widow",
                ]
            ).issubset(set(data["editions"]["experimental"].keys()))

            # some of the keys in the _meta edition are: DAWN, DEMON, DUSK,
            # MINION
            assert set(["DAWN", "DEMON", "DUSK", "MINION"]).issubset(
                set(data["editions"]["_meta"].keys())
            )

            # some of the keys in the bmr edition are: assassin, bishop, fool,
            # gambler, po, voudon
            assert set(
                ["assassin", "bishop", "fool", "gambler", "po", "voudon"]
            ).issubset(set(data["editions"]["bmr"].keys()))

            # some of the keys in the ks edition are: atheist, boomdandy,
            # damsel, farmer
            assert set(["atheist", "boomdandy", "damsel", "farmer"]).issubset(
                set(data["editions"]["ks"].keys())
            )

            # some of the keys in the snv edition are: artist, barber, barista,
            # klutz, mutant, nodashii
            assert set(
                [
                    "artist",
                    "barber",
                    "barista",
                    "klutz",
                    "mutant",
                    "nodashii",
                ]
            ).issubset(set(data["editions"]["snv"].keys()))

            # some of the keys in the tb edition are: baron, beggar, butler,
            # chef, spy, imp, bureaucrat
            assert set(
                [
                    "baron",
                    "beggar",
                    "butler",
                    "chef",
                    "spy",
                    "imp",
                    "bureaucrat",
                ]
            ).issubset(set(data["editions"]["tb"].keys()))

            # every edition should have a "_meta" key
            for edition in data["editions"]:
                assert "_meta" in data["editions"][edition]

            # each entry in editions that's NOT _meta should have id, name, physicaltoken keys
            for edition in data["editions"]:
                for role in data["editions"][edition]:
                    if role != "_meta":
                        assert "id" in data["editions"][edition][role]
                        assert "name" in data["editions"][edition][role]
                        assert "physicaltoken" in data["editions"][edition][role]

    def test_processed_data(self):
        """Test that the object/class data is processed as expected."""

        # get a RoleData object

        role_data = RoleData()

        # looking at the RoleData object, we expect roles to be in the expected edition
        test_data = [
            {
                "role_id": "acrobat",
                "expected_edition": "experimental",
            },
            {
                "role_id": "damsel",
                "expected_edition": "ks",
            },
            {
                "role_id": "vizier",
                "expected_edition": "experimental",
            },
        ]

        # for each role in the test data, get the role object and check that
        # the data is as expected
        for test in test_data:
            role = role_data.get_role(test["role_id"])
            assert (
                role.edition == test["expected_edition"]
            ), f"role: {role} does not have expected edition: {test['expected_edition']}"
