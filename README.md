# CS201 Data Structures and Algorithms — Team G1T8

## Skytrax User Reviews Dataset Analysis

<div align="center">
	<img src="https://img.shields.io/badge/Java-ED8B00?style=for-the-badge&logo=java&logoColor=white" alt="Java"/>
	<img src="https://img.shields.io/badge/Data%20Structures-Algorithm-blue?style=for-the-badge" alt="Data Structures"/>
	<img src="https://img.shields.io/badge/SMU-CS201-red?style=for-the-badge" alt="SMU CS201"/>
</div>

---

## 👥 Team G1T8 Members

<table align="center">
	<tr>
		<td align="center">
			<a href="https://github.com/SaaiAravindhRaja">
				<img src="https://github.com/SaaiAravindhRaja.png" width="80" alt="SaaiAravindhRaja"/><br/>
				<sub><b>SaaiAravindhRaja</b></sub><br/>
				<sub>Saai</sub>
			</a>
		</td>
		<td align="center">
			<a href="https://github.com/Onyxxx17">
				<img src="https://github.com/Onyxxx17.png" width="80" alt="Onyxxx17"/><br/>
				<sub><b>Onyxxx17</b></sub><br/>
				<sub>Aung</sub>
			</a>
		</td>
		<td align="center">
			<a href="https://github.com/regan-tan">
				<img src="https://github.com/regan-tan.png" width="80" alt="regan-tan"/><br/>
				<sub><b>regan-tan</b></sub><br/>
				<sub>Regan</sub>
			</a>
		</td>
		<td align="center">
			<a href="https://github.com/chuems">
				<img src="https://github.com/chuems.png" width="80" alt="chuems"/><br/>
				<sub><b>chuems</b></sub><br/>
				<sub>Chue</sub>
			</a>
		</td>
		<td align="center">
			<a href="https://github.com/thanh913">
				<img src="https://github.com/thanh913.png" width="80" alt="thanh913"/><br/>
				<sub><b>thanh913</b></sub><br/>
				<sub>Billy</sub>
			</a>
		</td>
	</tr>
</table>

---

## 📋 Project Overview

We analyze the Skytrax User Reviews Dataset to study how different data structures and algorithmic choices affect practical performance (time and space). The project focuses on implementing multiple data structures, running controlled experiments, and discussing theoretical vs practical trade-offs.

### 🎯 Objectives
- Implement and experiment with several data structures
- Compare theoretical complexity with empirical performance
- Analyze thresholds where one structure outperforms another

### 📊 Dataset
The dataset (provided in this repository under `Skytrax User Reviews Dataset/`) contains CSV files for airlines, airports, seats, and lounges with user reviews and metadata.

---

## 📁 Recommended Project Structure

```
CS201-G1T8/
├── README.md
├── docs/
│   ├── project-requirements.md
│   └── presentation/
│       └── slides.pdf
├── data/
│   └── Skytrax User Reviews Dataset/  # raw CSVs (already present)
├── src/
│   ├── main/
│   │   └── java/com/g1t8/
│   │       ├── algorithms/
│   │       ├── datastructures/
│   │       ├── experiments/
│   │       ├── models/
│   │       └── utils/
│   └── test/java/com/g1t8/
├── experiments/
│   ├── experiment1/
│   ├── experiment2/
│   └── experiment3/
├── results/
│   ├── performance-metrics/
│   ├── graphs/
│   └── analysis/
├── lib/
│   └── external-libraries/
└── scripts/
		├── compile.sh
		└── run-experiments.sh
```

---

## 🚀 Getting Started

### Prerequisites
- Java 11 or higher
- Git

### Quick setup
1. Clone the repository

```bash
git clone https://github.com/SaaiAravindhRaja/CS201-G1T8.git
cd CS201-G1T8
```

2. (Optional) Move the existing dataset into `data/` if you prefer a cleaner layout:

```bash
# From repo root
# mkdir -p data && mv "Skytrax User Reviews Dataset" data/
```

3. Compile (example)

```bash
./scripts/compile.sh  # or follow the instructions in scripts/compile.sh
```

4. Run experiments

```bash
./scripts/run-experiments.sh
```

---

## 🧪 Experiments (placeholders)

Each experiment lives in `experiments/experimentN/` with a README describing the goal, data subset, data structures compared, and results.

---

## 🤝 Contribution & Submission

This repository contains the full source code and documentation to be submitted for the CS201 project. Before submission, ensure:
- All source code is under `src/`
- Each experiment folder contains the code and a short README
- `README.md` at repo root explains how to run the code (this file)

---

## 📞 Contact
Reach out to any team member via their GitHub profiles listed above.

---

SMU • CS201 Data Structures and Algorithms • AY2025/26 Term 1
