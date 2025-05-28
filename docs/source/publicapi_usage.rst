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

