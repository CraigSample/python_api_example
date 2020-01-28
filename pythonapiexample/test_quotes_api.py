import json
import logging
from json import JSONDecodeError

import jsonpath
import pytest
import requests
# See https://loremipsum.readthedocs.io/en/latest/
from loremipsum import get_sentence, get_paragraphs

logger = logging.getLogger(__name__)


# Helper methods
def _check_if_int(passed_value):
    """Checks if the passed value is an integer"""
    if not isinstance(passed_value, int):
        raise ResponseError(f'Invalid value: \'{passed_value}\' is not an int.')


def _get_status_code(passed_response):
    """Returns the status code of the passed response"""
    passed_response_status_code = passed_response.status_code
    _check_if_int(passed_response_status_code)
    if passed_response:
        logger.info('Operation success!')
    else:
        # info level used for reporting status code errors
        logger.info(f"An error has occurred: {passed_response}")
    return passed_response_status_code


def _get_key_value_from_response(passed_response, passed_key):
    """Returns the first value of 'passed_key' in the passed response"""
    try:
        json_response = json.loads(passed_response.text)
        value = jsonpath.jsonpath(json_response, passed_key)
        logger.debug(f'{passed_key}: {value[0]}')
        return value[0]
    except JSONDecodeError:
        logger.fatal(f'Invalid response body returned from server. Expecting JSON. Found:\n{passed_response.text}')
    except TypeError:
        logger.fatal(f'Passed key \'{passed_key}\' was not found in response:\n{passed_response.text}')


def _get_first_value_for_key_from_response_data(passed_response, passed_key):
    """Returns the first value for 'passed_key' in the passed response"""
    value = jsonpath.jsonpath(passed_response, passed_key)
    logger.debug(f'value: {value[0]}')
    return value[0]


def _get_all_values_for_key_from_response_data(passed_response, passed_key):
    """Returns a list of all values for 'passed_key' in the passed response"""
    ids = []
    try:
        for elem in passed_response:
            logger.debug(f'elem[{passed_key}]: {elem[passed_key]}')
            ids.append(elem[passed_key])
        return ids
    except KeyError:
        logger.fatal(f'Key \'{passed_key}\' was not found in the response data:\n{passed_response}')


def _get_ids_from_server(session, send_request):
    response = send_request.get(session)
    response_data = _get_key_value_from_response(response, 'data')
    logger.debug(f'initial_get_response_data: {response_data}')
    ids = _get_all_values_for_key_from_response_data(response_data, 'id')
    return ids


def _get_entry_from_response_data(passed_response, passed_key, target_value):
    try:
        for elem in passed_response:
            if elem[passed_key] == target_value:
                logger.debug(f'elem[{passed_key}]: {elem[passed_key]} == {target_value}')
                return elem
        logger.fatal(
            f'Entry for {passed_key} with value {target_value} was not found in the response data:\n{passed_response}')
    except KeyError:
        logger.fatal(f'Key \'{passed_key}\' was not found in the response data:\n{passed_response}')


def assert_status(passed_response, expected_status):
    assert passed_response.status_code == expected_status, "Expected: {} actual: {}. Response error: {}".format(
        expected_status, passed_response.status_code, _get_key_value_from_response(passed_response, 'error'))


class ResponseError(Exception):
    """An exception class for the REST API Response"""


class SendReset:
    """Reset the API and make session and send_request available."""

    def __init__(self):
        session = requests.Session()
        send_request = SendRequest()
        response = send_request.reset(session)
        response_status_code = _get_status_code(response)
        response_ok = _get_key_value_from_response(response, 'ok')
        assert response_status_code == 200
        assert response_ok is True
        self.session = session
        self.send_request = send_request


