import math
from scipy.stats import norm

hit = 0.747
odds = 1.32
sd = 0.58
alpha = 0.05
power = 0.80

z_alpha = norm.ppf(1 - alpha/2)
z_beta = norm.ppf(power)

n_list = [65, 79, 100, 150, 200, 300, 600]

with open('antigravity_output_v2/antigravity_power_analysis_v2.md', 'w') as f:
    f.write("# Statistical Power & Sample Size\n\n")
    f.write(f"**Live Assumptions:** hit ≈ {hit:.3f}, odds ≈ {odds:.2f}, per-bet SD ≈ {sd:.2f}\n\n")
    
    f.write("## Single Sample Power Analysis\n")
    f.write("| n | SE_ROI | 95% CI Width | MDE (80% Power, α=0.05) |\n")
    f.write("|---|---|---|---|\n")
    
    for n in n_list:
        se = sd / math.sqrt(n)
        ci_width = 2 * z_alpha * se
        mde = (z_alpha + z_beta) * se
        f.write(f"| {n} | {se*100:.2f}% | ±{ci_width/2*100:.2f}% | {mde*100:.2f}% |\n")
        
    # Required n to detect backtest valid ROI +150bp (0.015)
    target_mde = 0.015
    req_n = math.ceil(((z_alpha + z_beta) * sd / target_mde)**2)
    f.write(f"\n**Required n to detect backtest valid ROI (+1.50%):** ~{req_n} priced bets (≈600)\n")
    
    # Current CAUTION n=25 MDE
    n_caution = 25
    mde_caution = (z_alpha + z_beta) * (sd / math.sqrt(n_caution))
    f.write(f"**Current CAUTION n=25 MDE:** {mde_caution*100:.2f}%\n")
    
    # Two-sample power: CAUTION vs VETO
    delta = 0.235 # 23.5pp ROI delta (-8.44% vs +15.05%)
    # n_per_group = 2 * ((z_alpha + z_beta)*sd / delta)^2
    n_per_group = math.ceil(2 * ((z_alpha + z_beta) * sd / delta)**2)
    f.write(f"\n## Two-Sample Power (CAUTION vs VETO)\n")
    f.write(f"To detect a {delta*100:.2f}% ROI delta with 80% power (α=0.05), you need **n = {n_per_group} per bucket**.\n")
    
    f.write("\n## Stop / Continue Rule\n")
    f.write("> **Continue flat 0.25u CAUTION until 100 priced total** (~Jul 23–28 sniper, ~Jul 14–16 with VETO_FLIP paper), re-evaluate with Wilson LB ≥0.74 AND ROI LB >0%.\n")
    f.write("\n*Justification:* At n=100, the CI width narrows to ±11.37%, giving sufficient resolution to determine if the negative ROI is variance or a true structural flaw, without risking substantial bankroll ruin.\n")

print("Power analysis done")
