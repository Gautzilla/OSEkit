Public API
----------

.. _publicapi_usage:

This API provides tools for working on large sets of audio data.

Basically, the whole point of **OSEkit**'s Public API is to export large amounts of spectrograms and/or reshaped audio files with no consideration of the original format of the audio files.

The :class:`OSmOSE.public_api.dataset.Dataset` class is the cornerstone of **OSEkit**'s Public API.

Building a ``Dataset``
^^^^^^^^^^^^^^^^^^^^^^

At first, A ``Dataset`` is built from a raw folder containing the audio files to be processed.
For example, this folder containing 4 audio files plus some extra files:

.. code-block::

    7181.230205154906.wav
    7181.230205164906.wav
    7181.230205174906.wav
    7181.230205194906.wav
    foo
    ├── bar.zip
    └── 7181.wav
    bar.txt

Only the folder path and strptime format are required to initialize the ``Dataset``.

Extra parameters allow for e.g. localizing the files in a specific timezone or accounting for the measurement chain to link the raw wav data to the measured acoustic presure.
The complete list of extra parameters is provided in the :class:`OSmOSE.public_api.dataset.Dataset` documentation.

Once this is done, the ``Dataset`` can be built using the :meth:`OSmOSE.public_api.dataset.Dataset.build` method,
which organizes the folder in the following fashion:

.. code-block::

    data
    └── audio
        └── original
            ├── 7181.230205154906.wav
            ├── 7181.230205164906.wav
            ├── 7181.230205174906.wav
            ├── 7181.230205194906.wav
            └── original.json
    other
    ├── foo
    │   ├── bar.zip
    │   └── 7181.wav
    └── bar.txt
    dataset.json

The **original audio files** have been turned into a :class:`OSmOSE.core_api.audio_dataset.AudioDataset`.
In this ``AudioDataset``, one :class:`OSmOSE.core_api.audio_data.AudioData` has been created per original audio file.
Additionally, both this Core API ``Audiodataset`` and the Public API ``Dataset`` have been serialized
into the ``original.json`` and ``dataset.json`` files, respectively.


Running an ``Analysis``
^^^^^^^^^^^^^^^^^^^^^^^

In **OSEkit**, **Analyses** are run with the :meth:`OSmOSE.public_api.dataset.Dataset.run_analysis` method to process and export spectrogram images, spectrum matrices and audio files from original audio files.

.. note::

    **OSEkit** makes it easy to **reshape** the original audio: it is not bound to the original files, and can freely be reshaped in audio data of **any duration and sample rate**.

The analysis parameters are described by a :class:`OSmOSE.public_api.analysis.Analysis` instance passed as a parameter to this method.

Analysis Type
"""""""""""""

The ``analysis_type`` parameter passed to the initializer is a :class:`OSmOSE.public_api.analysis.AnalysisType` instance that defines the analysis output(s):

.. list-table:: Analysis Types
   :widths: 40 60
   :header-rows: 1

   * - Flag
     - Output
   * - ``AnalysisType.AUDIO``
     - Reshaped audio files
   * - ``AnalysisType.MATRIX``
     - Spectrum NPZ matrix files
   * - ``AnalysisType.SPECTROGRAM``
     - PNG spectrogram images

Multiple outputs can be selected thanks to a logical or ``|`` separator.

For example, if an analysis aims at exporting both the reshaped audio files and the corresponding spectrograms:

.. code-block:: python

    from OSmOSE.public_api.analysis import AnalysisType
    analysis_type = AnalysisType.AUDIO | AnalysisType.SPECTROGRAM


Analysis Parameters
"""""""""""""""""""

The remaining parameters of the analysis (begin and end **Timestamps**, duration and sample rate of the reshaped data...) are described in the :class:`OSmOSE.public_api.analysis.Analysis` initializer docstring.

.. note::

   If the ``Analysis`` contains spectral computations (either ``AnalysisType.MATRIX`` or ``AnalysisType.SPECTROGRAM`` is in ``analysis_type``), a `scipy ShortTimeFFT instance <https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.ShortTimeFFT.html#scipy.signal.ShortTimeFFT>`_ should be passed to the ``Analysis`` initializer.


Running the analysis
""""""""""""""""""""

To run the ``Analysis``, simply execute the :meth:`OSmOSE.public_api.dataset.Dataset.run_analysis` method:

.. code-block:: python

    dataset.run_analysis(analysis=analysis) # And that's it!


Simple Example: Reshaping audio
"""""""""""""""""""""""""""""""

Regardless of the format(s) of the original audio files (as always in **OSEkit**), let's say we just want to resample our original audio data at ``48 kHz`` and export it as ``10 s``-long audio files.

The corresponding ``Analysis`` is the following:

.. code-block:: python

    from OSmOSE.public_api.analysis import Analysis, AnalysisType
    from pandas import Timedelta

    analysis = Analysis(
        analysis_type = AnalysisType.AUDIO, # We just want to export the reshaped audio files
        data_duration=Timedelta("10s"), # Duration of the new audio files
        sample_rate=48_000, # Sample rate of the new audio files
        name="cool_reshape", # You can name the analysis, or keep the default name.
    )

    dataset.run_analysis(analysis=analysis) # And that's it!

Output 1
""""""""

.. _output_1:

Once the analysis is run, a :class:`OSmOSE.core_api.audio_dataset.AudioDataset` instance named ``cool_reshape`` has been created and added to the dataset's :attr:`OSmOSE.public_api.dataset.Dataset.datasets` field.

