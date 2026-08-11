# ==========================================
# Run PC_01_data_retrieval
# df_corrected, df_uncorrected, df_pressure
# ==========================================

station_cols = [col for col in df_corrected.columns if col not in ['timestamp', 'Date']]
results = []

n_stations = len(station_cols)
n_cols = 3
n_rows = (n_stations + n_cols - 1) // n_cols

fig, axes = plt.subplots(n_rows, n_cols, figsize=(16, 4 * n_rows))
axes = axes.flatten()

for idx, station in enumerate(station_cols):
    corr = df_corrected[station].values
    uncorr = df_uncorrected[station].values
    press = df_pressure[station].values

    df_clean = (corr > 0) & (uncorr > 0) & (~np.isnan(press))

    x = press[df_clean]
    y = np.log(corr[df_clean]) - np.log(uncorr[df_clean])

    if len(x) > 2: # atleast 3 data point to plot a graph
        # linear regression: Y = slope * X + intercept
        slope, intercept, r_value, p_value, std_err = linregress(x, y)
        beta = slope
        p0 = -intercept / beta if beta != 0 else np.nan
        r_squared = r_value ** 2

        results.append({'station': station,'beta': beta,'P0': p0})

        ax = axes[idx]
        ax.scatter(x, y, color='blue', alpha=0.5, s=15, label='Data points')

        x_line = np.linspace(x.min(), x.max(), 100)
        y_line = slope * x_line + intercept
        ax.plot(x_line, y_line, color='red', linewidth=2, label=f'Fit Line')

        ax.set_title(f"Station: {station}\n$\\beta$ = {beta:.5f}, $P_0$ = {p0:.2f} hPa\n($R^2$ = {r_squared:.4f})", fontsize=10)
        ax.set_xlabel("Pressure (P)")
        ax.set_ylabel("$\\ln(Corrected) - \\ln(Uncorrected)$")
        ax.grid(True, linestyle='--', alpha=0.5)
        ax.legend(fontsize=8)

# delete error subplots 
for i in range(len(station_cols), len(axes)):
    fig.delaxes(axes[i])

plt.tight_layout()
plt.show()

df_params = pd.DataFrame(results)
print("\n=== ตารางสรุปค่า Beta และ P0 ของแต่ละสถานี ===")
print(df_params.to_string(index=False))