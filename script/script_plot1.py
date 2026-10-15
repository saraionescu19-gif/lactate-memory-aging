## Plot 1:

import os                                    ## to find the folder of this script
import numpy as np                           ## maths with arrays (as in class)
import matplotlib.pyplot as plt              ## plotting (as in class)
import pandas as pd                          ## ONLY used to read the Excel file
from scipy import stats                      ## ready-made statistics (Kruskal-Wallis, normal distribution, ...)

os.chdir(os.path.dirname(os.path.abspath(__file__)))     ## work in the folder of this script (as in Tutorial week 5)

np.random.seed(2023)                         ## fixed seed -> the random numbers (bootstrap, jitter) are the same every run



## settings used everywhere
ages = [7, 14, 21]                                           ## ages (in days) at which memory was tested
genotypes = ["Control", "Downregulation", "Upregulation"]    ## the 3 groups of flies (names as in the Excel file)

## short names for the plot
labels = {"Control": "Control",
          "Downregulation": "dLdh down",
          "Upregulation": "dLdh up"}

## one colour per genotype (purple, blue, red)
colors = {"Control": "#7B3FA0",
          "Downregulation": "#1F6FD1",
          "Upregulation": "#E0472B"}

grey = "#6b6b6b"                             ## colour for less important text
light_grey = "#e6e6e6"                       ## colour for grid lines

results_lines = []                           ## every result printed is also stored here and saved to results_plot1.txt

def show(text=""):
    ## print a line in the terminal AND remember it for the results file
    print(text)
    results_lines.append(text)
## load the data

#####################################################################################

## The Excel file has one column per group, for example "21d Control Naive" or "21d Control Trained".
## Each number is the COURTSHIP INDEX (CI) of one male fly = fraction of 10 minutes spent courting a female.
##   - "Naive" males: never rejected by a female before
##   - "Trained" males: rejected by a female the day before -> if they REMEMBER, they court less

data_folder = "data/doi_10_5061_dryad_2v6wwpzsb__v20230227"     ## folder with the Excel files downloaded from Dryad

courtship = pd.read_excel(f"{data_folder}/Figure2B_2C.xlsx", sheet_name="Courtship Indexes")   ## read the courtship sheet
authors_mi = pd.read_excel(f"{data_folder}/Figure2B_2C.xlsx", sheet_name="Memory Indexes")     ## the authors' memory indexes (only used as a check)


naive = {}                                   ## dictionary: group name -> array of naive CIs
trained = {}                                 ## dictionary: group name -> array of trained CIs

for age in ages:                             ## go through the 3 ages
    for g in genotypes:                      ## and the 3 genotypes -> 9 groups in total
        group = f"{age}d {g}"                ## group name, for example "21d Control"
        naive[group] = courtship[f"{group} Naive"].dropna().to_numpy()       ## take the columd with that certain name from the tabel in the Excel and then remove the empty cells (dropna)
        trained[group] = courtship[f"{group} Trained"].dropna().to_numpy()   ## turn the column into a numpy array (to_numpy)
        
##################################################################

## memory index (MI) of every trained fly:

## MI = 1 - CI_trained / average(CI_naive)
##   MI = 0  -> the fly courts as much as a naive fly       -> no memory
##   MI = 1  -> the fly stopped courting completely          -> perfect memory
##   MI < 0  -> the fly courts even more than a naive fly    -> no memory

memory = {}                                  ## an empty dictionary where the group name -> array of memory indexes will be saved later

for age in ages:
    for g in genotypes:
        group = f"{age}d {g}"
        memory[group] = 1 - trained[group] / np.mean(naive[group])           ## one MI per trained fly

        ## check: our numbers must be the same as the authors' numbers (difference smaller than 0.0001)
        theirs = authors_mi[group].dropna().to_numpy() ## making an array of the memory index results from the paper
        if np.max(np.abs(memory[group] - theirs)) > 0.0001:
            print("WARNING: memory index different from the authors for", group) ## we take the difference between the two arrays and make all the differences positive and then the biggest difference is checked (is it larger than 0.0001) --> if yes then we have an error

show("=" * 80)
show("Plot 1 - MEMORY  (memory indexes checked against the authors' values)")
show("=" * 80)

#####################################################
## mean memory index with uncertainties


## mean MI = 1 - mean(T) / mean(N)          T = trained CIs, N = naive CIs
##
## 1) STATISTICAL uncertainty: from the spread of the trained flies
##       sigma_stat = ( std(T) / root(n_T) ) / mean(N)
## 2) NORMALISATION uncertainty: the naive average mean(N) is also measured with an error,
##    and it moves ALL the memory indexes of the group together
## Error propagation: (how much does an error in mean(N) change the MI)
##       d(MI)/d(mean N) = mean(T) / mean(N)^2   ->   sigma_norm = mean(T) / mean(N)^2 * std(N) / root(n_N)
## 3) TOTAL uncertainty: the two are independent, so we add them in quadrature (we combine the two uncertanties into one error bar)
##       sigma_total = root( sigma_stat^2 + sigma_norm^2 )

mean_mi = {}                                 ## dictionaries to store the results of every group
stat_err = {}
norm_err = {}
total_err = {}

show("")
show("Group                n_naive  n_trained   mean MI    stat    norm   total")
for age in ages:
    for g in genotypes:
        group = f"{age}d {g}"
        N = naive[group]                     ## short names to keep the formulas readable
        T = trained[group]

        mean_mi[group] = 1 - np.mean(T) / np.mean(N)
        stat_err[group] = (np.std(T, ddof=1) / np.sqrt(len(T))) / np.mean(N)
        norm_err[group] = np.mean(T) / np.mean(N)**2 * (np.std(N, ddof=1) / np.sqrt(len(N)))
        total_err[group] = np.sqrt(stat_err[group]**2 + norm_err[group]**2)

        show(f"{group:<20} {len(N):>7} {len(T):>10} {mean_mi[group]:>9.3f} {stat_err[group]:>7.3f} {norm_err[group]:>7.3f} {total_err[group]:>7.3f}")


###############################################################################################
## bootstrap (10 000 "new experiments"): since we don t have more repetitions of the experiment we reuse the flies we already have but "reshuffle" them so we can lower the uncertainty of the average 


## Idea: we pretend to repeat the experiment many times by drawing flies from our own data
## WITH replacement (the same fly can be drawn twice). The spread of the 10 000 results = the uncertainty.

n_boot = 10000                               ## number of bootstrap repetitions

def bootstrap_mean_mi(N, T):
    ## returns 10 000 bootstrap values of the mean memory index of one group
    results = np.zeros(n_boot)                               ## make empty array to fill (10000 spaces)
    for i in range(n_boot):
        N_new = np.random.choice(N, size=len(N), replace=True)   ## new set of naive flies
        T_new = np.random.choice(T, size=len(T), replace=True)   ## new set of trained flies
        results[i] = 1 - np.mean(T_new) / np.mean(N_new)          ## mean MI of this "new experiment"
    return results

boot = {}                                    ## dictionary: group name -> 10 000 bootstrap means
for age in ages:
    for g in genotypes:
        group = f"{age}d {g}"
        boot[group] = bootstrap_mean_mi(naive[group], trained[group])
        
        
############################################################################################
## statistical tests between the genotypes (same tests as the paper)


## a) Kruskal-Wallis test: do the 3 genotypes differ at this age? 
## b) Dunn's test: which genotype differs from control? 
## c) Cliff's delta: HOW BIG is the difference? (effect size between -1 and +1)

def dunn_test(all_groups, i, j, n_comparisons):
    ## Dunn's test between group i and group j.
    ## 1) give every fly a rank (1 = lowest memory index, 2 = second lowest, ...) using ALL flies of this age
    ## 2) compare the average rank of the two groups
    ## 3) z = difference of average ranks / its uncertainty  -> p-value from the normal distribution
    ## 4) multiply p by the number of comparisons (Bonferroni correction, because we do 2 tests per age)
    
    all_values = np.concatenate(all_groups)                  ## all flies of this age in one array
    ranks = stats.rankdata(all_values)                       ## rank of every fly
    N_total = len(all_values)                                ## N here stands for number not naive as before

    ## cut the ranks back into the groups
    start = 0
    mean_ranks = []
    for group_values in all_groups:
        mean_ranks.append(np.mean(ranks[start:start + len(group_values)])) ## maiking one average rank per genotype by moving through the array from group to group
        start = start + len(group_values)

    ## correction for flies with exactly the same value (ties)
    values, counts = np.unique(all_values, return_counts=True)      ## list every value once and then we check how many times each one appears
    tie_correction = np.sum(counts**3 - counts) / (12 * (N_total - 1)) ## the standard formula for Dunns test (apllying the correction)

    ## uncertainty on the difference of mean ranks
    n_i, n_j = len(all_groups[i]), len(all_groups[j])
    sigma = np.sqrt((N_total * (N_total + 1) / 12 - tie_correction) * (1 / n_i + 1 / n_j))

    z = (mean_ranks[i] - mean_ranks[j]) / sigma                  ## how many sigma apart
    p = 2 * (1 - stats.norm.cdf(abs(z)))                         ## two-sided p-value
    p = min(1.0, p * n_comparisons)                              ## Bonferroni correction (with every test we have more chances to get significant value random so we minimise that possibility by multiplying with the number of tests we re making)
    return z, p

