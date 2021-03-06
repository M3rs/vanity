import unittest
import mock
import datetime

import vanity


# mocks
def empty_release_info(package, json):
    return iter(())


def single_release_info(package, json):
    url = {'filename': 'fake package',
           'downloads': 1,
           'upload_time': datetime.date(2016, 10, 13)}
    data = {'version': '1.0'}

    yield [url], data


def two_url_release_info(package, json):
    first_url = {'filename': 'fake package',
                 'downloads': 1,
                 'upload_time': datetime.date(2016, 10, 13)}

    second_url = {'filename': 'fake package two',
                  'downloads': 2,
                  'upload_time': datetime.date(2016, 10, 13)}

    data = {'version': '1.0'}

    yield [first_url, second_url], data


# http://stackoverflow.com/q/21611559
def Any(object_type):
    class Any(object_type):
        def __eq__(self, other):
            return True
    return Any()


class TestCountDownloads(unittest.TestCase):
    """
    A test class for the count_downloads method.
    """

    @mock.patch('vanity.get_release_info', side_effect=empty_release_info)
    def test_count_empty(self, get_release_func):
        count = vanity.count_downloads(None)

        self.assertEqual(count, 0)

    @mock.patch('vanity.get_release_info', side_effect=single_release_info)
    def test_count_single(self, get_release_func):
        count = vanity.count_downloads('fake package')

        self.assertEqual(count, 1)

    @mock.patch('vanity.get_release_info', side_effect=two_url_release_info)
    def test_count_multiple(self, get_release_func):
        count = vanity.count_downloads('fake package')

        self.assertEqual(count, 3)

    @mock.patch('vanity.get_release_info', side_effect=single_release_info)
    def test_count_version(self, get_release_func):
        count = vanity.count_downloads('fake package',
                                       version='1.1')

        self.assertEqual(count, 0)

    @mock.patch('vanity.get_release_info', side_effect=single_release_info)
    def test_bad_pattern(self, get_release_func):
        count = vanity.count_downloads('fake package',
                                       pattern='real')

        self.assertEqual(count, 0)

    @mock.patch('vanity.get_release_info', side_effect=single_release_info)
    def test_good_pattern(self, get_release_func):
        count = vanity.count_downloads('fake package',
                                       pattern='[Ff]ake')

        self.assertEqual(count, 1)

    @mock.patch('vanity.get_release_info', side_effect=single_release_info)
    def test_verbose_calls_debug(self, get_release_func):
        mock_logger = mock.Mock()
        vanity.logger = mock_logger

        count = vanity.count_downloads('fake package')

        self.assertEqual(count, 1)
        mock_logger.debug.assert_any_call(Any(str))

    @mock.patch('vanity.get_release_info', side_effect=single_release_info)
    def test_not_verbose_no_debug(self, get_release_func):
        mock_logger = mock.Mock()
        vanity.logger = mock_logger

        count = vanity.count_downloads('fake package',
                                       verbose=False)

        self.assertEqual(count, 1)
        mock_logger.debug.assert_not_called()


class TestByTwo(unittest.TestCase):
    """
    A test class for the by_two method.
    """

    def test_none(self):
        input = iter(())

        result = {url: data for (url, data) in vanity.by_two(input)}

        self.assertEqual(result, {})

    def test_pairs_url_and_data(self):
        input = iter(['test.com', 'test data',
                      'foo.org', 'foo data',
                      'bar.net', 'bar data'])

        result = {url: data for (url, data) in vanity.by_two(input)}

        self.assertEqual(result['test.com'], 'test data')
        self.assertEqual(result['foo.org'], 'foo data')
        self.assertEqual(result['bar.net'], 'bar data')

    def test_odd_input(self):
        input = iter(['test.com', 'test data',
                      'foo.org', 'foo data',
                      'bar.net'])

        result = {url: data for (url, data) in vanity.by_two(input)}

        self.assertEqual(result['test.com'], 'test data')
        self.assertEqual(result['foo.org'], 'foo data')
        self.assertIsNone(result.get('bar.net'))


class TestNormalize(unittest.TestCase):
    """
    A test class for the normalize method.
    """

    def test_fake_package(self):
        self.assertRaises(ValueError,
                          vanity.normalize,
                          "FAKEPACKAGE1@!")
        self.assertRaises(ValueError,
                          vanity.normalize,
                          "1337INoscopeyou")

    def test_django(self):
        normalized = vanity.normalize("dJaNgO")
        self.assertEqual(normalized, "Django")

    def test_none(self):
        normalized = vanity.normalize(None)
        self.assertEqual(normalized, "none")

    def test_flask(self):
        normalized = vanity.normalize("fLaSk")
        self.assertEqual(normalized, "Flask")

    def test_space_string(self):
        normalized = vanity.normalize("               Flask                ")
        self.assertEqual(normalized, "               Flask                ")

    def test_empty(self):
        normalized = vanity.normalize("")
        self.assertEqual(normalized, "")

if __name__ == '__main__':
    unittest.main()
