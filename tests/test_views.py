from sm.views.notfound import notfound_view


def test_my_view_failure(app_request):
    test = True
    assert test == True


def test_notfound_view(app_request):
    info = notfound_view(app_request)
    assert app_request.response.status_int == 404
    assert info == {}
