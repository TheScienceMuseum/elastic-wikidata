from elastic_wikidata import wd_entities
import pytest


@pytest.fixture
def ge():
    ge = wd_entities.get_entities()

    return ge


def test_get_all_results(ge):
    qids = ["Q203545", "Q706475", "Q18637243"]

    res = ge.get_all_results(qids, timeout=6)

    assert isinstance(res, list)
    assert len(res) == len(qids)
    assert [item["id"] for item in res] == qids


def test_get_labels(ge):
    qids = ["Q203545", "Q706475", "Q18637243", "Q82340"]

    label_dict = ge.get_labels(qids, timeout=6)

    # the last QID has no english label so a blank string is returned as its value
    assert label_dict == {
        "Q18637243": "Michaela Coel",
        "Q203545": "Michael Gambon",
        "Q706475": "Steve McQueen",
        "Q82340": "",
    }


def test_simplify_wbgetentities_result(ge):
    res = ge.get_all_results(["Q203545", "Q706475", "Q18637243"])
    pids = ["P31", "P21", "P735", "P734", "P1971"]

    res_simplified = [
        wd_entities.simplify_wbgetentities_result(doc, lang="en", properties=pids)
        for doc in res
    ]

    assert [doc["claims"]["P31"] == ["Q5"] for doc in res_simplified]
    assert res_simplified[1]["claims"]["P1971"][0] == "+2"
