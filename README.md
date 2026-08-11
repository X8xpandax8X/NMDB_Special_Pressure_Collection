# NMDB Pressure Correction Optimization

A personal quantitative research tool for re-evaluating and optimizing barometric efficiency coefficients ($\beta$) for cosmic ray neutron monitor stations across the **Neutron Monitor Database (NMDB)** network.

> **Disclaimer:** This is an independent, ongoing personal project. The methods, fittings, and theoretical frameworks implemented here are under active development and have not been 100% fully validated against formal theoretical standards or peer-reviewed literature.

---

## Overview & Motivation

In cosmic ray physics, atmospheric pressure fluctuations significantly affect ground-level neutron monitor count rates. Standard pressure corrections typically apply an exponential barometric response model:

$$I_{\text{corr}} = I_{\text{uncorr}} \cdot e^{\beta (P - P_0)}$$

However, cosmic ray particles observed at different station locations possess varying **rigidity cutoffs** (energy spectra). Because the barometric coefficient $\beta$ depends on the primary and secondary particle energy distribution, assuming uniform or static coefficients can introduce subtle inaccuracies into long-term intensity measurements.

This project automatically retrieves $counts/sec$ data (Uncorrected, Pressure Corrected, and Atmospheric Pressure) across multiple NMDB stations, uses **Linear Regression** to fit station-specific $\beta$ and baseline pressure $P_0$ parameters, and re-applies these customized parameters back to raw data for enhanced correction precision.

---

## Mathematical Model

By taking the natural logarithm of both sides of the standard pressure correction equation:

$$\ln(I_{\text{corr}}) = \ln(I_{\text{uncorr}}) + \beta (P - P_0)$$

Rearranging into linear form ($y = mx + c$):

$$\ln\left(\frac{I_{\text{corr}}}{I_{\text{uncorr}}}\right) = \beta \cdot P - \beta P_0$$

Where:
* **$y$ (Dependent Variable):** $\ln(I_{\text{corr}}) - \ln(I_{\text{uncorr}})$
* **$x$ (Independent Variable):** Atmospheric Pressure $P$ (in hPa / mbar)
* **$m$ (Slope):** Fitted Barometric Coefficient ($\beta$)
* **$c$ (Y-intercept):** $-\beta P_0$, giving $P_0 = -\frac{c}{\beta}$

---

## Features

* **Automated Data Pipeline:** Direct API/HTTP ingestion of multi-station ASCII data from NMDB NEST.
* **Multi-Station Support:** Handles $10+$ neutron monitor stations concurrently.
* **Missing Data Resilience:** Gracefully parses missing or malformed records without breaking row alignment.
* **Linear Regression Fitting:** Estimates $\beta$, $P_0$, $R^2$, and $p$-values per station using `scipy.stats`.
* **Database Integration:** Stores raw, corrected, and calculated parameter outputs into a local SQLite database (`.db`).
* **Visualization:** Generates side-by-side scatter plots and regression line fits for fast visual inspection.

---

## Project Workflow

1. **Ingestion (`fetch_nmdb`):** Queries NMDB for `uncorrected`, `corr_for_efficiency`, and barometric pressure data in $counts/s$.
2. **Preprocessing:** Merges station datasets on `timestamp` and cleans missing/invalid values.
3. **Regression Fitting:** Transforms count data into logarithmic ratios and computes linear regression parameters ($m, c$).
4. **Parameter Extraction:** Derives station-specific optimal $\beta$ and reference pressure $P_0$.
5. **Re-correction & Storage:** Re-applies fitted coefficients to raw counts and saves structured tables to SQLite.

---

## Requirements

* Python 3.8+
* `pandas`
* `numpy`
* `requests`
* `matplotlib`
* `scipy`

Install dependencies:
```bash
pip install pandas numpy requests matplotlib scipy