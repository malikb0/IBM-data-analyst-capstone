# Plan: Fix Step 5 Second Graph Y-Axis Scale

## Problem Analysis

In [`14_Lab_12_Finding_Outliers_Refactored.ipynb`](14_Lab_12_Finding_Outliers_Refactored.ipynb), **Step 5** creates side-by-side box plots to visualize the effect of outlier removal. The second graph ("After Removing TRUE Outliers Only") displays with an inappropriate y-axis scale because matplotlib doesn't automatically adjust when outliers are removed.

### Current Code Location
- Lines: **869-884** in the notebook file
- Section: Step 5 - Remove Only True Outliers and Create Clean DataFrame

## Root Cause

The boxplot code does not explicitly set y-axis limits:
```python
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))

# Before removing outliers (imputed data)
if len(df_imputed['ConvertedCompYearly'].dropna()) > 0:
    ax1.boxplot(df_imputed['ConvertedCompYearly'].dropna())
    ax1.set_title('After Imputation (Before Outlier Removal)')
    ax1.set_ylabel('Converted Compensation (Yearly)')

# After removing outliers
if len(df_no_outliers['ConvertedCompYearly'].dropna()) > 0:
    ax2.boxplot(df_no_outliers['ConvertedCompYearly'].dropna())
    ax2.set_title('After Removing TRUE Outliers Only')
    ax2.set_ylabel('Converted Compensation (Yearly)')
```

## Solution

Add y-axis limit setting for `ax2` after creating the boxplot:

```python
# After removing outliers
if len(df_no_outliers['ConvertedCompYearly'].dropna()) > 0:
    ax2.boxplot(df_no_outliers['ConvertedCompYearly'].dropna())
    ax2.set_title('After Removing TRUE Outliers Only')
    ax2.set_ylabel('Converted Compensation (Yearly)')
    # Set y-axis limit to match the upper bound for consistent scaling
    max_comp = df_no_outliers['ConvertedCompYearly'].max()
    ax2.set_ylim(0, int(max_comp * 1.1))  # Add 10% padding above max value
```

## Implementation Steps

1. **Read the notebook file** to confirm exact content at lines 869-884
2. **Apply diff** using `apply_diff` tool with:
   - Search: Current code block (lines 869-884)
   - Replace: Same code + two new lines for setting y-axis limit
3. **Verify** the changes by reading the modified section

## Expected Result

The second boxplot will display with a properly scaled y-axis that:
- Starts at 0
- Ends at approximately 110% of the maximum compensation value in the cleaned dataset
- Shows the data clearly without being "out of zoom"
