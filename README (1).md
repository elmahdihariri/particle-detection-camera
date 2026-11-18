# Particle detection with a camera sensor – cloud chamber project

Detection of ionising particles (cosmic muons, radioactive emissions) directly
on the silicon sensor of a camera, with a Python / OpenCV script that flags the
video frames where a particle may have hit the sensor.

Final-year project, Licence de Physique – Université Jean Monnet, Saint-Étienne (2024/25).
The wider project covered a home-built cloud chamber (Peltier cooling) and the
DECO approach (particle detection with smartphone camera sensors). This
repository contains the image-analysis part.

## Principle

When a charged particle crosses the silicon of a camera sensor, it creates
electron–hole pairs (about 3.6 eV per pair). The charge collected in the pixels
shows up as a bright spot or a short line in the image, even with the lens
covered and no light reaching the sensor.

Order of magnitude for our sensor (Teledyne e2v EV76C570, 1600 × 1200, 4.5 µm
pixels, 10-bit ADC), for a particle depositing 50 keV in one pixel:

```
electrons      n = 50 000 eV / 3.6 eV          ≈ 13 900 e⁻   (read noise ≈ 5 e⁻ RMS)
digital value  DN = n / 30 000 e⁻ × 1023       ≈ 474 / 1023  (well capacity ≈ 30 000 e⁻, typical value)
grey level     474 / 1023 × 255                ≈ 118 / 255
```
<img width="731" height="991" alt="image" src="https://github.com/user-attachments/assets/6590d5f7-c86f-4e37-8c49-74158330d44c" /> 
<img width="679" height="361" alt="image" src="https://github.com/user-attachments/assets/319c1597-8c61-4990-b119-4d49740e9786" />


So a single event is well above the read noise and should be visible in the image.

## Setup

- IDS camera (uEye), lens covered, sealed in a box wrapped in black so no light gets in.
- Two videos recorded with the uEye software:
  - **without source**: background noise only (dark current, read noise, cosmic rays);
  - **with source**: a small radioactive fragment (tungsten) placed next to the sensor.

## Method – `detection_traces.py`

1. **Background measurement** – every frame of the video *without* source is
   converted to greyscale and its mean brightness is computed.
2. **Threshold** – the detection threshold is set from these values:

   ```
   threshold = mean + k · σ        (k = 2 by default)
   ```

3. **Detection** – every frame of the video *with* source whose mean brightness is
   above the threshold is counted as a detection and saved as a PNG in
   `detected_frames/`.
4. **Summary** – number of frames analysed, number of detections and detection rate.

In the project, the extracted images were also analysed with ImageJ
(intensity profile): it showed an isolated, abnormally bright pixel in a dark
region, consistent with a particle (probably a muon) hitting the sensor.

## Usage

```bash
pip install -r requirements.txt
python detection_traces.py
```

Put `video_without_source.avi` and `video_with_source.avi` in the same folder
as the script (the paths are set at the top of the file). The videos are not
included in the repository because of their size.

Example output (on test videos):

```
Bruit de fond : moyenne = 38.81, écart-type = 0.05
Seuil de détection : 38.90
Détection 1 (image 11) : luminosité = 65.65
...
Images analysées : 50
Détections : 3
Taux de détection : 6.0 %
```

## Limitations

These limits came out of the experiments, and they matter for reading the results:

- **Sensor noise**: the sensor is designed to work below −20 °C, but it ran at
  room temperature. Thermal noise was high, which made real events hard to tell
  apart from noise.
- **Weak source**: with a source of low and unknown activity, events were rare
  and not reproducible, so the threshold could not be calibrated properly.
- **Statistical threshold**: with k = 2, about 2 % of noise-only frames go above
  the threshold (false positives). Raising k reduces them but misses faint events.
- **Whole-frame mean**: a single particle only lights up a few pixels, so its
  effect on the mean of a 1600 × 1200 image is small. Only strong events are
  caught.

## Next steps

- Detect at pixel level instead of on the frame mean: subtract a background
  image, threshold each pixel, then keep only small connected regions
  (contours of a few pixels) as candidate particles.
- Cool the sensor to reduce thermal noise.
- Use a calibrated source with known activity to measure the detection
  efficiency and tune the threshold.
- Classify events by shape (dot, straight line, curved track) to tell muons,
  electrons and alpha particles apart.