class SendRequest:
    """Send API requests to 'quotes_server .py' generated url endpoints."""

    base_url = "http://127.0.0.1:6543"
    quotes_endpoint = "quotes"
    reset_endpoint = "reset"
    headers = {
        'Content-Type': 'application/json',
        'Accept': '*/*'
    }
    empty_data = {}

    def reset(self, passed_session):
        # Send POST Request
        logger.info(f"POST url: {SendRequest.base_url}/{SendRequest.reset_endpoint}")
        response = passed_session.post(f'{SendRequest.base_url}/{SendRequest.reset_endpoint}',
                                       headers=SendRequest.headers, data=json.dumps(SendRequest.empty_data))
        return response

    def get(self, passed_session):
        # Send GET Request
        logger.info(f"GET url: {SendRequest.base_url}/{SendRequest.quotes_endpoint}   ")
        response = passed_session.get(f"{SendRequest.base_url}/{SendRequest.quotes_endpoint}")
        return response

    def get_id(self, passed_session, passed_id):
        # Send GET Request
        logger.info(f"GET url: {SendRequest.base_url}/{SendRequest.quotes_endpoint}/{passed_id}")
        _check_if_int(passed_id)
        response = passed_session.get(f"{SendRequest.base_url}/{SendRequest.quotes_endpoint}/{passed_id}")
        return response

    def delete(self, passed_session, passed_id=''):
        # Send DELETE Request
        logger.info(f"DELETE url: {SendRequest.base_url}/{SendRequest.quotes_endpoint}/{passed_id}")
        response = passed_session.delete(f"{SendRequest.base_url}/{SendRequest.quotes_endpoint}/{passed_id}")
        return response

    def post(self, passed_session, passed_json_string=''):
        # Send POST Request
        logger.info(f"POST url: {SendRequest.base_url}/{SendRequest.quotes_endpoint} with data {passed_json_string}")
        try:
            if passed_json_string == '':  # To allow for sending am empty JSON payload to the endpoint.
                request_json = SendRequest.empty_data.copy()
            else:
                request_json = json.loads(passed_json_string)
        except JSONDecodeError:  # This is an ugly solution to allow passing of invalid JSON payload to the endpoint.
            request_json = passed_json_string
        except ValueError:
            raise ResponseError(f'Invalid value: \'{passed_json_string}\' is not a valid json.')
        response = passed_session.post(f"{SendRequest.base_url}/{SendRequest.quotes_endpoint}",
                                       headers=SendRequest.headers, data=json.dumps(request_json))
        return response

    def custom_method_endpoint(self, passed_session, passed_endpoint, passed_method):
        print(f'passed_method: {passed_method}')

        url = SendRequest.base_url + '/' + passed_endpoint
        print(f'url: {url}')
        response = None
        if passed_method == 'GET':
            logger.info(f"GET url: {url}")
            response = passed_session.get(url)
        elif passed_method == 'POST':
            logger.info(f"POST url: {url}")
            response = passed_session.post(url)
        elif passed_method == 'PUT':
            logger.info(f"PUT url: {url}")
            response = passed_session.put(url)
        elif passed_method == 'DELETE':
            logger.info(f"DELETE url: {url}")
            response = passed_session.put(url)
        elif passed_method == 'PATCH':
            logger.info(f"PATCH url: {url}")
            response = passed_session.patch(url)
        elif passed_method == 'HEAD':
            logger.info(f"HEAD url: {url}")
            response = passed_session.head(url)
        elif passed_method == 'OPTIONS':
            logger.info(f"OPTIONS url: {url}")
            response = passed_session.options(url)
        else:
            logger.error(f'Unknown/Unsupported method: \'{passed_method}\'.')
        return response


if __name__ == "__main__":
    print("Pytest Skills Evaluation against " + SendRequest.base_url)
    cur_session = requests.Session()
    request = SendRequest()
    operations = [
        request.reset,
        request.get,
        request.get_id,
        request.delete,
        request.post,
        request.custom_method_endpoint
    ]
    print('Available operations: ')
    for i, operation in enumerate(operations, start=1):
        print(f"{i}: {operation.__name__}")
    try:
        print('\nGET: ')
        print(json.dumps(_get_key_value_from_response(operations[1](cur_session), 'data'), indent=4, sort_keys=True))
    except ResponseError as ex:
        print(ex)


