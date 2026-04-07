"""Tests for AVU-to-CKAN metadata mapping functions."""

import pytest
from kando.sync.mapping import (
    get_title, get_author, get_publication_year, get_description,
    get_license_info, get_tags, get_name_from_title, create_citation,
    get_extras, map_avus_to_ckan, clean_dataset_metadata,
)

# Sample AVU metadata dict mimicking real iRODS curated data
SAMPLE_AVUS = {
    "datacite.title": "Leaf Phenotyping Images of Maize",
    "datacite.creator": ["Alcock, J.", "Smith, B."],
    "description": "High-resolution images of maize leaves under drought stress.",
    "datacite.publicationyear": "2016",
    "identifier": "10.7946/P2BC78",
    "identifierType": "DOI",
    "publicationYear": "2016",
    "publisher": "CyVerse Data Commons",
    "rights": "ODC PDDL",
    "subject": ["maize", "phenotyping", "drought stress"],
    "contributor": ["CyVerse", "iPlant"],
    "resourceType": "Dataset",
    "version": "1.0",
    "date_created": "2016-05-10 10:00:00",
    "date_modified": "2020-02-20 22:05:33",
    "de_path": "/iplant/home/shared/commons_repo/curated/Alcock_leafPhenotypingImages_2016",
}


class TestGetTitle:
    def test_datacite_title(self):
        assert get_title(SAMPLE_AVUS) == "Leaf Phenotyping Images of Maize"

    def test_title_key(self):
        assert get_title({"title": "My Dataset"}) == "My Dataset"

    def test_title_as_list(self):
        assert get_title({"title": ["Part A", "Part B"]}) == "Part A, Part B"

    def test_missing_title_raises(self):
        with pytest.raises(KeyError):
            get_title({"description": "no title here"})


class TestGetAuthor:
    def test_list_creators(self):
        assert get_author(SAMPLE_AVUS) == "Alcock, J., Smith, B."

    def test_string_creator(self):
        assert get_author({"datacite.creator": "Jane Doe"}) == "Jane Doe"

    def test_missing_raises(self):
        with pytest.raises(KeyError):
            get_author({"description": "nothing"})


class TestGetPublicationYear:
    def test_string_year(self):
        assert get_publication_year({"datacite.publicationyear": "2016"}) == "2016"

    def test_list_year(self):
        assert get_publication_year({"datacite.publicationyear": ["2016", ""]}) == "2016"

    def test_four_char_truncation(self):
        assert get_publication_year({"datacite.publicationyear": "20160101"}) == "2016"


class TestGetDescription:
    def test_description(self):
        assert "images" in get_description(SAMPLE_AVUS).lower()

    def test_missing_raises(self):
        with pytest.raises(KeyError):
            get_description({"title": "no desc"})


class TestGetLicenseInfo:
    def test_odc_pddl(self):
        info = get_license_info({"rights": "ODC PDDL"})
        assert info["license_id"] == "odc-pddl"

    def test_cc_zero(self):
        info = get_license_info({"rights": "CC0 1.0"})
        assert info["license_id"] == "cc-zero"

    def test_unknown(self):
        info = get_license_info({"rights": "Some Other License"})
        assert info["license_id"] == "notspecified"

    def test_no_rights(self):
        info = get_license_info({})
        assert info["license_id"] == "notspecified"


class TestGetTags:
    def test_list_subjects(self):
        tags = get_tags(SAMPLE_AVUS)
        names = [t["name"] for t in tags]
        assert "maize" in names
        assert "phenotyping" in names

    def test_string_subject(self):
        tags = get_tags({"subject": "biology, ecology"})
        names = [t["name"] for t in tags]
        assert "biology" in names
        assert "ecology" in names

    def test_no_subject(self):
        assert get_tags({}) == []


class TestGetNameFromTitle:
    def test_basic(self):
        assert get_name_from_title("My Cool Dataset") == "my_cool_dataset"

    def test_special_chars(self):
        name = get_name_from_title("Data (v2.0) & More!")
        assert "(" not in name
        assert "&" not in name

    def test_truncation(self):
        long_title = "A" * 200
        assert len(get_name_from_title(long_title)) == 100


class TestCreateCitation:
    def test_citation_format(self):
        citation = create_citation(SAMPLE_AVUS)
        assert "Alcock" in citation
        assert "2016" in citation
        assert "CyVerse Data Commons" in citation
        assert "DOI 10.7946/P2BC78" in citation


class TestCleanDatasetMetadata:
    def test_removes_tabs(self):
        data = {"title": "Hello\tWorld", "tags": ["one\ttwo", "three"]}
        cleaned = clean_dataset_metadata(data)
        assert "\t" not in cleaned["title"]
        assert "\t" not in cleaned["tags"][0]


class TestMapAvusToCkan:
    def test_full_mapping(self):
        result = map_avus_to_ckan(SAMPLE_AVUS.copy())
        assert result["title"] == "Leaf Phenotyping Images of Maize"
        assert result["author"] == "Alcock, J., Smith, B."
        assert result["owner_org"] == "cyverse"
        assert result["license_id"] == "odc-pddl"
        assert result["version"] == "1.0"
        assert any(g["name"] == "cyverse-curated" for g in result["groups"])
        assert any(t["name"] == "maize" for t in result["tags"])
        # Extras should contain Citation
        extra_keys = [e["key"] for e in result["extras"]]
        assert "Citation" in extra_keys


class TestGetExtras:
    def test_extras_exclude_core_fields(self):
        extras = get_extras(SAMPLE_AVUS)
        extra_keys = [e["key"] for e in extras]
        assert "title" not in extra_keys
        assert "description" not in extra_keys
        assert "creator" not in extra_keys
        assert "Citation" in extra_keys
        assert "contributor" in extra_keys