The dataset folder now looks like this:

.. code-block::

    data
    └── audio
        ├── original
        │   ├── 7181.230205154906.wav
        │   ├── 7181.230205164906.wav
        │   ├── 7181.230205174906.wav
        │   ├── 7181.230205194906.wav
        │   └── original.json
        └── cool_reshape
            ├── 2023_04_05_15_49_06_000000.wav
            ├── 2023_04_05_15_49_16_000000.wav
            ├── 2023_04_05_15_49_26_000000.wav
            ├── ...
            ├── 2023_04_05_20_48_46_000000.wav
            ├── 2023_04_05_20_48_56_000000.wav
            └── cool_reshape.json
    other
    ├── foo
    │   └── bar.zip
    └── bar.txt
    dataset.json

The ``cool_reshape`` folder has been created, containing the freshly created ``10 s``-long, ``48 kHz``-sampled audio files.

.. note::

    The ``cool_reshape`` folder also contains a ``cool_reshape.json`` serialized version of the cool_reshape ``AudioDataset``, which will be used for deserializing the ``dataset.json`` file in the dataset folder root.

Example: full analysis
""""""""""""""""""""""

Let's now say we want to export audio, spectrum matrices and spectrograms with the following parameters:

.. list-table:: Example analysis parameters
   :widths: 40 60
   :header-rows: 1

   * - Parameter
     - Value
   * - Begin
     - 00:30 after the begin of the original audio files
   * - End
     - 01:30 after the begin of the original audio files
   * - Data duration
     - ``10 s``
   * - Sample rate
     - ``48 kHz``
   * - FFT
     - ``hamming window``, ``1024 points``, ``40% overlap``

Let's first instantiate the ``ShortTimeFFT`` since we want to run a spectral analysis:

.. code-block:: python

    from scipy.signal import ShortTimeFFT
    from scipy.signal.windows import hamming

    sft = ShortTimeFFT(
        win=hamming(1_024), # Window shape,
        hop=round(1_024*(1-.4)), # 40% overlap
        fs=48_000,
        scale_to="magnitude"
    )

Then we are good for running the analysis:

.. code-block:: python

    from OSmOSE.public_api.analysis import Analysis, AnalysisType
    from pandas import Timedelta

    analysis = Analysis(
        analysis_type = AnalysisType.AUDIO | AnalysisType.MATRIX | AnalysisType.SPECTROGRAM, # Full analysis
        begin=dataset.get_dataset("original").begin + Timedelta(minutes=30), # 30m after the begin of the original dataset
        end=dataset.get_dataset("original").begin + Timedelta(hours=1.5), # 1h30 after the begin of the original dataset
        data_duration=Timedelta("10s"), # Duration of the output data
        sample_rate=48_000, # Sample rate of the output data
        name="full_analysis", # You can name the analysis, or keep the default name.
        fft=sft, # The FFT parameters
    )

    dataset.run_analysis(analysis=analysis) # And that's it!

Output 2
""""""""

Since the analysis contains both ``AnalysisType.AUDIO`` and spectral analysis types, two core API datasets were created and added to the dataset's :attr:`OSmOSE.public_api.dataset.Dataset.datasets` field:

* A :class:`OSmOSE.core_api.audio_dataset.AudioDataset` named ``full_analysis_audio`` (with the *_audio* suffix)
* A :class:`OSmOSE.core_api.spectro_dataset.SpectroDataset` named ``full_analysis``

The dataset folder now looks like this (the output from the first example was removed for convenience):

.. code-block::

    data
    └── audio
        ├── original
        │   ├── 7181.230205154906.wav
        │   ├── 7181.230205164906.wav
        │   ├── 7181.230205174906.wav
        │   ├── 7181.230205194906.wav
        │   └── original.json
        └── full_analysis_audio
            ├── 2023_04_05_16_19_06_000000.wav
            ├── 2023_04_05_16_19_16_000000.wav
            ├── 2023_04_05_16_19_26_000000.wav
            ├── ...
            ├── 2023_04_05_17_18_46_000000.wav
            ├── 2023_04_05_17_18_56_000000.wav
            └── full_analysis_audio.json
    processed
    └── full_analysis
        ├── spectrogram
        │   ├── 2023_04_05_16_19_06_000000.png
        │   ├── 2023_04_05_16_19_16_000000.png
        │   ├── 2023_04_05_16_19_26_000000.png
        │   ├── ...
        │   ├── 2023_04_05_17_18_46_000000.png
        │   └── 2023_04_05_17_18_56_000000.png
        ├── welches
        │   ├── 2023_04_05_16_19_06_000000.npz
        │   ├── 2023_04_05_16_19_16_000000.npz
        │   ├── 2023_04_05_16_19_26_000000.npz
        │   ├── ...
        │   ├── 2023_04_05_17_18_46_000000.npz
        │   └── 2023_04_05_17_18_56_000000.npz
        └── full_analysis.json
    other
    ├── foo
    │   └── bar.zip
    └── bar.txt
    dataset.json

As in :ref:`the output of example 1 <output_1>`, a ``full_analysis_audio`` folder was created, containing the reshaped audio files.

Additionally, the fresh ``processed`` folder contains the output spectrograms and NPZ matrices, along with the ``full_analysis.json`` serialized :class:`OSmOSE.core_api.spectro_dataset.SpectroDataset`.