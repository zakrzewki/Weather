import asyncio
from unittest.mock import patch, MagicMock, AsyncMock, call
from src.main import WeatherFetcher, WeatherProcessor, runner, get_location


def test_weather_fetcher():
    with patch('aiohttp.ClientSession.get') as mocked_get:
        mocked_get.return_value.__aenter__.return_value.status = 200
        mocked_get.return_value.__aenter__.return_value.text = AsyncMock(return_value='{"hourly": '
                                                                                      '{"temperature_2m": [20, 15], "rain": [0, 10], "time": ["2023-10-20T12:00:00Z", "2023-10-20T13:00:00Z"]}}')

        fetcher = WeatherFetcher(51.10, 17.03)
        data = asyncio.run(fetcher.get_data())

        assert data == {"hourly": {"temperature_2m": [20, 15], "rain": [0, 10], "time": ["2023-10-20T12:00:00Z", "2023-10-20T13:00:00Z"]}}


def test_weather_processor_temperature():
    data = {"hourly": {"temperature_2m": [20, 15], "rain": [0, 4],
                       "time": ["2023-10-20T12:00:00Z", "2023-10-20T13:00:00Z"]}}
    processor = WeatherProcessor(data, 18, 5, "Wrocław")

    with patch('builtins.print') as mocked_print:
        processor.process()
        mocked_print.assert_called_once_with(
            "Warning Wrocław, low temperature 15 of C and rain 4 mm expected on 2023-10-20T13:00:00Z")


def test_weather_processor_rain():
    data = {"hourly": {"temperature_2m": [17, 15], "rain": [0, 10],
                       "time": ["2023-10-20T12:00:00Z", "2023-10-20T13:00:00Z"]}}
    processor = WeatherProcessor(data, 10, 5, "Wrocław")

    with patch('builtins.print') as mocked_print:
        processor.process()
        mocked_print.assert_called_once_with(
            "Warning Wrocław, low temperature 15 of C and rain 10 mm expected on 2023-10-20T13:00:00Z")


def test_weather_processor_rain_and_temperature():
    data = {"hourly": {"temperature_2m": [7, 15], "rain": [0, 10],
                       "time": ["2023-10-20T12:00:00Z", "2023-10-20T13:00:00Z"]}}
    processor = WeatherProcessor(data, 10, 5, "Wrocław")

    with patch('builtins.print') as mocked_print:
        processor.process()
        calls = [call('Warning Wrocław, low temperature 15 of C and rain 10 mm expected on 2023-10-20T13:00:00Z'), call('Warning Wrocław, low temperature 7 of C and rain 0 mm expected on 2023-10-20T12:00:00Z')]
        mocked_print.assert_has_calls(calls)


def test_runner():
    with patch('src.main.WeatherFetcher.get_data') as mocked_get_data:
        mocked_get_data.return_value = {"hourly": {"temperature_2m": [20, 15], "rain": [0, 10],
                                                   "time": ["2023-10-20T12:00:00Z", "2023-10-20T13:00:00Z"]}}

        with patch('src.main.WeatherProcessor.process') as mocked_process:
            asyncio.run(runner("Warsaw", 18, 5))
            mocked_process.assert_called_once()


def test_get_location_using_geopy():
    with patch('geopy.geocoders.Nominatim.geocode') as mocked_geocode:
        mocked_geocode.return_value = MagicMock(latitude=52.2297, longitude=21.0122)

        lat, long = get_location("Warsaw")
        assert lat == 52.2297
        assert long == 21.0122


def test_runner_with_digits_in_name_no_coma():
    name = "52.2297 21.0122"
    lat, long = get_location(name)
    assert lat == "52.2297"
    assert long == "21.0122"


def test_runner_with_digits_in_name_with_coma():
    name = "52.229, 21.012"
    lat, long = get_location(name)
    assert lat == "52.229"
    assert long == "21.012"


def test_runner_with_incorrect_city():
    # TODO: TBD when implementation is done
    pass
    # with patch('geopy.geocoders.Nominatim.geocode') as mocked_geocode:
    #     mocked_geocode.return_value = MagicMock(None)
    #
    #     get_location("HHHHHHHH")
    #     assert lat == 52.2297
    #     assert long == 21.0122


def test_runner_with_incorrect_input():
    # TODO: TBD when implementation is done
    pass