def cliffs_delta(x, y):
    ## Cliff's delta = P(fly from x > fly from y) - P(fly from x < fly from y)
    ## we compare every fly of x with every fly of y
    bigger = 0
    smaller = 0
    for a in x:
        bigger = bigger + np.sum(a > y)
        smaller = smaller + np.sum(a < y) ## how many flies in y have a higher memory than a (we count them with np.sum)
    return (bigger - smaller) / (len(x) * len(y)) ## effect size: how much worse/better the mutant memory is vs control, independent of the number of flies (-1 = always worse, 0 = no difference, +1 = always better)

def stars(p):
    ## turn a p-value into stars, as in the paper
    if p < 0.0001:
        return "****"
    elif p < 0.001:
        return "***"
    elif p < 0.01:
        return "**"
    elif p < 0.05:
        return "*"
    else:
        return "ns"

def p_text(p):
    ## nice text for a p-value, for example "p = 0.012" or "p = 9.1e-6"
    if p < 0.001:
        exponent = int(np.floor(np.log10(p)))
        return f"p = {p / 10**exponent:.1f}e{exponent}"
    return f"p = {p:.3f}"

kruskal = {}                                 ## age -> (H, p)
dunn = {}                                    ## group name -> (z, p) for the comparison with control
delta = {}                                   ## group name -> Cliff's delta vs control

show("")
show("Kruskal-Wallis test per age + Dunn's test vs control (Bonferroni, 2 comparisons) + Cliff's delta")
for age in ages:
    groups_this_age = [memory[f"{age}d {g}"] for g in genotypes]       ## list of 3 arrays: control, down, up
    H, p = stats.kruskal(*groups_this_age)                               ## Kruskal-Wallis test
    kruskal[age] = (H, p)
    show(f"  {age} days: Kruskal-Wallis H = {H:.2f}, {p_text(p)}  {stars(p)}")

    for j in [1, 2]:                                                      ## 1 = Downregulation, 2 = Upregulation
        group = f"{age}d {genotypes[j]}"
        z, p = dunn_test(groups_this_age, 0, j, n_comparisons=2)         ## 0 = Control
        dunn[group] = (z, p)
        delta[group] = cliffs_delta(memory[group], memory[f"{age}d Control"])
        show(f"     {genotypes[j]:<15} vs Control: Dunn z = {z:5.2f}, adjusted {p_text(p)} {stars(p):<4} | Cliff's delta = {delta[group]:+.2f}")
        

#####################################################
## memory as a percentage of the control flies of the same age


## percentage = mean MI of the mutant / mean MI of the control (same age) x 100
## 95% range: take the same ratio for the 10 000 bootstrap repetitions and keep the middle 95%

percent = {}                                 ## group name -> percentage
percent_low = {}                             ## lower end of the 95% range
percent_high = {}                            ## upper end of the 95% range

show("")
show("Memory as % of the control flies of the same age (bootstrap 95% range)")
for age in ages:
    control = f"{age}d Control"
    for g in genotypes[1:]:                                          ## only the 2 mutant genotypes
        group = f"{age}d {g}"
        percent[group] = 100 * mean_mi[group] / mean_mi[control]     ## the mutant mean memory as a percentage of the control at the same age
        ratios = 100 * boot[group] / boot[control]                   ## the sme thing as above but for all 10 000 bootstrap repeats
        percent_low[group] = np.percentile(ratios, 2.5)              ## cutoff the lowest and highest 2.5 % so we re left with the middle 95% range
        percent_high[group] = np.percentile(ratios, 97.5)
        show(f"  {group:<20} {percent[group]:5.0f}%   [{percent_low[group]:.0f}% to {percent_high[group]:.0f}%]")
        

#####################################################
## the plot


def half_violin(ax, values, x, color):
    ## draws the "cloud": a smooth shape showing where most flies are, on the LEFT of position x
    density = stats.gaussian_kde(values)                     ## smooth version of a histogram
    y = np.linspace(values.min(), values.max(), 200)        ## 200 heights between the lowest and highest fly
    width = density(y)                                       ## how many flies at each height
    width = width / width.max() * 0.42                       ## scale so the widest part is 0.42 wide
    ax.fill_betweenx(y, x, x - width, color=color, alpha=0.3, linewidth=0)   ## filled shape
    ax.plot(x - width, y, color=color, linewidth=1.2)                          ## outline

fig, ax = plt.subplots(figsize=(15, 6.8))    ## one big plot

## 1) x-position of every group: the 3 ages are 4.2 apart, the 3 genotypes 1.15 apart inside an age
xpos = {}
for a_i, age in enumerate(ages):             ## enumerate gives 0,1,2 together with 7,14,21
    for g_i, g in enumerate(genotypes):
        xpos[f"{age}d {g}"] = a_i * 4.2 + g_i * 1.15

## 2) dashed line at 0 = no memory
ax.axhline(0, color=grey, linewidth=1, linestyle="--", zorder=0)
ax.text(-1.45, 0.015, "no memory", color=grey, fontsize=8.5, va="bottom")

## 3) draw every group
for age in ages:
    for g in genotypes:
        group = f"{age}d {g}"
        x = xpos[group]
        values = memory[group]
        c = colors[g]

        ## the cloud (density shape)
        half_violin(ax, values, x - 0.06, c)

        ## the rain: every fly as a dot, moved sideways by a small random amount (jitter) so they don't overlap
        jitter = np.random.uniform(0.10, 0.42, size=len(values))
        ax.scatter(x + jitter, values, s=9, color=c, alpha=0.55, linewidth=0, zorder=2)

        ## the box: median and the middle 50% of the flies (25th to 75th percentile)
        q25, median, q75 = np.percentile(values, [25, 50, 75])
        ax.add_patch(plt.Rectangle((x - 0.05, q25), 0.10, q75 - q25, facecolor="white", edgecolor=c, linewidth=1.2, zorder=3))
        ax.plot([x - 0.05, x + 0.05], [median, median], color=c, linewidth=2, zorder=4)

        ## the mean (diamond): thin bar with wide caps = total uncertainty, thick bar = statistical uncertainty
        ax.errorbar(x - 0.22, mean_mi[group], yerr=total_err[group], fmt="none", ecolor="black", elinewidth=1, capsize=4, zorder=5)
        ax.errorbar(x - 0.22, mean_mi[group], yerr=stat_err[group], fmt="D", markersize=6, markerfacecolor=c,
                    markeredgecolor="white", ecolor="black", elinewidth=2.4, capsize=0, zorder=6)

        ## number of flies under each group
        ax.text(x + 0.1, -0.62, f"n={len(values)}", fontsize=8, color=grey, ha="center")

## 4) significance brackets (Dunn's test vs control) and Kruskal-Wallis result for every age
for age in ages:
    x_control = xpos[f"{age}d Control"]
    for level, g in enumerate(genotypes[1:]):                 ## level 0 = down (lower bracket), level 1 = up (higher bracket)
        group = f"{age}d {g}"
        z, p = dunn[group]
        x_mutant = xpos[group]
        y = 1.06 + level * 0.17                               ## height of the bracket
        if p < 0.05:
            text_color, weight = "black", "bold"             ## significant -> black and bold
        else:
            text_color, weight = grey, "normal"              ## not significant -> grey
        ax.plot([x_control, x_control, x_mutant, x_mutant], [y - 0.03, y, y, y - 0.03], color=text_color, linewidth=1)
        ax.text((x_control + x_mutant) / 2, y + 0.012, f"{stars(p)}  {p_text(p)}   δ={delta[group]:+.2f}",
                ha="center", va="bottom", fontsize=8.3, color=text_color, fontweight=weight)

    H, p = kruskal[age]
    ax.text(xpos[f"{age}d Downregulation"], 1.47, f"{age} days   ·   Kruskal–Wallis H = {H:.1f}, {p_text(p)}",
            ha="center", fontsize=9.5, fontweight="bold" if p < 0.05 else "normal")