class TestCases:
    # This wasn't working for me; I'd be really interested to find out where I went wrong.
    # @classmethod
    # def setup_class(cls):
    #     """Start the quotes_server.py server"""
    #     logger.debug("setup_class       class:%s" % cls.__name__)
    #     global global_server_process
    #     global_server_process = subprocess.Popen("/usr/bin/env python quotes_server.py > /dev/null 2> /dev/null &",
    #                                               shell=False, preexec_fn=os.setsid)
    #
    #
    # @classmethod
    # def teardown_class(cls):
    #     """Stop the quotes_server.py server"""
    #     logger.debug("teardown_class    class:%s" % cls.__name__)
    #     global global_server_process
    #     global_server_process.terminate()

    @pytest.fixture
    def setup(self):
        """Reset the API state before each test case to maintain test case independence"""
        logger.debug("setup           class:%s" % self)
        return SendReset()

    # def setup_method(self):
    #     """Reset the API state before each test case to maintain test case independence"""
    #     logger.debug("setup_method    class:%s" % self)
    #     # global sendRequest
    #     sendRequest = SendRequest()
    #     response = sendRequest.reset()
    #     response_status_code = _get_status_code(response)
    #     response_ok = _get_key_value_from_response(response, 'ok')
    #     assert response_status_code == 200
    #     assert response_ok is True
    #     # This return is not needed for this solution as the var is global, but is included because it was a
    #     # requirement.
    #     return session

    def test_reset(self, setup):
        """Not required, but created for TDD."""
        response = setup.send_request.reset(setup.session)
        response_status_code = _get_status_code(response)
        response_ok = _get_key_value_from_response(response, 'ok')
        get_response = setup.send_request.get(setup.session)
        get_response_status_code = _get_status_code(get_response)
        get_response_ok = _get_key_value_from_response(get_response, 'ok')
        get_response_data = _get_key_value_from_response(get_response, 'data')

        assert response_status_code == 200
        assert response_ok is True
        assert get_response_status_code == 200
        assert get_response_ok is True
        assert len(get_response_data) == 3

    def test_get_all(self, setup):
        """Test default GET /quotes."""
        response = setup.send_request.get(setup.session)
        response_status_code = _get_status_code(response)
        response_ok = _get_key_value_from_response(response, 'ok')
        response_data = _get_key_value_from_response(response, 'data')

        assert response_status_code == 200
        assert response_ok is True
        assert len(response_data) == 3

    def test_get_requirements(self, setup):
        """
        Test default GET /quotes output.
        Requirement: Output data is sorted by id. Test that this is true for at least 12 quotes.
        Requirement: There are no duplicate IDs.
        """
        num_total_entries = 15

        # Get the initial id entries from the server
        initial_ids = _get_ids_from_server(setup.session, setup.send_request)

        # Loop to create the number of new entries
        for x in range(num_total_entries - len(initial_ids)):
            logger.debug(f'x: {x}')
            quote_text = get_sentence(True)
            post_response = setup.send_request.post(setup.session, '{"text": "' + quote_text + '"}')
            assert_status(post_response, 201)
            post_response_status_code = _get_status_code(post_response)
            post_response_ok = _get_key_value_from_response(post_response, 'ok')
            assert post_response_status_code == 201
            assert post_response_ok is True

        # Get the GET payload from the server.
        response = setup.send_request.get(setup.session)
        response_status_code = _get_status_code(response)
        response_ok = _get_key_value_from_response(response, 'ok')
        response_data = _get_key_value_from_response(response, 'data')

        # Get the id keys from the payload.
        keys_from_server = _get_all_values_for_key_from_response_data(response_data, 'id')

        # Sort the keys numerically in a second array.
        sorted_keys_from_server = keys_from_server.copy()
        sorted_keys_from_server.sort()

        assert response_status_code == 200
        assert response_ok is True
        assert len(response_data) == num_total_entries
        assert len(keys_from_server) == len(set(keys_from_server))
        assert sorted_keys_from_server == keys_from_server

    def test_post_requirement1(self, setup):
        """
        Test POST /quotes of a new valid entry.
        Requirement: Accepts a string as the "text" field, e.g. {"text": "I have a dream"}.
                    The response data contains a new ID and the text as provided in the request.
        """
        quote_text = "I have a dream"

        # Get the initial id entries from the server
        initial_ids = _get_ids_from_server(setup.session, setup.send_request)

        response = setup.send_request.post(setup.session, '{"text": "' + quote_text + '"}')
        response_status_code = _get_status_code(response)
        response_ok = _get_key_value_from_response(response, 'ok')
        response_data = _get_key_value_from_response(response, 'data')
        new_id = _get_first_value_for_key_from_response_data(response_data, 'id')
        response_text = _get_first_value_for_key_from_response_data(response_data, 'text')

        # Get the final id entries from the server
        final_ids = _get_ids_from_server(setup.session, setup.send_request)

        assert response_status_code == 201
        assert response_ok is True
        assert response_text == quote_text
        assert new_id not in initial_ids
        assert new_id in final_ids

    def test_post_requirement2a(self, setup):
        """
        Test POST /quotes of a new entry without passing a payload.
        Requirement: Rejects (with HTTP code 400) objects missing the text field, and
                    when the text field is not a string, e.g. {}  and  {"text": 123}
        """
        response = setup.send_request.post(setup.session)
        response_status_code = _get_status_code(response)
        response_ok = _get_key_value_from_response(response, 'ok')

        assert response_status_code == 400
        assert response_ok is False

    def test_post_requirement2b(self, setup):
        """
        Test POST /quotes of a new entry passing the text field with no value.
        Requirement: Rejects (with HTTP code 400) objects missing the text field, and
                    when the text field is not a string, e.g. {}  and  {"text": 123}
        """
        response = setup.send_request.post(setup.session, '{"text": }')
        response_status_code = _get_status_code(response)
        response_ok = _get_key_value_from_response(response, 'ok')

        assert response_status_code == 400
        assert response_ok is False

    def test_post_requirement2c(self, setup):
        """
        Test POST /quotes of a new entry passing {} value for text.
        Requirement: Rejects (with HTTP code 400) objects missing the text field, and
                    when the text field is not a string, e.g. {}  and  {"text": 123}
        """
        response = setup.send_request.post(setup.session, '{"text": {}}')
        response_status_code = _get_status_code(response)
        response_ok = _get_key_value_from_response(response, 'ok')

        assert response_status_code == 400
        assert response_ok is False

    def test_post_requirement2d(self, setup):
        """
        Test POST /quotes of a new entry passing an int value for text.
        Requirement: Rejects (with HTTP code 400) objects missing the text field, and
                    when the text field is not a string, e.g. {}  and  {"text": 123}
        """
        response = setup.send_request.post(setup.session, '{"text": 123}')
        response_status_code = _get_status_code(response)
        response_ok = _get_key_value_from_response(response, 'ok')

        assert response_status_code == 400
        assert response_ok is False

    def test_post_requirement2e(self, setup):
        """
        Test POST /quotes of a new entry by passing a bad field name.
        Requirement: Rejects (with HTTP code 400) objects missing the text field, and
                    when the text field is not a string, e.g. {}  and  {"text": 123}
        """
        quote_text = "I have a dream"
        response = setup.send_request.post(setup.session, '{"testy": "' + quote_text + '"}')
        response_status_code = _get_status_code(response)
        response_ok = _get_key_value_from_response(response, 'ok')

        assert response_status_code == 400
        assert response_ok is False

    def test_post_requirement3(self, setup):
        """
        Test POST /quotes of 25 new entries.
        Requirement: Storing at least 20 quotes is supported.
        """
        num_new_entries = 25

        # Get the initial id entries from the server
        initial_ids = _get_ids_from_server(setup.session, setup.send_request)
        num_initial_ids = len(initial_ids)
        logger.debug(f'num_initial_ids: {num_initial_ids}')

        # Loop to create the number of new entries
        for x in range(num_new_entries):
            logger.debug(f'x: {x}')
            quote_text = get_sentence(True)
            post_response = setup.send_request.post(setup.session, '{"text": "' + quote_text + '"}')
            assert_status(post_response, 201)
            post_response_status_code = _get_status_code(post_response)
            post_response_ok = _get_key_value_from_response(post_response, 'ok')
            post_response_data = _get_key_value_from_response(post_response, 'data')
            new_id = _get_first_value_for_key_from_response_data(post_response_data, 'id')
            logger.debug(f'new_id: {new_id}')
            response_text = _get_first_value_for_key_from_response_data(post_response_data, 'text')
            logger.debug(f'response_text: {response_text}')

            try:
                cur_get_response = setup.send_request.get(setup.session)
                assert_status(cur_get_response, 200)
                cur_get_response_data = _get_key_value_from_response(cur_get_response, 'data')
                cur_ids = _get_all_values_for_key_from_response_data(cur_get_response_data, 'id')

                assert post_response_status_code == 201
                assert post_response_ok is True
                assert response_text == quote_text
                assert new_id not in initial_ids
                assert new_id in cur_ids
            except (AssertionError, TypeError):
                num_current_entries = num_initial_ids + x
                logger.error(f'Invalid response from server when number of quotes exceeds {num_current_entries}')

        # Get the final id entries from the server
        final_ids = _get_ids_from_server(setup.session, setup.send_request)
        num_final_ids = sum(1 for _ in final_ids)
        logger.debug(f'num_final_ids: {num_final_ids}')

        assert num_final_ids == num_initial_ids + num_new_entries

    def test_post_requirement4(self, setup):
        """
        Test POST /quotes of a new valid entry.
        Requirement: After adding a new quote, it should appear in a subsequent GET /quotes request.
        """
        quote_text = "a new quote"

        # Get the initial id entries from the server
        initial_ids = _get_ids_from_server(setup.session, setup.send_request)

        # Add the new quote
        post_response = setup.send_request.post(setup.session, '{"text": "' + quote_text + '"}')
        post_response_status_code = _get_status_code(post_response)
        post_response_ok = _get_key_value_from_response(post_response, 'ok')
        post_response_data = _get_key_value_from_response(post_response, 'data')
        new_id = _get_first_value_for_key_from_response_data(post_response_data, 'id')
        post_response_text = _get_first_value_for_key_from_response_data(post_response_data, 'text')

        # Issue a new GET
        get_response = setup.send_request.get(setup.session)
        get_response_status_code = _get_status_code(get_response)
        get_response_ok = _get_key_value_from_response(get_response, 'ok')
        get_response_data = _get_key_value_from_response(get_response, 'data')
        found_entry = _get_entry_from_response_data(get_response_data, 'id', new_id)
        found_entry_text = _get_first_value_for_key_from_response_data(found_entry, 'text')

        # Get the final id entries from the server
        final_ids = _get_all_values_for_key_from_response_data(get_response_data, 'id')

        assert post_response_status_code == 201
        assert post_response_ok is True
        assert get_response_status_code == 200
        assert get_response_ok is True
        assert post_response_text == quote_text
        assert found_entry_text == quote_text
        assert new_id not in initial_ids
        assert new_id in final_ids

    def test_post_large_quote(self, setup):
        """
        Test POST /quotes of a new entry with a large quote.
        """
        str1 = " "
        quote_text = str1.join(get_paragraphs(1000, True))
        logger.debug(f'Size of large quote: {len(quote_text)} characters.')

        response = setup.send_request.post(setup.session, '{"text": "' + quote_text + '"}')
        response_status_code = _get_status_code(response)
        response_ok = _get_key_value_from_response(response, 'ok')
        response_data = _get_key_value_from_response(response, 'data')
        response_text = _get_first_value_for_key_from_response_data(response_data, 'text')

        assert response_status_code == 201
        assert response_ok is True
        assert response_text == quote_text

    def test_get_id_1(self, setup):
        """Test GET /quotes with a valid existing id."""
        target_id = 1
        response = setup.send_request.get_id(setup.session, target_id)
        response_status_code = _get_status_code(response)
        response_ok = _get_key_value_from_response(response, 'ok')
        response_data = _get_key_value_from_response(response, 'data')
        response_id = _get_first_value_for_key_from_response_data(response_data, 'id')
        response_text = _get_first_value_for_key_from_response_data(response_data, 'text')

        assert response_status_code == 200
        assert response_ok is True
        assert response_id == target_id
        assert response_text == 'We have nothing to fear but fear itself!'

    def test_get_id_requirement1(self, setup):
        """
        Test GET /quotes/<id> with valid existing ids against GET results.
        Requirement: All quotes objects from GET /quotes are retrievable individually based
                    on their ID, and that the text matches.
        """

        # Issue a new GET
        get_all_response = setup.send_request.get(setup.session)
        get_all_response_status_code = _get_status_code(get_all_response)
        get_all_response_ok = _get_key_value_from_response(get_all_response, 'ok')
        get_all_response_data = _get_key_value_from_response(get_all_response, 'data')

        assert get_all_response_status_code == 200
        assert get_all_response_ok is True

        # Get the initial id entries from the server
        initial_ids = _get_all_values_for_key_from_response_data(get_all_response_data, 'id')

        for cur_id in initial_ids:
            cur_get_all_entry = _get_entry_from_response_data(get_all_response_data, 'id', cur_id)
            cur_get_all_entry_text = _get_first_value_for_key_from_response_data(cur_get_all_entry, 'text')

            # Perform a GET /quotes/<id> for the current id
            cur_get_id_response = setup.send_request.get_id(setup.session, cur_id)
            cur_get_id_response_status_code = _get_status_code(cur_get_id_response)
            cur_get_id_response_ok = _get_key_value_from_response(cur_get_id_response, 'ok')
            cur_get_id_response_data = _get_key_value_from_response(cur_get_id_response, 'data')
            cur_get_id_response_id = _get_first_value_for_key_from_response_data(cur_get_id_response_data, 'id')
            cur_get_id_response_text = _get_first_value_for_key_from_response_data(cur_get_id_response_data, 'text')

            assert cur_get_id_response_status_code == 200
            assert cur_get_id_response_ok is True
            assert cur_get_id_response_id == cur_id
            assert cur_get_id_response_text == cur_get_all_entry_text

    def test_get_id_requirement2a(self, setup):
        """
        Test GET /quotes/<id> with an invalid id: -1.
        Requirement: Nonexistant quote IDs provoke an HTTP code 404.
        """
        target_id = -1
        response = setup.send_request.get_id(setup.session, target_id)
        response_status_code = _get_status_code(response)
        response_ok = _get_key_value_from_response(response, 'ok')

        assert response_status_code == 404
        assert response_ok is False

    def test_get_id_requirement2b(self, setup):
        """
        Test GET /quotes/<id> with an id that doesn't exist: 0.
        Requirement: Nonexistant quote IDs provoke an HTTP code 404.
        """
        target_id = 0
        response = setup.send_request.get_id(setup.session, target_id)
        response_status_code = _get_status_code(response)
        response_ok = _get_key_value_from_response(response, 'ok')

        assert response_status_code == 404
        assert response_ok is False

    def test_delete_requirement1(self, setup):
        """
        Test DELETE /quotes/<id> with a known id.
        Requirement: Deleting a quote succeeds, and subsequent attempts to delete that quote reply with HTTP code 404.
        """
        target_id = '3'

        # Delete the target_id entry
        first_response = setup.send_request.delete(setup.session, target_id)
        first_response_status_code = _get_status_code(first_response)
        first_response_ok = _get_key_value_from_response(first_response, 'ok')

        # Delete the target_id entry
        second_response = setup.send_request.delete(setup.session, target_id)
        second_response_status_code = _get_status_code(second_response)
        second_response_ok = _get_key_value_from_response(second_response, 'ok')

        # Delete the target_id entry
        third_response = setup.send_request.delete(setup.session, target_id)
        third_response_status_code = _get_status_code(third_response)
        third_response_ok = _get_key_value_from_response(third_response, 'ok')

        assert first_response_status_code == 200
        assert first_response_ok is True
        assert second_response_status_code == 404
        assert second_response_ok is False
        assert third_response_status_code == 404
        assert third_response_ok is False

    def test_delete_requirement2(self, setup):
        """
        Test DELETE /quotes/<id> with a known id.
        Requirement: Once a quote is deleted, it no longer shows up in the data for GET /quotes.
        """
        target_id = '2'

        # Get the initial id entries from the server
        initial_ids = _get_ids_from_server(setup.session, setup.send_request)
        num_initial_ids = len(initial_ids)

        # Delete the target_id entry
        response = setup.send_request.delete(setup.session, target_id)
        response_status_code = _get_status_code(response)
        response_ok = _get_key_value_from_response(response, 'ok')
        response_data = _get_key_value_from_response(response, 'data')

        # Get the final id entries from the server
        final_ids = _get_ids_from_server(setup.session, setup.send_request)
        num_final_ids = len(final_ids)

        assert response_status_code == 200
        assert response_ok is True
        assert int(target_id) in initial_ids
        assert int(target_id) not in final_ids
        assert num_final_ids == num_initial_ids - 1
        assert response_data is None

    def test_delete_unknown_id(self, setup):
        """Test DELETE /quotes/<id> with a non existing id."""
        target_id = '28'
        response = setup.send_request.delete(setup.session, target_id)
        response_status_code = _get_status_code(response)
        response_ok = _get_key_value_from_response(response, 'ok')

        assert response_status_code == 404
        assert response_ok is False

    def test_delete_text_value(self, setup):
        """Test DELETE /quotes/<id> with a text value for id."""
        target_id = "one"
        response = setup.send_request.delete(setup.session, target_id)
        response_status_code = _get_status_code(response)
        response_ok = _get_key_value_from_response(response, 'ok')

        assert response_status_code == 404
        assert response_ok is False

    def test_delete_no_id(self, setup):
        """Test DELETE /quotes/<id> with no value for id."""
        response = setup.send_request.delete(setup.session)
        response_status_code = _get_status_code(response)
        response_ok = _get_key_value_from_response(response, 'ok')

        assert response_status_code == 404
        assert response_ok is False

    def test_put_quotes(self, setup):
        """Test PUT /quotes (MethodNotAllowed)."""
        response = setup.send_request.custom_method_endpoint(setup.session, SendRequest.quotes_endpoint, 'PUT')
        # assert_status(response, 405)
        response_status_code = _get_status_code(response)
        response_ok = _get_key_value_from_response(response, 'ok')
        # response_error = _get_key_value_from_response(response, 'error')

        assert response_status_code == 405
        assert response_ok is False

    def test_delete_quotes(self, setup):
        """Test DELETE /quotes (MethodNotAllowed)."""
        response = setup.send_request.custom_method_endpoint(setup.session, SendRequest.quotes_endpoint, 'DELETE')
        # assert_status(response, 405)
        response_status_code = _get_status_code(response)
        response_ok = _get_key_value_from_response(response, 'ok')
        # response_error = _get_key_value_from_response(response, 'error')

        assert response_status_code == 405
        assert response_ok is False
