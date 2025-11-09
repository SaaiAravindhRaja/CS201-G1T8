# CS201 Data Structures and Algorithms — Team G1T8

## Skytrax User Reviews Dataset Analysis

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

## 🚀 Quick Start

### Interactive CLI (Recommended)

Run the interactive command-line interface to automatically compare all 5 index implementations:

```bash
python scripts/cli.py
```

Or on Windows, simply double-click `run_cli.bat`

**How it works:**
1. Select a dataset (default: Airlines) - just press Enter for quick start
2. Enter your search query
3. Choose AND/OR mode (default: AND)
4. Set document limit (default: 1,000)
5. View side-by-side comparison of all 5 indexes

**Navigation:**
- Type `b` at any prompt to go back to the previous step
- Type `q` at any prompt to exit immediately
- Press Enter to use defaults for fastest workflow

**Index Implementations Tested:**
- **Array Scan** - Linear search baseline
- **Inverted Index** - Fast keyword lookup
- **Bloom Filter** - Space-efficient probabilistic
- **K-Gram Index** - Fuzzy/wildcard matching
- **Suffix Array** - Substring searches

See [CLI_GUIDE.md](CLI_GUIDE.md) for detailed usage and example output.

### Running Scripts Manually

You can also run individual scripts:

