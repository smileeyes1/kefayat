from resilience_router import Cache, QuotaState, Request, ResilientRouter, Route


def test_cache_wins(tmp_path):
    cache = Cache(str(tmp_path / "cache.json"))
    router = ResilientRouter(cache)
    request = Request("lesson", {"grade": 1}, "kb1")
    cache.put(request.key, {"answer": "cached"})
    route, result = router.resolve(request, lambda _: {"answer": "rules"})
    assert route == Route.CACHE
    assert result["answer"] == "cached"


def test_local_rules_avoid_cloud(tmp_path):
    router = ResilientRouter(Cache(str(tmp_path / "cache.json")))
    calls = {"cloud": 0}
    request = Request("validation", {"x": 1}, "kb1")

    def cloud(_):
        calls["cloud"] += 1
        return {"bad": True}

    route, result = router.resolve(request, lambda _: {"valid": True}, authorized_cloud=cloud)
    assert route == Route.LOCAL_RULES
    assert result["valid"] is True
    assert calls["cloud"] == 0


def test_quota_exhaustion_blocks_cloud(tmp_path):
    router = ResilientRouter(Cache(str(tmp_path / "cache.json")))
    request = Request("generation", {"x": 1}, "kb1")
    calls = {"cloud": 0}

    def cloud(_):
        calls["cloud"] += 1
        return {"answer": "cloud"}

    route, result = router.resolve(
        request,
        lambda _: None,
        authorized_cloud=cloud,
        quota=QuotaState(cloud_allowed=False, reason="exhausted"),
    )
    assert route == Route.BLOCKED
    assert result is None
    assert calls["cloud"] == 0


def test_local_model_is_second_fallback(tmp_path):
    router = ResilientRouter(Cache(str(tmp_path / "cache.json")))
    request = Request("generation", {"x": 1}, "kb1")
    route, result = router.resolve(
        request,
        lambda _: None,
        local_model=lambda _: {"answer": "local"},
        authorized_cloud=lambda _: {"answer": "cloud"},
    )
    assert route == Route.LOCAL_MODEL
    assert result["answer"] == "local"
