import requests
import random
import pytest

BASE = "https://qa-internship.avito.com"


def create_item(data):
	return requests.post(BASE + "/api/1/item", json=data)


def get_item(item_id):
	return requests.get(f"{BASE}/api/1/item/{item_id}")


def get_items_by_seller(seller):
	return requests.get(f"{BASE}/api/1/{seller}/item")


def get_stat(item_id):
	return requests.get(f"{BASE}/api/1/statistic/{item_id}")


import random

@pytest.fixture(scope="module")
def seller_and_items():
    seller = random.randint(111111, 999999)
    ids = []
    r = create_item({"sellerID": seller, "name": "Тестовое объявление", "price": 1000, "statistics": {"likes": 0, "viewCount": 0, "contacts": 0}})
    assert r.status_code == 200
    j = r.json()
    ids.append(j.get("id"))
    r2 = create_item({"sellerID": seller, "name": "Тестовое объявление 2", "price": 2000, "statistics": {"likes": 1, "viewCount": 2, "contacts": 0}})
    assert r2.status_code == 200
    j2 = r2.json()
    ids.append(j2.get("id"))
    return {"seller": seller, "ids": ids, "first": j, "second": j2}


def test_TC_001_create_correct(seller_and_items):
	j = seller_and_items["first"]
	assert "id" in j
	assert j.get("sellerId") == seller_and_items["seller"]
	assert j.get("name") == "Тестовое объявление"
	assert isinstance(j.get("price"), int)
	assert isinstance(j.get("statistics"), dict)
	assert "createdAt" in j


def test_TC_002_create_multiple_same_seller(seller_and_items):
	ids = seller_and_items["ids"]
	assert len(ids) >= 2
	assert ids[0] != ids[1]
	# check sellerId for both
	r0 = get_item(ids[0])
	r1 = get_item(ids[1])
	assert r0.status_code == 200
	assert r1.status_code == 200
	assert r0.json().get("sellerId") == seller_and_items["seller"]
	assert r1.json().get("sellerId") == seller_and_items["seller"]


def test_TC_003_create_without_seller():
	r = create_item({"name": "NoSeller", "price": 10})
	assert r.status_code == 400


def test_TC_004_create_seller_too_small():
	r = create_item({"sellerID": 100000, "name": "BadSellerSmall", "price": 10})
	assert r.status_code == 400


def test_TC_005_create_seller_too_large():
	r = create_item({"sellerID": 1000000, "name": "BadSellerLarge", "price": 10})
	assert r.status_code == 400


def test_TC_006_get_existing(seller_and_items):
	item_id = seller_and_items["ids"][0]
	r = get_item(item_id)
	assert r.status_code == 200
	j = r.json()
	assert j.get("id") == item_id


def test_TC_007_get_nonexistent():
	r = get_item("nonexistent123")
	assert r.status_code == 404


def test_TC_008_get_bad_format_id():
	r = get_item("")
	assert r.status_code == 400


def test_TC_009_get_all_by_seller(seller_and_items):
	seller = seller_and_items["seller"]
	r = get_items_by_seller(seller)
	assert r.status_code == 200
	arr = r.json()
	assert isinstance(arr, list)
	assert len(arr) >= 2
	for item in arr:
		assert item.get("sellerId") == seller


def test_TC_010_get_items_nonexistent_seller():
	r = get_items_by_seller(999999)
	assert r.status_code in (200, 404)
	if r.status_code == 200:
		assert r.json() == []


def test_TC_011_get_items_bad_seller_format():
	r = get_items_by_seller("abc")
	assert r.status_code == 400


def test_TC_012_get_statistic_existing(seller_and_items):
	item_id = seller_and_items["ids"][0]
	r = get_stat(item_id)
	assert r.status_code == 200
	j = r.json()
	assert isinstance(j, dict) or isinstance(j, list)
	if isinstance(j, dict):
		assert "likes" in j and "viewCount" in j and "contacts" in j
	else:
		# if array
		first = j[0] if j else {}
		assert "likes" in first and "viewCount" in first and "contacts" in first


def test_TC_013_get_statistic_nonexistent():
	r = get_stat("nonexistent123")
	assert r.status_code == 404