## vertical lines between the ages
ax.axvline(4.2 - 0.85, color=light_grey, linewidth=1.2, zorder=0)
ax.axvline(2 * 4.2 - 0.85, color=light_grey, linewidth=1.2, zorder=0)

## 5) row at the bottom: memory as % of the control of the same age
ax.axhline(-0.68, color=light_grey, linewidth=0.8)
ax.text(-1.45, -0.80, "memory as %\nof control:", fontsize=8.5, va="center", style="italic")
for age in ages:
    control = f"{age}d Control"
    ax.text(xpos[control] + 0.1, -0.76, "100%", ha="center", va="center", fontsize=11, color=colors["Control"], fontweight="bold")
    ax.text(xpos[control] + 0.1, -0.87, "(reference)", ha="center", va="center", fontsize=7.8, color=grey)
    for g in genotypes[1:]:
        group = f"{age}d {g}"
        ax.text(xpos[group] + 0.1, -0.76, f"{percent[group]:.0f}%", ha="center", va="center", fontsize=11,
                color=colors[g], fontweight="bold")
        ax.text(xpos[group] + 0.1, -0.87, f"[{percent_low[group]:.0f}–{percent_high[group]:.0f}%]", ha="center",
                va="center", fontsize=7.8, color=grey)

## 6) axes, labels and title
ax.set_xticks([xpos[group] + 0.1 for group in xpos])                     ## one tick under every group
ax.set_xticklabels([labels[group.split(" ")[1]] for group in xpos])       ## "21d Control" -> "Control"
ax.set_yticks([-0.5, 0, 0.5, 1.0, 1.5])
ax.set_xlim(-1.5, xpos["21d Upregulation"] + 0.8)
ax.set_ylim(-1.0, 1.62)
ax.set_ylabel("Memory index  (1 − CI$_{trained}$ / mean CI$_{naive}$)")
ax.set_title("Long-term courtship memory of every fly, by age and genotype", loc="center", fontweight="bold", fontsize=14, pad=12)
ax.grid(axis="y", color=light_grey, linewidth=0.8)
ax.set_axisbelow(True)                                                   ## grid behind the data
ax.spines["top"].set_visible(False)                                      ## remove the top and right frame lines
ax.spines["right"].set_visible(False)

## 7) legend explaining the symbols (empty plots used only to create the legend entries)
ax.plot([], [], color=grey, linewidth=6, alpha=0.4, label="density of flies")
ax.scatter([], [], s=12, color=grey, label="one fly")
ax.add_patch(plt.Rectangle((0, 0), 0, 0, facecolor="white", edgecolor=grey, label="median & middle 50%"))
ax.errorbar([], [], yerr=[], fmt="D", markersize=6, markerfacecolor="white", markeredgecolor="black", ecolor="black",
            label="mean ± stat. (thick) / total (thin) uncertainty")
ax.legend(loc="upper left", bbox_to_anchor=(0.0, -0.1), ncol=4, frameon=False, fontsize=8.5)
ax.text(0.0, -0.185, "Brackets: Dunn's test vs control (Bonferroni-adjusted p)  ·  δ = Cliff's delta effect size  ·  "
        "% row: mean memory of mutants / mean memory of control of the same age [bootstrap 95% range]",
        transform=ax.transAxes, ha="left", va="top", fontsize=8.5, color=grey)


#####################################################
## saving everything


fig.savefig("Plot1_memory.png", dpi=300, bbox_inches="tight")    ## for the presentation
fig.savefig("Plot1_memory.pdf", bbox_inches="tight")             ## for the LaTeX report

with open("results_plot1.txt", "w", encoding="utf-8") as f:      ## all printed numbers in a text file
    f.write("\n".join(results_lines))

print("")
print("Saved: Plot1_memory.png, Plot1_memory.pdf, results_plot1.txt")
plt.show()                                                       ## show the plot (close the window to finish)