🐳 Examples
===========

.. _examples:

This section gather **OSEkit** jupyter notebooks that complete typical tasks.

Example tasks will be completed with both the :ref:`Public <publicapi_usage>` and :ref:`Core API <coreapi_usage>` (see the :ref:`usage <usage>` section
for more info about the differences between the two APIs).

The examples use a small set of audio files that can be found in the **OSEkit** repository, under ``docs/source/_static/sample_audio``.
This sample dataset is made of 10 ``10 s``-long audio files sampled at ``48 kHz``. The 5 first and 5 last audio files are consecutive
(there is no recording gap between them), but both groups of 5 consecutive files are spaced by a ``30 s``-long recording gap.

===========

.. toctree::
   :maxdepth: 1

   example_reshaping_one_file

You have an audio file of given duration and sample rate and you want to extract a specific time period and/or resample it.

===========

.. toctree::
   :maxdepth: 1

   example_reshaping_multiple_files

Same example as the previous one, but at a larger scale: you have multiple audio files and want to reshape and export them.

===========

.. toctree::
   :maxdepth: 1

   example_spectrogram

Compute the spectrum matrix of an ``AudioData``, export it and/or plot it as a spectrogram.

===========

