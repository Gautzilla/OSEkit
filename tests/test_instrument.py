import numpy as np
import pytest
from scipy.signal import ShortTimeFFT
from scipy.signal.windows import hamming

from OSmOSE.config import TIMESTAMP_FORMAT_TEST_FILES
from OSmOSE.core_api.audio_data import AudioData
from OSmOSE.core_api.audio_file import AudioFile
from OSmOSE.core_api.instrument import Instrument
from OSmOSE.core_api.spectro_data import SpectroData


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
            Instrument(gain_db=6.020599913279624),
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
        pytest.param(
            Instrument(
                end_to_end_db=0.0,
            ),
            Instrument.P_REF,
            id="end_to_end_of_0dB_results_in_pref",
        ),
        pytest.param(
            Instrument(
                end_to_end_db=120.0,
            ),
            1e6 * Instrument.P_REF,
            id="end_to_end_of_120dBSPL_makes_1_Pa",
        ),
        pytest.param(
            Instrument(
                sensitivity=0.1,
                gain_db=20,
                peak_voltage=0.01,
                end_to_end_db=0.0,
            ),
            Instrument.P_REF,
            id="end_to_end_overwrites_the_rest",
        ),
    ],
)
def test_end_to_end(
    instrument: Instrument,
    expected_end_to_end: float,
) -> None:
    assert instrument.end_to_end == expected_end_to_end


@pytest.mark.parametrize(
    ("instrument", "n", "expected_p"),
    [
        pytest.param(
            Instrument(
                sensitivity=0.1,
                gain_db=20,
                peak_voltage=0.01,
            ),
            1.0,
            0.01,
            id="full_scale",
        ),
        pytest.param(
            Instrument(
                sensitivity=0.1,
                gain_db=20,
                peak_voltage=0.01,
            ),
            -1.0,
            -0.01,
            id="negative_full_scale",
        ),
        pytest.param(
            Instrument(
                sensitivity=0.1,
                gain_db=20,
                peak_voltage=0.01,
            ),
            0.0,
            0.0,
            id="zero",
        ),
        pytest.param(
            Instrument(
                sensitivity=0.1,
                gain_db=20,
                peak_voltage=0.01,
            ),
            0.3,
            0.003,
            id="within_scale",
        ),
        pytest.param(
            Instrument(
                end_to_end_db=-40,
            ),
            -0.3,
            -0.003 * Instrument.P_REF,
            id="specified_end_to_end",
        ),
    ],
)
def test_n_to_p(
    instrument: Instrument,
    n: float,
    expected_p: float,
) -> None:
    assert instrument.n_to_p(n) == expected_p


@pytest.mark.parametrize(
    ("natural", "decibel"),
    [
        pytest.param(
            1.0,
            0.0,
            id="no_gain",
        ),
        pytest.param(
            10.0,
            20.0,
            id="positive_gain",
        ),
        pytest.param(
            0.1,
            -20.0,
            id="negative_gain",
        ),
    ],
)
def test_db_conversion(natural: float, decibel: float) -> None:
    i = Instrument()

    i.gain = natural
    assert i.gain_db == decibel

    i.gain_db = decibel
    assert i.gain_db == decibel

    i.end_to_end = natural
    assert i.end_to_end_db == decibel - 20 * np.log10(Instrument.P_REF)

    i.end_to_end_db = decibel
    assert i.end_to_end == Instrument.P_REF * natural


@pytest.mark.parametrize(
    ("audio_files", "instrument", "sft"),
    [
        pytest.param(
            {
                "duration": 1,
                "sample_rate": 48_000,
                "nb_files": 1,
                "series_type": "sine",
                "sine_frequency": 1_000,
                "magnitude": 1.0,
            },
            None,
            ShortTimeFFT(hamming(128), 10, 48_000, scale_to="magnitude"),
            id="0_db_fs",
        ),
        pytest.param(
            {
                "duration": 1,
                "sample_rate": 48_000,
                "nb_files": 1,
                "series_type": "sine",
                "sine_frequency": 1_000,
                "magnitude": 0.1,
            },
            None,
            ShortTimeFFT(hamming(128), 10, 48_000, scale_to="magnitude"),
            id="negative_db_fs",
        ),
    ],
    indirect=["audio_files"],
)
def test_instrument_level_spectrum(
    audio_files: pytest.fixture, instrument: Instrument | None, sft: ShortTimeFFT
) -> None:

    af, request = audio_files
    ad = AudioData.from_files(
        [AudioFile(af[0], strptime_format=TIMESTAMP_FORMAT_TEST_FILES)]
    )
    sd = SpectroData.from_audio_data(ad, sft)

    sine_frequency = request.param["sine_frequency"]
    sine_magnitude = request.param["magnitude"]

    # Get the bin index which center frequency is the closest to the signal frequency:
    bin_idx = min(enumerate(sft.f), key=lambda t: abs(t[1] - sine_frequency))[0]

    expected_level = 20 * np.log10(sine_magnitude)
    # Level in db FS if no instrument, dB SPL otherwise
    expected_level += 0 if instrument is None else 20 * np.log10(1 / instrument.P_REF)

    # We'll not land on exactly the expected level because energy
    # scatters around sine_frequency
    level_tolerance = 10

    equalized_sx = sd.to_db(sd.get_value())
    computed_level = equalized_sx[bin_idx, :].mean()

    assert abs(computed_level - expected_level) < level_tolerance
