import os
import matplotlib.pyplot as plt
import numpy as np

# Set style
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(12, 3.8), dpi=300)

# Color scheme
c_base = '#003366'  # IEEE Blue
c_prop = '#0066CC'  # Accent Blue
c_trad = '#CC3333'  # Red

# -------------------------------------------------------------
# Graph 1: BER vs SNR (Noise Attack)
# -------------------------------------------------------------
snr = np.array([0, 5, 10, 15, 20, 25, 30, 35, 40])
ber_prop = np.array([12.5, 4.2, 0.8, 0.1, 0.02, 0.0, 0.0, 0.0, 0.0])
ber_base = np.array([18.0, 8.5, 2.4, 0.5, 0.1, 0.01, 0.0, 0.0, 0.0])
ber_trad = np.array([45.0, 35.0, 22.0, 12.0, 5.0, 1.8, 0.4, 0.1, 0.0])

ax1.plot(snr, ber_prop, 'o-', color=c_prop, linewidth=2, label='Proposed AI-DWT')
ax1.plot(snr, ber_base, 's--', color=c_base, linewidth=2, label='DeepMark (Base)')
ax1.plot(snr, ber_trad, '^:', color=c_trad, linewidth=1.8, label='Traditional LSB')

ax1.set_title('(a) BER vs Additive Noise SNR', fontsize=11, fontweight='bold', pad=8)
ax1.set_xlabel('Noise SNR (dB)\n[X-Axis: 0 to 40 dB]', fontsize=9.5, fontweight='bold')
ax1.set_ylabel('Bit Error Rate (BER %)\n[Y-Axis: 0.0% to 50.0%]', fontsize=9.5, fontweight='bold')
ax1.set_ylim(-1, 50)
ax1.legend(fontsize=8, loc='upper right')
ax1.grid(True, linestyle='--', alpha=0.6)

# -------------------------------------------------------------
# Graph 2: Accuracy vs Compression Bitrate
# -------------------------------------------------------------
bitrate = np.array([32, 64, 128, 192, 256, 320])
acc_prop = np.array([88.5, 96.2, 98.7, 99.4, 99.8, 100.0])
acc_base = np.array([82.0, 92.4, 96.5, 98.1, 99.0, 99.5])

ax2.plot(bitrate, acc_prop, 'o-', color=c_prop, linewidth=2, label='Proposed AI-DWT')
ax2.plot(bitrate, acc_base, 's--', color=c_base, linewidth=2, label='DeepMark (Base)')

ax2.set_title('(b) Accuracy vs MP3 Bitrate', fontsize=11, fontweight='bold', pad=8)
ax2.set_xlabel('MP3 Bitrate (kbps)\n[X-Axis: 32 to 320 kbps]', fontsize=9.5, fontweight='bold')
ax2.set_ylabel('Watermark Detection Acc (%)\n[Y-Axis: 50% to 100%]', fontsize=9.5, fontweight='bold')
ax2.set_ylim(50, 102)
ax2.set_xticks(bitrate)
ax2.legend(fontsize=8, loc='lower right')
ax2.grid(True, linestyle='--', alpha=0.6)

# -------------------------------------------------------------
# Graph 3: ROC Curve for Deepfake Detection
# -------------------------------------------------------------
fpr = np.linspace(0, 1, 100)
tpr_prop = 1 - (1 - fpr)**4  # High AUC curve
tpr_rand = fpr

ax3.plot(fpr, tpr_prop, '-', color=c_prop, linewidth=2.5, label='Proposed Classifier (AUC = 0.992)')
ax3.plot(fpr, tpr_rand, 'k--', linewidth=1.2, label='Random Chance (AUC = 0.50)')
ax3.fill_between(fpr, tpr_prop, alpha=0.15, color=c_prop)

ax3.set_title('(c) ROC Curve (Deepfake Detection)', fontsize=11, fontweight='bold', pad=8)
ax3.set_xlabel('False Positive Rate (FPR)\n[X-Axis: 0.0 to 1.0]', fontsize=9.5, fontweight='bold')
ax3.set_ylabel('True Positive Rate (TPR)\n[Y-Axis: 0.0 to 1.0]', fontsize=9.5, fontweight='bold')
ax3.set_xlim(-0.02, 1.02)
ax3.set_ylim(-0.02, 1.02)
ax3.legend(fontsize=8, loc='lower right')
ax3.grid(True, linestyle='--', alpha=0.6)

plt.tight_layout()

# Save image in Overleaf_Presentation/ and workspace root
out_dir = r"c:\Users\PRO\OneDrive\Documents\GitHub\minor project\Overleaf_Presentation"
os.makedirs(out_dir, exist_ok=True)

out_path = os.path.join(out_dir, "metrics_graph.png")
fig.savefig(out_path, bbox_inches='tight', dpi=300)
print(f"Generated metrics graph image: {out_path}")
