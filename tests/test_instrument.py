import pytest

from OSmOSE.public_api.instrument import Instrument


@pytest.mark.parametrize(
    ("instrument", "expected_end_to_end"),
    [
        pytest.param(
            Instrument(),
            1.0,
            id="default_to_1",
        ),
        pytest.param(
            Instrument(sensitivity=2),
            0.5,
            id="2V_per_Pa_with_1V_Vmax",
        ),
        pytest.param(
            Instrument(gain_db=6),
            0.5,
            id="6dB_gain_doubles_voltage",
        ),
        pytest.param(
            Instrument(peak_voltage=2),
            2,
            id="2V_Vmax",
        ),
        pytest.param(
            Instrument(
                sensitivity=0.1,
                gain_db=20,
                peak_voltage=0.01,
            ),
            0.01,
            id="full_chain",
        ),
    ],
)
def test_end_to_end_from_chain(
    instrument: Instrument, expected_end_to_end: float
) -> None:
    assert round(instrument.end_to_end, ndigits=2) == expected_end_to_end
