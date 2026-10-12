# Loop Closure Detection with Scan Context (NCLT)

LiDAR-based place recognition on the [NCLT dataset](http://robots.engin.umich.edu/nclt/) (AMR, Exercise 3).
Each Velodyne scan is turned into a **Scan Context** descriptor; scans are then matched against
earlier/later scans to detect loop closures, and the results are evaluated against the ground-truth
trajectory.

## Pipeline

1. **Load scans** – `DataLoader` reads the NCLT Velodyne `.bin` files (uint16 x/y/z, 5 mm scale,
   −100 m offset) and the ground-truth poses CSV. Only every `SUBSAMPLING`-th scan is used.
2. **Compute descriptors** – `ScanContext` flips the z-axis (the sensor is mounted upside down),
   keeps points with height in `(mask_low, mask_high)`, bins them into a polar grid of
   `num_rings × num_sectors` up to `max_range`, and stores the maximum height per bin.
3. **Match** – `Matcher` excludes scans within `TEMPORAL_WINDOW` frames, pre-selects the `top_k`
   candidates by L2 distance between ring keys (row means), and then computes the rotation-invariant
   L1 distance (minimum over all sector shifts) on those candidates. The best match is labelled a
   true loop if the two scans are less than `GT_DISTANCE_THRESHOLD` metres apart.
4. **Evaluate** – `Evaluator` prints AP, AUC-ROC and precision/recall/F1 at `MATCH_THRESHOLD`,
   and plots the precision-recall curve and a trajectory map with true/false positives.

## Structure

```
3dscan/
├── main.py                 # entry point, sets parameters and runs the pipeline
├── visualize_scan.py       # 3D scatter plot of a single Velodyne scan
├── src/
│   ├── data_loader.py      # reading scans and ground truth
│   ├── descriptor.py       # Scan Context descriptor
│   └── matcher.py          # ring-key pre-filter + Scan Context matching
├── experiments/
│   ├── pipeline.py         # descriptor computation, scan ↔ pose association
│   └── evaluator.py        # metrics and plots
└── requirements.txt        # pinned dependencies
```

## Setup

Tested with Python 3.12.

```bash
python3 -m venv scancontext
source scancontext/bin/activate
pip install -r requirements.txt
```

### Data

> **Note:** The dataset is **not included** in this repository because of its size, and it is
> distributed by its authors under its own license. Download it yourself from the official source.

This project uses the **University of Michigan North Campus Long-Term (NCLT) Vision and LIDAR
Dataset**: <http://robots.engin.umich.edu/nclt/>

On the download page, get the following for the session **2012-01-15**:

- **Velodyne** → `2012-01-15_vel.tar.gz`
- **Ground Truth Pose** → `groundtruth_2012-01-15.csv`

Extract the archive and place the files like this:

```
3dscan/data/
├── 2012-01-15_vel/2012-01-15/velodyne_sync/*.bin
└── groundtruth_2012-01-15.csv
```

`visualize_scan.py` uses a scan from the **2012-01-08** session
(`data/2012-01-08_vel/2012-01-08/velodyne_sync/`). Download that Velodyne archive the same way
if you want to run it, or change the file path in the script.

If you use the dataset, please cite:

> N. Carlevaris-Bianco, A. K. Ushani, and R. M. Eustice, "University of Michigan North Campus
> long-term vision and lidar dataset," *International Journal of Robotics Research*, vol. 35,
> no. 9, pp. 1023–1035, 2016.

## Usage

```bash
source scancontext/bin/activate
python main.py             # run loop closure detection + evaluation
python visualize_scan.py   # view a single scan
```

`main.py` saves `precision_recall_curve.png` and `map.png` in the current directory.

### Parameters (`main.py`)

| Parameter               | Default | Meaning                                              |
|-------------------------|---------|------------------------------------------------------|
| `MATCH_THRESHOLD`       | 0.8     | Scan Context distance below which a match is accepted |
| `TEMPORAL_WINDOW`       | 10      | Neighbouring frames excluded from matching            |
| `GT_DISTANCE_THRESHOLD` | 15.0    | Max. distance (m) for a ground-truth loop             |
| `SUBSAMPLING`           | 10      | Use every n-th scan                                   |
| `num_rings`/`num_sectors` | 40 / 80 | Descriptor resolution                              |
| `mask_low`/`mask_high`  | 0.2 / 10.0 | Height filter (m)                                 |

Further `Matcher` and `ScanContext` options: `top_k` (default 50) and `max_range` (default 80 m).
