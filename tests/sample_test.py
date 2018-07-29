import os


def test_os_path_join():
    path = os.path.join('hello', 'there.jpg')
    assert path == 'hello/there.jpg'

