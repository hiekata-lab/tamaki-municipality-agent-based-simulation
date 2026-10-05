# tamaki-municipality-agent-based-simulation

## Table of contents
- [Simulation overview](#simulation-overview)
- [Figures](#figures)
- [Code overview](#code-overview)
- [Data sources](#data-sources)
  - [2021 Survey on Time Use and Leisure Activities](#2021-survey-on-time-use-and-leisure-activities)
    - [Questionnaire A](#questionnaire-a)
    - [Table Number 70-1-2](#table-number-70-1-2)
    - [Table Number 78-1-1](#table-number-78-1-1)
    - [Table Number 13](#table-number-13)
    - [Appendix Table A](#appendix-table-a)
  - [2020 Population Census](#2020-population-census)
    - [Table Number 2-5-1](#table-number-2-5-1)
  - [2022 National Survey on Living Conditions](#2022-national-survey-on-living-conditions)
    - [Table Number 30](#table-number-30)
  - [Tamaki Town Municipality Boundaries](#tamaki-town-municipality-boundaries)
    - [Boundary Shapefile](#boundary-shapefile)
- [Statistical Comparison of Mean Time Spent on Activities in Simulation and Survey data](#statistical-comparison-of-mean-time-spent-on-activities-in-simulation-and-survey-data)

## Simulation overview
The defined state attributes that were used were:
- **Reasoning**: A plain text attribute for the agent to perform Chain-of-Thought reasoning about its state before filling in the following attributes. Included as a compromise between using reasoning functionality and constrained sampling which are two features that are mutually exclusive in the LLM provider used in this study.
- **Memory**: A plain text attribute for the agent to write down things it deems important to remember for the next state. Included as a compromise between including a long state history (to counteract issues such as "lost in the middle" shown by Liu et al.) and keeping the simulation history-less.
- **Activity**: Different activities that the agent is allowed to choose from during the simulation. What activities are available to choose is based on the type of location the agent was in during the last state.
- **Location**: Different locations that the agent can visit during the simulation. The only way for the agent to change its location in the next state is by selecting a traveling activity in the current state.
- **Time**: A completely deterministic value that is updated each step by a time mapped to an activity in a fixed table.

There was also a set of accompanying prompt arguments included. These served as contextual information for the LLM's decision process, for example distance to other locations.

## Figures

![Tamaki Town Geo-Spatial Model](readme_figures/tamaki-municipality-geo-spatial-model.png)

*Red dot icons are locations registered by Google Maps, Blue house icons are randomly picked houses used as agent starting points, the red border is the municipality boundary, the inner multicolored shapes are municipality subdivisions.*

![Flowchart of the case study DCSP](readme_figures/case-study-flowchart.png)

*The flowchart figure visualizes how a sequence of visited states $S$ transitions into a new state $s_{i+1}$ utilizing both inferred LLM choices and deterministic functions.*

![Flowchart of the pre-implementation testing case study Scenarios](readme_figures/simulation-flowchart.png)

*The flowchart figure visualizes how the different scenarios are simulated, the data extracted, aggregated and presented as PIT for decision support. In the simulation code this process is done once for each LLM model.*

## Code overview
A data -> simulation -> results pipeline using the LSPS package. Setup of the pipeline is loosely based on a microservices architecture. Each script is highly modular and can be run independently.

## Data sources
Below is a full list of sources for all the data used in this simulation.

> **!NOTICE!**: Set API URL appId parameter manually (appId=your-app-id) to access, this requires you to sign up on the e-stat website, published by the Japanese government

### 2021 Survey on Time Use and Leisure Activities <a id="datasources:2021timeuse"></a>

#### Questionnaire A <a id="datasources:2021timeuse/qua"></a>
**Statistics name**: 2021 Survey on Time Use and Leisure Activities, **Document title**: Questionnaire A, **Document URL**: [URL](https://www.stat.go.jp/english/data/shakai/2021/pdf/qua.pdf), **Accessed**: Jul 15, 2026

#### Table Number 70-1-2 <a id="datasources:2021timeuse/70-1-2"></a>
**Statistics name**: Survey on Time Use and Leisure Activities 2021 Survey on Time Use and Leisure Activities Questionnaire A Results on Time Use, Time Use for Prefectures, **Table title**: Average time spent in activities for all persons by Kind of activities, Day of the week, Area classification, Sex, Usual economic activity, Usual state of health, Age (15 Years Old and Over)-Japan, Prefectures, **Table URL**: [URL](https://www.e-stat.go.jp/en/dbview?sid=0003457373), **Table API**: [URL](http://api.e-stat.go.jp/rest/3.0/app/getSimpleStatsData?cdCat01=1&cdCat03=0%2C1%2C2&cdCat05=0%2C6%2C7&cdArea=24000&appId=&lang=E&statsDataId=0003457373&metaGetFlg=Y&cntGetFlg=N&explanationGetFlg=Y&annotationGetFlg=Y&sectionHeaderFlg=1&replaceSpChars=0), **Accessed**: Jul 16, 2026

#### Table Number 78-1-1 <a id="datasources:2021timeuse/78-1-1"></a>
**Statistics name**: Survey on Time Use and Leisure Activities 2021 Survey on Time Use and Leisure Activities Questionnaire A Results on Time Use, Time Use for Prefectures, **Table title**: Average time spent in activities for all persons by Kind of activities, Day of the week, Area classification, Sex, Usual economic activity, Age (Heads of One-Person Household)-Japan, Prefectures, **Table URL**: [URL](https://www.e-stat.go.jp/index.php/en/dbview?sid=0003457588), **Table API**: [URL](http://api.e-stat.go.jp/rest/3.0/app/getSimpleStatsData?cdCat04=0%2C1%2C2%2C3%2C4%2C5%2C6%2C7&cdArea=24000&cdTab=202126A99B99&appId=&lang=E&statsDataId=0003457588&metaGetFlg=Y&cntGetFlg=N&explanationGetFlg=Y&annotationGetFlg=Y&sectionHeaderFlg=1&replaceSpChars=0), **Accessed**: Aug 17, 2026

#### Table Number 13 <a id="datasources:2021timeuse/13"></a><a id="datasource:standard-errors"></a>
**Statistics name**: Survey on Time Use and Leisure Activities 2021 Survey on Time Use and Leisure Activities Questionnaire A Results on Time Use, Time Use for Prefectures, **Table title**: Standard Error Ratios of Average time spent in activities for all persons by Sex, Kind of activities - Weekly average, Japan, Prefectures, **Table URL**: [URL](https://www.stat.go.jp/english/data/shakai/2021/zuhyou/2021gosaA013.xlsx), **Accessed**: Jul 15, 2026

#### Appendix Table A <a id="datasources:2021timeuse/appendix-a"></a>
**Statistics name**: Survey on Time Use and Leisure Activities 2021 Survey on Time Use and Leisure Activities Questionnaire A Results on Time Use, Time Use for Prefectures, **Table title**: Number of Sample EDs, Households and Persons by Prefectures (Questionnaire A), **Table URL**: [URL](https://www.stat.go.jp/data/shakai/2021/zuhyou/huhyoua.xlsx), **Accessed**: Jul 15, 2026

### 2020 Population Census <a id="datasources:2020popcensus"></a>

#### Table Number 2-5-1 <a id="datasources:2020popcensus/2-5-1"></a>
**Statistics name**: Population Census 2020 Population Census Basic Complete Tabulation on Population and Households, **Table title**: Population by Sex, Age (single years) and All nationality or Japanese - Japan, Prefectures, Municipalities (including Municipalities as of 2000), **Table URL**: [URL](https://www.e-stat.go.jp/en/dbview?sid=0003445139), **Table API**: [URL](https://api.e-stat.go.jp/rest/3.0/app/getStatsData?cdCat01=1&cdArea=24461&cdCat03=066%2C067%2C068%2C069%2C070%2C071%2C072%2C073%2C074%2C075%2C076%2C077%2C078%2C079%2C080%2C081%2C082%2C083%2C084%2C085%2C086%2C087%2C088%2C089%2C090%2C091%2C092%2C093%2C094%2C095%2C096%2C097%2C098%2C099%2C100%2C101&appId=&lang=E&statsDataId=0003445139&metaGetFlg=Y&cntGetFlg=N&explanationGetFlg=Y&annotationGetFlg=Y&sectionHeaderFlg=1&replaceSpChars=0), **Accessed**: Jul 16, 2026

### 2022 National Survey on Living Conditions <a id="datasources:2022livingcond"></a>

#### Table Number 30 <a id="datasources:2022livingcond/30"></a>
**Statistics name**: National Survey on Living Conditions, 2022 National Survey on Living Conditions: Health, **Table title**: Household size (15 years and older), health awareness, gender, age (5-year age groups), and education level, **Table URL**: [URL](https://www.e-stat.go.jp/dbview?sid=0002040972), **Table API**: [URL](https://api.e-stat.go.jp/rest/3.0/app/getStatsData?cdTab=2580&cdTime=15&cdCat02=370%2C400%2C410%2C440%2C450&cdCat04=110&cdCat01=110%2C120%2C130%2C140%2C150%2C160&appId=&lang=J&statsDataId=0002040972&metaGetFlg=Y&cntGetFlg=N&explanationGetFlg=Y&annotationGetFlg=Y&sectionHeaderFlg=1&replaceSpChars=0), **Accessed**: Jul 16, 2026

### Tamaki Town Municipality Boundaries <a id="datasources:tamaki2020estat"></a>

#### Boundary Shapefile <a id="datasources:tamaki2020estat/boundary"></a>
**Statistics name**: 2020 Population Census Boundary Data (e-Stat GIS), **Boundary title**: 24461 tama-ki-chō (Tamaki Town), **Download URL**: [URL](https://www.e-stat.go.jp/gis/statmap-search/data?dlserveyId=A002005212020&code=24461&coordSys=1&format=shape&downloadType=5&datum=2000), **Page URL**: [URL](https://www.e-stat.go.jp/gis/statmap-search?page=2&type=2&aggregateUnitForBoundary=A&toukeiCode=00200521&toukeiYear=2020&serveyId=A002005212020&prefCode=24&coordsys=1&format=shape&datum=2000), **Accessed**: Jul 15, 2026

## Statistical Comparison of Mean Time Spent on Activities in Simulation and Survey data
An independent two-sample comparison using **Welch's $t$-test** is conducted to evaluate differences between the simulated agents' mean weekly time spent on each activity and the mean weekly time spent on each activity by the citizens who participated in the 2021 Survey on Time Use and Leisure Activities (Questionnaire A). Because the simulation and survey cohorts have unequal sample sizes ($N_{\text{sim}} = 100$ vs. $N_{\text{val}} = 218$) and unequal variances, equal variance is not assumed:

1. **Sample Sizes ($N$)**:
   - **Simulation ($N_{\text{sim}} = 100$)**: Sample of $N = 100$ simulated autonomous elderly agents (aged 65+) under Scenario 2.
   - **Survey Subgroup ($N_{\text{val}} = 218$)**: Effective sample size of elderly, non-working citizens in Mie Prefecture derived from Table 78-1-1 (*Heads of One-Person Household, Mie Prefecture, Not working, 65+*).
   - **Survey Total Sample ($N_{\text{total}} = 3{,}372$)**: Total sampled respondents in Mie Prefecture across all ages (15+) and employment statuses from Questionnaire A (`Sample_Persons_Average_Time` in `data/processed/Questionnaire A.csv`).

2. **Activity Means ($\bar{x}$) and Alignment**:
   - **Simulation Mean ($\bar{x}_{\text{sim}}$)**: Evaluated over each agent's first 24-hour cycle ($1{,}440\text{ minutes}$) starting from initial deployment ($T_0 = \text{2026-06-10 08:00:00}$ to $T_1 = \text{2026-06-11 08:00:00}$). Restricting the analysis window to exactly 24 hours (1 daytime cycle and 1 nighttime sleep cycle) ensures consistent daily proportions and avoids sleep deflation from multi-day partial spans. All transportation modes (`Walking`, `Riding bus`, `Driving car`, `Riding taxi`, `Riding mobility-on-demand shuttle`, `Riding bike`) are consolidated into a unified `Moving` category.
   - **Survey Mean ($\bar{x}_{\text{val}}$)**: Population mean from Table 70-1-2 (*Average time spent in activities for all persons by Kind of activities, Day of the week, Area classification, Sex, Usual economic activity, Usual state of health, Age (15 Years Old and Over) - Japan, Prefectures*) filtered to Mie Prefecture (`24000`), weekly average (`1_Weekly average`), both sexes (`0_Both sexes`), not working (`2_Not working`), total health (`0_Total`), and elderly cohorts (`65 to 74 years old` and `75 years old and over`).
   - **Activity Set Alignment**: Comparison is restricted via an inner join to mutual activities, mapping survey `Moving (excluding commuting)` to `Moving` and dropping non-simulated categories (`Work`, `Schoolwork`, `Commuting to and from school or work`).

3. **Standard Errors ($SE$)**:
   - **Simulation ($SE_{\text{sim}}$)**: Computed directly from agent-level sample standard deviations ($s_{\text{sim}}$) across the $N_{\text{sim}} = 100$ agents:
     $$SE_{\text{sim}} = \frac{s_{\text{sim}}}{\sqrt{N_{\text{sim}}}}$$
   - **Survey ($SE_{\text{val}}$)**: Computed using the official Standard Error Ratio ($r$) from Table 13 (*Standard Error Ratios of Average time spent in activities for all persons by Sex, Kind of activities - Weekly average, Japan, Prefectures*) for Mie Prefecture. Because Table 13 computes $r$ across the entire prefectural sample ($N_{\text{total}} = 3{,}372$), the ratio is scaled to the elderly non-working subgroup ($N_{\text{val}} = 218$) using the square root ratio of the sample sizes ($SE \propto \frac{1}{\sqrt{N}}$):
     $$SE_{\text{val}} = r \times \bar{x}_{\text{val}} \times \sqrt{\frac{N_{\text{total}}}{N_{\text{val}}}} = r \times \bar{x}_{\text{val}} \times \sqrt{\frac{3372}{218}} \approx 3.9329 \times (r \times \bar{x}_{\text{val}})$$
   - **Combined Standard Error**:
     $$SE_{\text{combined}} = \sqrt{SE_{\text{sim}}^2 + SE_{\text{val}}^2}$$

4. **Degrees of Freedom**:
   Effective degrees of freedom ($\nu_{\text{Welch}}$) for the mean difference are estimated using the Welch–Satterthwaite equation:
   $$\nu_{\text{Welch}} = \frac{\left(SE_{\text{sim}}^2 + SE_{\text{val}}^2\right)^2}{\frac{SE_{\text{sim}}^4}{N_{\text{sim}} - 1} + \frac{SE_{\text{val}}^4}{N_{\text{val}} - 1}}$$

5. **Confidence Intervals**:
   Confidence intervals at the 90% and 95% levels are computed using Student's $t$-distribution:
   - **Simulation**:
     $$CI_{\text{sim}} = \bar{x}_{\text{sim}} \pm t_{1 - \alpha/2, \, N_{\text{sim}} - 1} \times SE_{\text{sim}}$$
   - **Survey**:
     $$CI_{\text{val}} = \bar{x}_{\text{val}} \pm t_{1 - \alpha/2, \, N_{\text{val}} - 1} \times SE_{\text{val}}$$

6. **Test Statistics and $p$-Values**:
   To test the null hypothesis of equal mean activity durations ($H_0: \mu_{\text{sim}} - \mu_{\text{val}} = 0$) against the two-sided alternative ($H_1: \mu_{\text{sim}} - \mu_{\text{val}} \neq 0$), Welch's $t$-statistic is calculated as:
   $$t = \frac{\bar{x}_{\text{sim}} - \bar{x}_{\text{val}}}{SE_{\text{combined}}} = \frac{\bar{x}_{\text{sim}} - \bar{x}_{\text{val}}}{\sqrt{SE_{\text{sim}}^2 + SE_{\text{val}}^2}}$$
   The two-tailed $p$-value is evaluated under Student's $t$-distribution with $\nu_{\text{Welch}}$ degrees of freedom:
   $$p = 2 \times \left(1 - F_t\left(|t|; \, \nu_{\text{Welch}}\right)\right) = 2 \times P\left(T \ge |t|\right)$$
   where $F_t(\cdot; \, \nu_{\text{Welch}})$ denotes the cumulative distribution function (CDF) of Student's $t$-distribution with $\nu_{\text{Welch}}$ degrees of freedom.

   - **MiniMax-M2.5 (Scenario 2)**:

     | Activity | $\bar{x}_{\text{sim}}$ (min) | $\bar{x}_{\text{val}}$ (min) | $SE_{\text{combined}}$ | $\nu_{\text{Welch}}$ | Welch's $t$ | $p$-value |
     | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
     | Caring or nursing | 0.00 | 6.50 | 4.49 | 217.0 | -1.446 | 0.1495 |
     | Child care | 0.00 | 3.00 | 0.71 | 217.0 | -4.231 | 3.44e-05 |
     | Hobbies and amusements | 12.69 | 49.00 | 8.44 | 234.6 | -4.303 | 2.48e-05 |
     | Housework | 27.97 | 144.50 | 21.17 | 220.5 | -5.504 | 1.02e-07 |
     | Learning, self-education, and training (excluding schoolwork) | 2.60 | 9.50 | 2.25 | 312.6 | -3.062 | 0.0024 |
     | Meals | 119.49 | 119.00 | 4.72 | 301.3 | 0.104 | 0.9173 |
     | Medical examination or treatment | 0.20 | 14.50 | 6.70 | 217.4 | -2.135 | 0.0339 |
     | Moving | 15.14 | 19.00 | 2.34 | 309.8 | -1.648 | 0.1005 |
     | Other activities | 0.40 | 30.50 | 10.62 | 217.6 | -2.833 | 0.0050 |
     | Personal care | 160.39 | 94.00 | 8.83 | 294.8 | 7.523 | 6.53e-13 |
     | Rest and relaxation | 313.19 | 108.00 | 11.72 | 167.5 | 17.503 | 1.15e-39 |
     | Shopping | 4.67 | 32.50 | 3.66 | 250.4 | -7.612 | 5.52e-13 |
     | Sleep | 429.00 | 500.50 | 9.99 | 197.2 | -7.158 | 1.58e-11 |
     | Social life | 9.98 | 12.00 | 5.09 | 306.0 | -0.397 | 0.6919 |
     | Sports | 0.20 | 21.50 | 4.60 | 217.8 | -4.635 | 6.16e-06 |
     | Volunteer and social activities | 0.00 | 4.00 | 1.31 | 217.0 | -3.045 | 0.0026 |
     | Watching TV, listening to the radio, reading newspapers or magazines | 335.83 | 267.00 | 12.89 | 204.5 | 5.341 | 2.45e-07 |

   - **GLM-5 (Scenario 2)**:

     | Activity | $\bar{x}_{\text{sim}}$ (min) | $\bar{x}_{\text{val}}$ (min) | $SE_{\text{combined}}$ | $\nu_{\text{Welch}}$ | Welch's $t$ | $p$-value |
     | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
     | Caring or nursing | 0.00 | 6.50 | 4.49 | 217.0 | -1.446 | 0.1495 |
     | Child care | 0.00 | 3.00 | 0.71 | 217.0 | -4.231 | 3.44e-05 |
     | Hobbies and amusements | 63.40 | 49.00 | 8.77 | 265.3 | 1.643 | 0.1016 |
     | Housework | 15.60 | 144.50 | 21.11 | 218.1 | -6.106 | 4.63e-09 |
     | Learning, self-education, and training (excluding schoolwork) | 0.20 | 9.50 | 1.94 | 221.6 | -4.789 | 3.07e-06 |
     | Meals | 63.20 | 119.00 | 3.68 | 234.6 | -15.170 | 1.10e-36 |
     | Medical examination or treatment | 0.00 | 14.50 | 6.70 | 217.0 | -2.166 | 0.0314 |
     | Moving | 0.20 | 19.00 | 2.04 | 219.1 | -9.227 | 2.42e-17 |
     | Other activities | 0.00 | 30.50 | 10.62 | 217.0 | -2.873 | 0.0045 |
     | Personal care | 22.40 | 94.00 | 6.66 | 222.8 | -10.748 | 5.61e-22 |
     | Rest and relaxation | 298.80 | 108.00 | 7.23 | 314.8 | 26.408 | 7.86e-82 |
     | Shopping | 0.00 | 32.50 | 3.52 | 217.0 | -9.246 | 2.25e-17 |
     | Sleep | 653.92 | 500.50 | 7.04 | 314.7 | 21.787 | 8.26e-65 |
     | Social life | 0.00 | 12.00 | 3.95 | 217.0 | -3.034 | 0.0027 |
     | Sports | 0.00 | 21.50 | 4.59 | 217.0 | -4.683 | 4.99e-06 |
     | Volunteer and social activities | 0.00 | 4.00 | 1.31 | 217.0 | -3.045 | 0.0026 |
     | Watching TV, listening to the radio, reading newspapers or magazines | 322.20 | 267.00 | 9.02 | 315.6 | 6.121 | 2.75e-09 |
