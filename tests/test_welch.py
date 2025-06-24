import numpy as np
import pytest
from scipy.signal import ShortTimeFFT
from scipy.signal.windows import hamming

from OSmOSE.core_api.audio_data import AudioData
from OSmOSE.core_api.instrument import Instrument
from OSmOSE.core_api.spectro_data import SpectroData


@pytest.mark.parametrize(
    ("audio_files", "sft", "instrument"),
    [
        pytest.param(
            {
                "duration": 2,
                "sample_rate": 50_000,
                "series_type": "noise",
            },
            ShortTimeFFT(
                win=hamming(2048),
                fs=48_000,
                hop=1024,
            ),
            None,
            id="no_instrument",
        ),
        pytest.param(
            {
                "duration": 2,
                "sample_rate": 50_000,
                "series_type": "noise",
            },
            ShortTimeFFT(
                win=hamming(2048),
                fs=48_000,
                hop=1024,
            ),
            Instrument(
                sensitivity=10**6 * 10 ** (-170 / 20),
                gain_db=0,
                peak_voltage=1,
            ),
            id="with_instrument",
        ),
    ],
    indirect=["audio_files"],
)
def test_welch_level(
    audio_files: pytest.fixture, sft: ShortTimeFFT, instrument: Instrument | None
) -> None:
    afs, _ = audio_files
    ad = AudioData.from_files(files=afs, instrument=instrument)
    sd = SpectroData.from_audio_data(data=ad, fft=sft)

    ref = 1 if instrument is None else instrument.P_REF

    welch = sd.get_welch()
    welch_db = 10 * np.log10(welch / (ref**2))
    assert welch.shape == sft.f.shape

    th_psd_level = -10 * np.log10(ad.sample_rate / 2)
    if instrument is not None:
        th_psd_level += instrument.end_to_end_db

    db_threshold = 0.1  # 1 dB accuracy from the theoretical level
    assert abs(np.median(welch_db) - th_psd_level) < db_threshold
