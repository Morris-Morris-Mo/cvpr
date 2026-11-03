# GeoRank: Geometry-Disagreement-Aware Ranking for Late Supplementation in Aerial–Ground Cooperative Perception

## Abstract

Aerial–ground cooperative perception improves scene understanding through information exchange across agents, yet intermediate-fusion detection outputs can still omit useful candidates and rank their quality inadequately. We propose GeoRank, which uses geometry-disagreement-aware ranking to strengthen late supplementation of cooperative outputs with independent vehicle predictions. GeoRank associates two sets of candidates at the receiver and incorporates center disagreement, matching cost, confidence relationships, and source status into final scoring. It supports both explicit disagreement penalties and lightweight learned rescoring, without retraining the underlying detection networks for ranking. The independent vehicle branch uses local observations, while supplementation and ranking reuse the same remote inputs, introducing no additional remote message payload relative to the cooperative baseline. On the complete Griffin-55m validation set, the explicit multiplicative variant achieves **39.87 vehicle AP and 44.68 vehicle AMOTA**, numerically exceeding all intermediate-fusion methods reported in Table 3 of the Griffin benchmark and surpassing the strongest reported method, CoopTrack, by **3.47 and 4.48 percentage points**, respectively. With identical branch inputs, linear and multiplicative disagreement scoring improve the base fusion AP from 39.26 to **39.86 and 39.87**. With candidates and box geometry further fixed, adding center disagreement alone increases AP on a five-scene holdout within the validation set from 38.70 to **39.49 (+0.79)**. Learned GeoRank reaches **40.12 (+1.42)** and improves AP by **2.38 points** at the strict 0.5 m matching tolerance. Module ablations, eight feature configurations, and scene-level analyses support the ranking value of geometric disagreement. Explicit penalties slightly reduce AMOTA relative to base fusion, indicating that detection ranking and tracking operating points still require coordination. These results show that receiver-side candidate relationship modeling can improve late supplementation in 55 m aerial–ground cooperative perception while preserving the upstream message payload.

**Keywords:** aerial–ground cooperative perception; 3D object detection; late fusion; geometric disagreement; candidate rescoring.

## 1. Introduction

Cooperative perception combines observations from multiple agents to mitigate occlusion and limited fields of view in vehicle-mounted sensors, making it an important direction for autonomous-driving perception. Depending on the exchanged information, existing methods are commonly categorized as early, intermediate, or late fusion. Early fusion transmits raw observations and preserves rich information at a high communication cost. Late fusion exchanges detection results through a compact interface but cannot readily recover information lost before detection. Intermediate fusion exchanges deep features or instance queries, providing a flexible trade-off between representation and communication cost and attracting extensive research [2–6]. Within this paradigm, how to further exploit predictions already available at the receiver remains an important question.

We focus on late supplementation after intermediate fusion: jointly processing independent vehicle predictions and detection outputs that have already undergone cooperation. Independent outputs contribute useful single-branch candidates but also introduce duplicate predictions, localization conflicts, and score differences across sources. Confidence thresholds control output counts, and source discounts adjust branch weights, but neither fully describes agreement in position, size, and orientation. Improving late supplementation therefore requires more than retaining additional boxes: relationships among candidates should help assign more appropriate ranks to reliable predictions.

This problem is practically relevant to Griffin's 55 m aerial–ground setting. Griffin reports performance degradation as UAV altitude increases [2]. In its Table 3, several intermediate-fusion methods provide limited gains over the vehicle-only baseline at 55 m, and some even degrade performance. This makes 55 m a concrete setting for examining output supplementation. We use the publicly reported intermediate-fusion methods in that table as the principal performance references, study receiver-side candidate processing at a fixed altitude of 55 m, and separately report raw-data early fusion as a high-communication-cost reference.

Object-level analysis distinguishes candidate availability from appropriate scoring. At a score threshold of 0.20 and a same-class center-distance threshold below 2 m, 263 of 594 GT observations detected only by the vehicle branch already have low-scoring cooperative candidates within 2 m. Among paired candidates whose parents both match the same GT, the higher-scoring parent has a smaller center error in only 46.79% of cases. These observations suggest that raw confidence does not adequately represent localization quality and motivate geometric disagreement as additional scoring information. Counts are accumulated over frames and do not represent distinct physical vehicles.

We therefore propose **GeoRank** (Geometry-Disagreement-Aware Ranking), whose core idea is to explicitly use geometric disagreement when scoring candidate quality. The method has two implementations. An explicit disagreement penalty directly adjusts scores using the distance between parent-box centers. Learned GeoRank jointly maps center disagreement, matching cost, score relationships, and source status to a detection score. The former provides an isolatable geometric intervention, whereas the latter learns joint weights for multiple relationships. Both share the same candidate association and retention front end, extending geometric relationships used for pairing to final ranking.

This receiver-side design also has a direct communication advantage. The independent vehicle branch uses local observations, and all GeoRank geometry and score features come from predictions already available at the receiver. No additional remote features or detection messages are required. A payload audit over the complete 55 m validation cache confirms that the base supplementation pipeline uses the same remote messages as the cooperative baseline. Subsequent explicit and learned scoring reuse the same local predictions. Performance improvements thus incur receiver-side computation without increasing the remote message payload.

Experiments first establish the method's position relative to published results and then analyze the source of its gains. On the complete 55 m validation set, the explicit multiplicative variant achieves **39.87 AP / 44.68 AMOTA**, numerically exceeding all intermediate-fusion methods in Griffin Table 3. Compared with the strongest reported result, CoopTrack (36.40 / 40.20), the gains are **3.47 / 4.48 points**. Differences between published methods and local configurations are stated in the experiments, while module effects are established using identical inputs. AP is 39.26, **39.86**, and **39.87** for the base reference, linear penalty, and multiplicative penalty, respectively. On a five-scene holdout within validation, fixed-candidate base scoring, explicit penalization, and learned GeoRank achieve 38.70, **39.49**, and **40.12 AP**. These controls connect system-level improvements to the independent effect of disagreement-aware scoring.

Our main contributions are:

1. **Geometry-disagreement-aware late supplementation.** GeoRank extends geometric relationships between independent vehicle and final cooperative predictions from candidate association to quality scoring, using explicit penalties and learned rescoring to exploit geometry, confidence, and source information.
2. **55 m vehicle performance above the published intermediate-fusion baselines.** The explicit multiplicative variant achieves **39.87 AP / 44.68 AMOTA**, numerically exceeding the intermediate-fusion methods in Griffin Table 3. Local fixed-input controls further validate the effect of output enhancement.
3. **Evidence for the role of geometry with fixed candidates.** Center disagreement alone improves internal-holdout AP by **0.79 points**, and learned GeoRank improves it by **1.42 points**. Eight feature ablations, scene-level results, and a reversed split examine the sources of improvement and the detection–tracking trade-off.
4. **Receiver-side enhancement without additional remote payload.** Independent vehicle supplementation and GeoRank reuse upstream cooperative messages. An audit over all 1,490 frames and the scoring input protocols confirm zero additional remote messages and tensor payload, while local computational costs are discussed separately.

## 2. Related Work

### 2.1 Cooperative Perception and Intermediate–Late Hybrid Fusion

Griffin [2] establishes a dataset and benchmark for aerial–ground cooperative detection and tracking, comparing early fusion, BEV-level and instance-level intermediate fusion, and late fusion. UniV2X [3] and CoopTrack [6] organize cross-agent information for end-to-end cooperative driving and sequential perception, respectively. SparseCoop [4] and Long-SCOPE [5] investigate sparse queries, geometric association, and long-range information aggregation. These methods advance representations and interactions inside cooperative networks. We use existing cooperative outputs and study the subsequent supplementation stage with independent detections.

CoSDH [1] explores intermediate–late hybrid cooperation. Our focus is how geometric disagreement between independent vehicle predictions and final cooperative predictions should contribute to candidate quality scoring. We examine this mechanism on Griffin-55m through published performance comparisons and fixed-candidate experiments.

### 2.2 Detection Fusion and Candidate Rescoring

WBF [7] clusters candidates and fuses box geometry using confidence weights. ProbEn [8] studies probabilistic ensembling of multisource detections and discusses combining independent branches with already fused outputs. CLOCs [9] learns to rescore candidates using geometric consistency and scores from camera and LiDAR detections, demonstrating that candidate relationships can inform quality assessment. MS3D [10] combines multiple 3D detectors and temporal information to construct more reliable pseudo-labels.

GeoRank uses two sets of 3D predictions: independent vehicle outputs and cooperative outputs that already incorporate vehicle information. Because the branches share input information, they cannot simply be treated as statistically independent evidence. We use their geometric disagreement as an observable descriptor and combine it with raw scores to learn final ranking. We do not interpret the resulting scores as empirically validated calibrated probabilities or assume that geometric agreement necessarily implies correctness.

### 2.3 Multi-Branch Candidate Relationships and Detection-Based Tracking

ETS [11] organizes consistent, conflicting, and one-sided pseudo-labels according to matching relationships for domain-adaptive object detection and performs box fusion. UMS [12] maintains both single-agent and multi-agent predictions in unsupervised cooperative perception, using candidate complementarity to improve training supervision. Our method processes final detection outputs at deployment; GT is used only to generate labels for ranker fitting and for offline evaluation.

Detection-based 3D tracking typically organizes detections through state prediction, data association, and track management [13]. We use a common basic motion tracker to examine how output processing affects tracking performance; the tracker itself is not a new algorithmic contribution. Detection scores affect ranking and may also influence association and track birth, so AP and AMOTA changes must be evaluated separately.

## 3. GeoRank

### 3.1 Problem Definition and Overview

Given vehicle observations $I^v$ and UAV observations $I^a$, independent vehicle and cooperative predictions are denoted by

$$
\mathcal B^v=f_v(I^v),\qquad \mathcal B^c=f_c(I^v,I^a).
$$

For simplicity, we omit any historical temporal state used by the underlying networks. Final candidates from both branches are transformed into a common global coordinate system. Each candidate contains a class, center, size, rotation, velocity, and confidence:

$$
b=(k,\mathbf x,\mathbf s,\mathbf q,\mathbf v,p).
$$

We establish candidate relationships at the output level, construct a base fusion result $\mathcal D_0$, and estimate detection scores from relationship features $\phi$:

$$
\mathcal D_0=\mathcal F_0(\mathcal B^v,\mathcal B^c),\qquad s^{\mathrm{det}}=\mathcal R_\theta(\phi(b)).
$$

$\mathcal F_0$ comprises geometric pairing, matched-candidate fusion, single-branch retention, and deduplication. $\mathcal R_\theta$ is GeoRank's disagreement-aware rescorer. In the current learned experiments, the candidate set and all non-score fields of $\mathcal D_0$ are fixed, and only vehicle detection scores change, directly testing the effect of ranking.

### 3.2 Shared Candidate Front End

For same-class candidates $b_v$ and $b_c$, define the planar center distance

$$
d_{vc}=\|\mathbf x^v_{xy}-\mathbf x^c_{xy}\|_2.
$$

The front end uses a pairing cost $C_{vc}$ incorporating center, size, and orientation relationships. Hungarian assignment produces a matched set $\mathcal M$, a vehicle-only set $\mathcal U^v$, and a cooperative-only set $\mathcal U^c$. Matched boxes use confidence-weighted geometry, while single-branch boxes retain their original geometry. The base score $s_0$ applies a matching bonus and single-branch scaling; deduplication then yields $\mathcal D_0$. This front end supplies common candidates, parent relationships, and reference scores for rescoring experiments. Complete association and fusion formulas are provided in Appendix A.1. We focus below on the added disagreement-aware scoring.

### 3.3 Geometry-Disagreement-Aware Rescoring

The base score distinguishes matched from unmatched candidates, but geometric disagreement after successful matching does not directly enter scoring. We construct three groups of candidate descriptors.

**Confidence relationships.** Features include the base-score logit, both raw branch scores, their minimum and maximum, their absolute difference, and score balance:

$$
a_{vc}=\frac{2\min(p_v,p_c)}{p_v+p_c+\epsilon}.
$$

These features describe the strength of support from both branches, avoiding decisions based solely on the maximum score.

**Geometric disagreement.** Features include parent-center distance $d_{vc}$, matching cost $C_{vc}$, and normalized center distance

$$
\bar d_{vc}=\frac{d_{vc}}{\max(0.8,\hat\ell)},
$$

where $\hat\ell$ is the fused candidate length. Center distance describes positional disagreement, while matching cost also captures size and orientation differences. Normalization represents relative disagreement across object scales.

**Candidate source.** Three indicators encode matched, vehicle-only, and cooperative-only status. For single-branch candidates, the missing source score and geometric pairing quantities are set to zero, while source indicators are retained. A zero geometric value for a single-branch candidate is therefore not interpreted in isolation as perfect agreement between two branches.

The complete feature vector has 13 dimensions. Means and standard deviations are estimated from the fitting scenes, and L2-regularized logistic regression produces the score:

$$
\tilde\phi=\frac{\phi-\boldsymbol\mu}{\boldsymbol\sigma},\qquad
s^{\mathrm{det}}=\operatorname{sigmoid}(\mathbf w^\top\tilde\phi+b).
$$

The implementation has 13 linear weights and one bias, without an additional detection backbone. The coefficient of the base logit is also learned. We therefore describe the method as rescoring, rather than a fixed residual formulation or a ranking loss that directly optimizes AP.

### 3.4 Learning Supervision and Explicit Disagreement Penalties

Training labels are generated on the fitting scenes. For vehicle candidates and vehicle GT in each frame, we enumerate pairs within 2 m, sort them by center distance, and perform one-to-one assignment. Assigned candidates are positive; the rest are negative. This procedure does not use candidate confidence, reducing the direct replication of the original ranking in supervision. Training uses a class-balanced binary classification loss with L2 regularization, $C=0.1$, and random seed 0. GT supplies supervision labels, while inference features come exclusively from predictions.

The same disagreement-aware scoring idea can be implemented directly as an explicit penalty without fitting:

$$
s_\lambda=\begin{cases}
\operatorname{clip}(s_0-\lambda d_{vc},0,0.999), & b\in\mathcal M,\\
s_0, & b\notin\mathcal M.
\end{cases}
$$

We also consider the multiplicative form $s_0\exp(-\lambda d_{vc})$, applied only to matched candidates. Applying an explicit rule to fixed final candidates isolates the independent ranking contribution of disagreement. Applying it after base scoring but before deduplication and truncation tests its interaction with the complete candidate-processing and tracking pipeline. Learned GeoRank fits joint weights for several relationships. Its current logistic-regression implementation does not constrain distance coefficients to be negative, so it is not expressed as the same scoring formula as a fixed linear penalty.

### 3.5 Detection Ranking and the Tracking Interface

AP evaluates detections across confidence operating points, whereas the basic tracker also uses absolute score thresholds for association, track birth, and state updates. Improved detection ranking therefore does not automatically imply improved tracking.

The learned ranking-only experiments separate detection scoring from base trajectory outputs: detection candidates use $s^{\mathrm{det}}$, while tracking retains trajectories generated using the original candidates and scores. This isolates ranking effects and does not support claims of new tracking gains. The complete pipeline with explicit distance penalties reruns the basic tracker to observe the practical trade-off induced by shared scores.

The module accepts standard 3D boxes and scores and could potentially be adapted to other systems at the output level. Current evidence comes from the UniV2X framework. Deployments that do not already retain independent vehicle predictions must also account for generating that branch. The rescorer's small parameter count is not evidence of end-to-end real-time performance.

In the current receiver-side implementation, the independent vehicle branch uses only local information, while candidate supplementation and rescoring reuse the same remote inputs. Neither the number of remote messages nor their input tensor payload increases relative to the cooperative baseline. The complete-validation cache audit supports this relative-overhead conclusion; it is not a wireless-throughput measurement and does not remove the computational costs of the local branch and postprocessing.

## 4. Experiments

### 4.1 Data, Metrics, and Protocols

**Data.** We focus on Griffin-55m, built with CARLA and AirSim. Its training split contains 40 scenes and 5,960 frames, and the official validation split contains 10 scenes and 1,490 frames. The 55 m setting denotes UAV capture altitude; the official object evaluation range is 50 m horizontally from the receiver. These quantities have different meanings. Vehicles are the main focus, with bicycle, pedestrian, and three-class macro-average results also retained.

**Metrics.** Vehicle AP averages official center-distance AP at 0.5, 1, 2, and 4 m. AMOTA uses the project's official tracking evaluation. All tabulated metrics are multiplied by 100, and differences are in percentage points. Values such as 0.5 m denote prediction-to-GT matching tolerances, not object-to-sensor distance bins.

**Predictions and tracking.** The base complete pipeline uses independent vehicle predictions and ungated Control cooperative predictions. Control is initialized from official 55 m cooperative weights and incorporates motion-velocity coordinate handling and receiver-side fine-tuning. The independent vehicle branch retains official weights. Controls use the same branch caches and basic motion tracker. Model and tracking parameters are given in Appendix A.

**Experimental identities.** The current evidence comprises three settings:

| Setting | Data scope | Purpose | Scores and trajectories |
|---|---|---|---|
| A: complete 55 m pipeline | 10 official validation scenes, 1,490 frames | Compare individual branches, direct merging, base fusion, and explicit rules | Evaluate conditions separately; disagreement rules rerun deduplication, truncation, and tracking |
| B: ranking development within validation | Five fitting and five held-out validation scenes, 745 frames each | Test learned rescoring and feature changes with fixed candidates | Fix candidates and geometry; change detection scores only |
| C: train8 offline pilot | Eight training scenes, 1,192 frames; 6/2 split | Examine small-sample fitting and held-out ranking gains | Offline evaluation without rerunning deduplication or tracking |

The validation set has already participated in method development, so A and B are development-validation results. In B, held-out scenes are excluded only from the current ranker fit. Scenes in C belong to the underlying detector's training split, and consistency of the offline evaluator with the official evaluator has not yet been verified. We interpret these settings separately rather than combine them into an independent-test conclusion.

### 4.2 Published 55 m Performance and Controlled GeoRank Gains

Table 1(a) compares GeoRank's 55 m vehicle detection and tracking performance primarily with intermediate-fusion methods reported in the Griffin paper. Vehicle-only and late fusion provide benchmark references, while raw-data early fusion is a separate high-communication-cost reference. Local-version comparisons distinguish base candidate fusion from additional geometric scoring within the same evaluation scope. Historical versions changed upstream training or tracking settings; their scores document the research history, while module effects are determined through fixed-input experiments.

**Table 1(a). Comparison with the 55 m results in Griffin Table 3. Published intermediate-fusion methods are the principal comparison group; Early Fusion is a high-communication-cost reference. Published metrics are multiplied by 100. Local rows cover all 1,490 validation frames and use two decimal places. The learned row is a full-validation development reference that includes fitting scenes and reuses base trajectories.**

| Method | Vehicle AP | Vehicle AMOTA |
|---|---:|---:|
| No Fusion | 33.50 | 35.90 |
| Early Fusion | 48.30 | 52.20 |
| V2X-ViT | 35.00 | 37.90 |
| Where2Comm | 31.70 | 35.30 |
| CoopTrack | 36.40 | 40.20 |
| UniV2X | 32.30 | 34.90 |
| Late Fusion | 30.60 | 33.20 |
| GeoRank: explicit linear disagreement | **39.86** | **44.61** |
| GeoRank: explicit multiplicative disagreement | **39.87** | **44.68** |
| Base fusion + learned GeoRank (development; reused tracks) | **40.50** | **45.02** |

**Vehicle performance above published intermediate-fusion methods.** The explicit linear and multiplicative variants achieve **39.86 / 39.87 AP** and **44.61 / 44.68 AMOTA**, respectively. Both metrics exceed the V2X-ViT, Where2Comm, CoopTrack, and UniV2X results in Griffin Table 3. Relative to the strongest reported method, CoopTrack, the linear variant improves **3.46 AP / 4.41 AMOTA**, and the multiplicative variant improves **3.47 AP / 4.48 AMOTA**. These results demonstrate the practical value of receiver-side geometric relationship scoring for late supplementation. With identical inputs, the additional AP over the base reference is **0.59 / 0.61 points**.

Historical V1 and V2+ use earlier output-box fusion and complete causal tracking. The V2 bare network and V3–V7 are cooperative-network outputs rather than scoring ablations under a common front end. Raw Control-network outputs also differ from Control after common postprocessing. These historical identities are retained: version numbers do not denote cumulative additions to one method. V2+ repeat inference, historical module breakdowns, both 25 m settings, and complete parameter and formula scans are recorded in the accompanying local score archive.

The two learned full-validation development results fit on five validation scenes and report detections over all ten. They reuse base-fusion trajectories; consequently, 45.0180 / 17.4278 AMOTA does not represent tracking gains from the new ranker. Tracking cells for internal-validation and train8 holdouts are left unreported where tracking was not rerun. The **40.2391 AP** from complete features with 1 m labels is a label-sensitivity result; the default remains **40.1176 AP** with 2 m labels.

The train8 experiment uses eight scenes, six for fitting; its 93.3845 AP comes from the other two scenes. Its offline evaluation still requires alignment with the official protocol, and the underlying detector may already have seen these training scenes. No statistical evidence currently establishes that it represents the entire dataset. Absolute AP is not directly compared across groups, and its +2.2603 gain is not added to full-validation base AP.

**Further gains from scoring.** The complete explicit-disagreement pipeline improves base AP of 39.2635 by **0.5933 / 0.6111**. Default learned GeoRank reaches **40.1176 (+1.4184)** on the internal holdout; the label-sensitivity configuration reaches **40.2391 (+1.5399)**. The full-validation development reference is **40.5008 (+1.2374)**, and the train8 offline holdout is **93.3845 (+2.2603)**. Each exceeds its own same-scope base ranking. These results respectively concern the complete pipeline, held-out ranking, development evaluation, and small-sample exploration; absolute AP is not compared across groups.

**Class-dependent gains.** Base fusion has slightly lower three-class mAP than the independent vehicle branch, primarily alongside a bicycle AP decrease from 12.5840 to 6.3912; pedestrian AP remains zero. Our principal performance conclusions concern vehicles and do not imply consistent improvement for all road users.

### 4.3 Complete-Pipeline Effects of Geometric Disagreement

To test direct incorporation of matched geometric disagreement into scoring, we add a center-distance penalty after base scoring and rerun deduplication, truncation, tracking, and official evaluation. The coefficient $\lambda=0.04$ is selected on the five development scenes in the fixed-candidate experiment; smaller coefficients provide supplementary comparisons.

**Table 2. Complete-pipeline results for explicit geometric disagreement. All conditions use the same 55 m validation set. AMOTA is computed from trajectories actually generated under each condition.**

| Scoring rule | Vehicle AP | Vehicle AMOTA | Three-class mAP | Three-class AMOTA |
|---|---:|---:|---:|---:|
| Base score, $\lambda=0$ | 39.2635 | 45.0180 | 15.2182 | 17.4278 |
| Linear, $\lambda=0.01$ | **39.6649** | 44.9390 | **15.3461** | 17.4015 |
| Linear, $\lambda=0.02$ | **39.7957** | 44.7492 | **15.3867** | 17.3382 |
| Linear, $\lambda=0.04$ | **39.8568** | 44.6052 | **15.3967** | 17.2492 |
| Multiplicative, $s_0\exp(-0.04d_{vc})$, matched only | **39.8746** | 44.6770 | **15.4067** | 17.2731 |

The linear penalty improves vehicle AP by **0.5933 points**, and the multiplicative form by **0.6111 points**. Both indicate that incorporating post-match center disagreement into scoring further improves existing fusion outputs. Section 4.5 presents corresponding fixed-candidate interventions to distinguish scoring effects from changes in candidate retention.

The companion experiment with fixed final candidates improves full-validation AP from 39.2635 to **39.8553 (+0.5918)**, close to the complete-pipeline gain. Because candidates and box geometry remain unchanged, most of the detection improvement can be obtained through scoring alone.

Meanwhile, the linear penalty lowers vehicle AMOTA by approximately 0.41 points. Directly using detection-ranking scores at the existing tracking operating points can therefore have a different effect. Joint AP and AMOTA gains from complete fusion over a single branch and AP-only gains from added disagreement penalties are conclusions at different levels. We retain this trade-off and separately analyze detection rescoring and reused trajectories in the learned experiments.

### 4.4 GeoRank Ranking and Feature Ablations

In setting B, the ranker is trained on 18,845 vehicle candidates from five fitting scenes, including 3,616 positives. Another five scenes provide 22,025 vehicle candidates for held-out evaluation. All conditions fix the candidate set, geometric parameters, and non-score fields.

**Table 3. All eight learned feature ablations. Conditions share 2 m labels, the 5/5 validation-scene split, and fixed candidates and geometry.**

| Rescoring configuration | Fitting AP | Held-out AP | Held-out gain |
|---|---:|---:|---:|
| Base ranking | 39.9648 | 38.6992 | — |
| Score relationships and matched indicator | 40.2934 | 39.5248 | +0.8256 |
| Base logit, matched indicator, center distance | 40.4329 | **39.8112** | **+1.1120** |
| Base logit, matched indicator, distance, matching cost | 40.4369 | **39.8064** | **+1.1071** |
| Geometric support: base, matched, minimum score, score gap, balance, distance, cost, single-branch source | 40.5862 | **39.7677** | **+1.0685** |
| Geometric support without matching cost | 40.5771 | **39.7720** | **+1.0728** |
| Symmetric geometry: geometric support plus maximum parent score | 40.5733 | **39.7778** | **+1.0786** |
| Complete features without normalized distance | 40.7168 | **40.0876** | **+1.3883** |
| Complete GeoRank features | **40.9449** | **40.1176** | **+1.4184** |

All eight learned configurations outperform base ranking, with complete GeoRank achieving the highest **40.1176 AP (+1.4184)**. The three-feature model using only the base logit, matched indicator, and center distance already gains **1.1120 points**. Removing normalized distance from complete features still yields **40.0876 (+1.3883)**. Thus, the gains do not depend on high-dimensional features or a particular normalization trick. Adding matching cost to the small model gives no further improvement; the complete model's advantage should be understood through joint confidence, geometry, and source modeling.

Complete features improve by another **0.5928 points** over score relationships and the matched indicator. This comparison adds both geometry and two single-branch source indicators, reflecting their joint contribution. The independent contribution of geometric disagreement itself is directly tested in Section 4.5 by changing only the distance penalty with fixed candidates. The two ablations answer different questions: independent geometric information and learned combinations of relationships.

**Table 4. AP at different matching tolerances for complete GeoRank on the five held-out scenes.**

| Center-distance tolerance | Base ranking | GeoRank | Gain |
|---|---:|---:|---:|
| 0.5 m | 14.1289 | **16.5107** | **+2.3818** |
| 1 m | 26.2982 | **28.5044** | **+2.2062** |
| 2 m | 47.0544 | **48.1168** | **+1.0624** |
| 4 m | 67.3154 | **67.3386** | **+0.0232** |
| Mean over four tolerances | 38.6992 | **40.1176** | **+1.4184** |

Improvements concentrate at stricter matching tolerances. Since box positions are unchanged, this indicates more effective ranking of existing candidates under strict localization criteria, not direct improvement in coordinate accuracy.

Applying the same ranker to all 1,490 validation frames yields **40.5008** vehicle AP and **15.6307** three-class mAP under official detection evaluation, above the same-scope base scores of 39.2635 / 15.2182. Another completed configuration, using 1 m labels without normalized distance, obtains **40.3838 / 15.5917**. Both include fitting scenes and serve only as development references. Their saved 45.0180 AMOTA comes from reused base trajectories.

### 4.5 Ablations: Geometric Scoring, Candidate Front End, and Stability

This section consolidates completed ablations to examine whether geometric disagreement affects ranking, which parts of base candidate processing are effective, and how sensitive scoring is to supervision and scene splits. All results come from existing experiment records.

| Ablation | Location | Main controls |
|---|---|---|
| Eight learned feature configurations | Table 3 | Identical candidates, labels, and scene split |
| Adding only geometric disagreement | Table 5(a) | Fixed candidates and geometry; scores only |
| Label tolerance, forward/reverse splits, per-scene results | Tables 5(b), 5(c) | Fitting and held-out scopes explicitly distinguished |
| Removing geometry weighting or base score adjustment | Table 5(d) | Same two-branch predictions and basic tracker |
| Matching bonus and single-branch scaling | Table 5(e) | Complete pipeline with each operation enabled or disabled |
| Restoring original parent scores | Table 5(f) | Fixed final candidates; no repeated deduplication |
| Upstream correction, fine-tuning, historical tracker breakdown | Appendix C.2 | Sequential controls and historical tracking reported separately |
| Neighboring rules and 16 parameter settings | Appendices C.1, C.3 | Same-cache rule comparisons and one-factor sweeps |

#### 4.5.1 Fixed Candidates: Changing Geometric Disagreement Scoring Only

To directly identify the effect of disagreement, we fix all 54,644 final candidates in the complete validation set, including their geometry, classes, sources, and single-branch scores. We do not rerun deduplication, truncation, or tracking, and add a center-distance penalty only to matched boxes. The coefficient $\lambda=0.04$ is selected on five development scenes and then applied to the other five held-out scenes.

**Table 5(a). Fixed-candidate geometric interventions and learned scoring. Each AP column compares methods within identical candidate and evaluation scopes.**

| Scoring condition | Full-validation vehicle AP | Internal-holdout vehicle AP | Held-out gain |
|---|---:|---:|---:|
| Base ranking, no disagreement term | 39.2635 | 38.6992 | — |
| Center-distance linear penalty only | **39.8553** | **39.4883** | **+0.7891** |
| Center-distance multiplicative penalty only | **39.8747** | **39.5038** | **+0.8046** |
| Learned GeoRank: 2 m labels, complete features | **40.5008†** | **40.1176** | **+1.4184** |

† The learned full-validation column includes ranker-fitting scenes. The complete-pipeline multiplicative result, 39.8746, and the fixed-candidate result here, **39.8747**, are recorded separately. Fixed explicit interventions preserve maximum recall at all four GT matching tolerances.

The linear rule improves full-validation and internal-holdout AP by **0.5918 / 0.7891**, directly establishing an independent ranking contribution from geometric disagreement. Learned GeoRank further exceeds the explicit linear rule by **0.6293 points** on the same holdout, suggesting that jointly learning candidate relationships provides additional benefits. We also select parameters for nine explicit formulas using development AP only. Their held-out AP ranges from **39.0534 to 39.5038**, all above the base 38.6992. The usefulness of geometry is therefore not limited to a single linear expression. The complete 54-setting scan is available in the supplementary score archive.

#### 4.5.2 Supervision Tolerance and Scene Splits

**Table 5(b). Label-generation tolerance ablation. All conditions share the five-scene fitting / five-scene holdout split and base AP of 38.6992. Label tolerance differs from the four AP evaluation tolerances.**

| Label tolerance | Complete GeoRank held-out AP | Gain | Without normalized distance | Gain |
|---|---:|---:|---:|---:|
| 0.5 m | 38.2063 | −0.4929 | 38.7705 | +0.0712 |
| 1 m | **40.2391** | **+1.5399** | **40.1840** | **+1.4848** |
| 2 m (default) | **40.1176** | **+1.4184** | **40.0876** | **+1.3883** |
| 4 m | **40.0528** | **+1.3536** | **39.9628** | **+1.2635** |

Labels at 1–4 m give positive gains. Complete features with 0.5 m labels degrade performance, showing that overly strict supervision does not necessarily improve multi-tolerance AP. Complete features with 1 m labels reach **40.2391** in this comparison; we retain this as a sensitivity result rather than replace the default 2 m configuration after observing results.

Both split directions are evaluated with 1 m labels. The original direction improves from 38.6992 to **40.2391 (+1.5399)**. Swapping fitting and held-out scenes improves from 39.9648 to **40.7097 (+0.7450)**. The version without normalized distance gains **1.4848 / 0.5380**, respectively. Both directions show improvements, but both use validation scenes already involved in method development.

**Table 5(c). Per-scene held-out results for complete GeoRank with 1 m labels in the original split direction. Each scene has 149 frames; all five improve.**

| Held-out scene | Base AP | GeoRank AP | Gain |
|---|---:|---:|---:|
| scene_36 | 52.8036 | **53.8786** | **+1.0750** |
| scene_39 | 60.3050 | **65.1133** | **+4.8084** |
| scene_4 | 23.8521 | **24.0682** | **+0.2160** |
| scene_45 | 41.7780 | **42.9620** | **+1.1840** |
| scene_8 | 35.8493 | **36.6073** | **+0.7579** |

A simple average of per-scene AP cannot replace pooled evaluation AP. Together with fixed-candidate interventions and eight feature ablations, these results support GeoRank's scoring contribution. We next report existing base-front-end ablations to explain the candidate processing on which the additional ranking operates.

#### 4.5.3 Base Candidate Front-End Modules

On the complete 55 m validation set, we fix both branches' predictions and the basic tracker, remove geometric weighting or base score adjustment, and rerun output processing. We also report subsequent GeoRank results to distinguish base-module effects from added disagreement scoring.

**Table 5(d). Front-end module ablations and subsequent explicit scoring over all 1,490 frames. AP changes are relative to base candidate fusion.**

| Setting | Vehicle AP | AP change | Vehicle AMOTA | Three-class mAP | Three-class AMOTA |
|---|---:|---:|---:|---:|---:|
| Without matched-candidate geometry weighting | 38.6412 | −0.6223 | 44.0547 | 14.9823 | 16.9169 |
| Without base fusion score adjustment | 37.5958 | −1.6676 | 42.9897 | 14.5130 | 15.3772 |
| Base candidate fusion (reference) | 39.2635 | — | 45.0180 | 15.2182 | 17.4278 |
| Add GeoRank explicit linear penalty | **39.8568** | **+0.5933** | 44.6052 | **15.3967** | 17.2492 |
| Add GeoRank explicit multiplicative penalty | **39.8746** | **+0.6111** | 44.6770 | **15.4067** | 17.2731 |

Removing geometry weighting retains pairing but selects the higher-scoring parent's geometry. Removing score adjustment disables both the matching bonus and single-branch scaling. The former reduces AP / AMOTA by 0.6223 / 0.9633 points; the latter reduces them by 1.6676 / 2.0283 points. Thus, both candidate geometry processing and base scoring contribute. Added disagreement scoring further improves AP when both are already enabled. Removal differences depend on other modules remaining active and cannot be summed as independent contributions.

#### 4.5.4 Matching Bonus, Single-Branch Scaling, and Fixed-Candidate Scoring

**Table 5(e). Base-score combinations and added GeoRank. Setting $\beta=0$ disables the matching bonus, and $\gamma=1$ disables single-branch discounting. Each row reruns the complete output pipeline.**

| Bonus $\beta$ | Scaling $\gamma$ | Disagreement scoring | Vehicle AP | Vehicle AMOTA | Three-class mAP | Three-class AMOTA |
|---|---|---|---:|---:|---:|---:|
| 0 | 1 | None | 37.5958 | 42.9897 | 14.5130 | 15.3772 |
| 0 | 0.85 | None | 39.2138 | 44.7973 | 15.1821 | 17.3133 |
| 0.10 | 1 | None | 37.9552 | 43.1025 | 14.6441 | 15.4506 |
| 0.10 | 0.85 | None (base reference) | 39.2635 | 45.0180 | 15.2182 | 17.4278 |
| 0.10 | 0.85 | Explicit linear | **39.8568** | 44.6052 | **15.3967** | 17.2492 |
| 0.10 | 0.85 | Explicit multiplicative | **39.8746** | 44.6770 | **15.4067** | 17.2731 |

Disabling single-branch discounting reduces base AP from 39.2635 to 37.9552, while disabling the matching bonus reduces it to 39.2138. Most of the current base-score benefit therefore comes from relative treatment of matched and single-branch candidates. With both base operations enabled, disagreement still adds **0.5933 / 0.6111 AP**.

**Table 5(f). Scoring interventions with fixed final candidates, without repeated deduplication or truncation.**

| Scoring condition | Full-validation vehicle AP |
|---|---:|
| Restore original scores for both matched and unmatched candidates | 37.5149 |
| Restore original scores for unmatched candidates only | 37.8800 |
| Restore maximum parent score for matched candidates only | 39.2138 |
| Base scoring (reference) | 39.2635 |
| Add linear center-disagreement penalty | **39.8553** |
| Add multiplicative center-disagreement penalty | **39.8747** |
| Learned GeoRank, full-validation development reference including fitting scenes | **40.5008** |

With boxes and candidates fixed, base scoring improves AP by **1.7486** over restoring both original scores. Explicit geometry then adds **0.5918 / 0.6112 AP**, separating the base scoring effect from additional disagreement effects. Table 5(e) reruns deduplication, whereas Table 5(f) fixes final candidates; their scores are not interchangeable. At 2 m recall of 0.5, the base front end reduces FP by 663 relative to direct merging. Its maximum recall is 67.1872%, below direct merging's 69.3455%. Subsequent explicit scoring with fixed candidates does not change maximum recall.

### 4.6 Object-Level Motivation: Available Candidates Still Need Appropriate Scores

Object-level analysis explains the need for scoring. At a score threshold of 0.20 and a same-class center distance below 2 m, there are 594 vehicle-only GT detections at 55 m. Of these, 263 already have cooperative candidates within 2 m, but their scores are insufficient. Candidate coverage and inadequate scoring should therefore be addressed separately.

**Table 6. Missing-detection types in cooperative outputs and base-fusion retention for vehicle-only GT observations. The operating point uses scores at least 0.20 and same-class center distance below 2 m.**

| Cooperative output status | Observations | Retained by fusion |
|---|---:|---:|
| No candidate within 2 m; candidate at 2–4 m | 270 | 209 |
| No same-class candidate within 4 m | 61 | 57 |
| Candidates within 2 m, all scoring below 0.20 | 263 | 239 |
| Total | 594 | 505 |

The 263 low-scoring nearby candidates account for 44.28% of vehicle-only observations. This motivates candidate quality scoring; GeoRank's actual ranking gains are established through the score interventions in Tables 3–5.

Real success and failure cases are discussed in Appendix C.4, including a high-scoring fused box crossing the GT matching tolerance. They show that generated boxes still require quality assessment. Object-level statistics at a fixed operating point do not replace AP or learned-scoring ablations.

### 4.7 Supplementary Validation: Ranking Gains from Few Fitting Scenes

To assess fitting a ranker with few scenes, we select eight 55 m scenes, totaling 1,192 frames, from the training split and run vehicle, UAV, and cooperative inference. The ranking module reads only independent vehicle and final cooperative outputs. The first six scenes, comprising 894 frames, are used for fitting; the remaining two, comprising 298 frames, are held out. There are 7,804 fitting vehicle candidates, including 3,409 positives, and 3,364 held-out vehicle candidates.

**Table 7. The train8 offline pilot. Results come from the current offline evaluation script and cannot be directly compared with official validation AP.**

| Center-distance tolerance | Base ranking | GeoRank | Gain |
|---|---:|---:|---:|
| 0.5 m | 74.1494 | **77.8126** | **+3.6632** |
| 1 m | 96.2214 | **98.1515** | **+1.9301** |
| 2 m | 96.9562 | **98.7702** | **+1.8140** |
| 4 m | 97.1699 | **98.8038** | **+1.6339** |
| Mean over four tolerances | 91.1242 | **93.3845** | **+2.2603** |

This result provides a positive signal for learned ranking on another scene split. It is held out at the ranker level; the underlying detector may have seen these training scenes. Moreover, consistency between prediction-range filtering in the offline script and the official evaluator has not been verified. The experiment supports small-sample exploration rather than a final official-validation claim, and its 2.2603-point gain is not added to AP in Table 1 or 2. Known differences between the two offline scripts are documented in Appendix B.

### 4.8 Communication Payload: Receiver-Side Enhancement with Unchanged Upstream Messages

We audit the remote cache across all ten scenes and 1,490 frames of the 55 m validation set and verify the historical sender manifest file by file. Base fusion and the cooperative baseline use the same single UAV message per frame; the independent vehicle branch uses only local observations. Input paths and hashes for explicit linear and multiplicative scoring match the main pipeline, and learned scoring also processes only existing local candidates. Thus, **GeoRank adds zero remote messages and zero input tensor payload relative to the cooperative baseline**.

**Table 8. Remote payload accounting on the complete 55 m validation set. Rates assume a fixed 10 Hz and use bytes per second (B/s), not bit/s. These are tensor-payload statistics, not wireless packet captures.**

| Accounting convention | Cooperative baseline B/s | Supplementation + GeoRank B/s | Added B/s |
|---|---:|---:|---:|
| Griffin paper: three fields, uniform 32-bit formula | 69,763.76 | 69,763.76 | **0** |
| Current four fields, valid-object message budget | 138,722.55 | 138,722.55 | **0** |
| Current four fields, all unpruned input slots | 18,750,722.55 | 18,750,722.55 | **0** |

The three conventions answer different questions. The paper's formula counts `query_feats`, `obj_idxes`, and `ref_pts` at four bytes per element, yielding approximately **69.76 kB/s**. The current implementation also reads `query_embeds`, and IDs are 64-bit. Counting all four fields using their actual types and retaining only valid objects gives a budget of approximately **138.72 kB/s**. However, the loader currently reads all slots before receiver-side filtering; the valid-object budget is not an implemented sender-pruned communication volume. Unpruned input tensors occupy approximately **1.875 MB/frame**, equivalent to **18.75 MB/s** at 10 Hz. Here kB and MB use decimal units. Localization and synchronization metadata, serialization, packet headers, and retransmissions are excluded.

Identical payloads follow from input reuse rather than a new compression algorithm. GeoRank therefore provides **performance gains with unchanged upstream message payload**. The complete system still communicates, and the independent vehicle branch and ranking add local computation. Table 8 supports an incremental comparison with the same cooperative baseline, not a ranking against all external methods under a unified communication budget.

### 4.9 Discussion and Scope

Using the same two-branch caches and basic tracker, we also compare source score reduction, confidence filtering, and fixed source discounts in Appendix C.1. These output-rule controls distinguish simple filtering from candidate relationship processing; their origins and adaptation scope are stated there.

The method has explicit failure modes. Base fusion may move an originally correct parent box outside the GT matching tolerance. Single-branch discounts may lower valid candidates below the operating threshold. Both branches may also share the same error, producing a high-scoring false positive despite geometric agreement. Disagreement is therefore a quality cue, not proof of correctness. The AP/AMOTA trade-off of explicit penalties further requires separate evaluation of detection ranking and trajectory generation.

We concentrate on 55 m vehicle gains within one cooperative framework. Generality across models, consistent improvements across classes, and end-to-end speed require additional experiments. Although the rescorer has few parameters, total system cost includes both prediction branches and candidate matching. Existing inference records cannot substitute for latency comparisons on identical hardware.

## 5. Conclusion

We propose GeoRank to strengthen late supplementation in aerial–ground cooperative perception through geometry-disagreement-aware ranking. On the complete Griffin-55m validation set, the explicit multiplicative variant achieves **39.87 vehicle AP and 44.68 vehicle AMOTA**, numerically exceeding all intermediate-fusion methods reported in Griffin Table 3 and surpassing the strongest reported method, CoopTrack, by **3.47 and 4.48 points**. Fixed-input and fixed-candidate experiments further explain this output enhancement: explicit geometric scoring adds **0.59 / 0.61 AP** over base fusion on complete validation; center disagreement alone adds **0.79 AP** on the internal holdout; and learned GeoRank adds **1.42 AP**. Complete-cache audits and input protocols also show that receiver-side supplementation and ranking **do not increase remote message payload relative to the cooperative baseline**. Together, performance, ablation, and payload evidence support using candidate geometric relationships for final quality assessment, improving outputs in high-altitude cooperation while preserving upstream messages. Future work will examine independent-test generalization and coordination between detection and tracking scores.

## References

[1] Junhao Xu, Yanan Zhang, Zhi Cai, and Di Huang. **CoSDH: Communication-Efficient Collaborative Perception via Supply-Demand Awareness and Intermediate-Late Hybridization.** CVPR, 2025. https://openaccess.thecvf.com/content/CVPR2025/html/Xu_CoSDH_Communication-Efficient_Collaborative_Perception_via_Supply-Demand_Awareness_and_Intermediate-Late_Hybridization_CVPR_2025_paper.html

[2] Jiahao Wang, Xiangyu Cao, Jiaru Zhong, et al. **Griffin: Aerial-Ground Cooperative Detection and Tracking Dataset and Benchmark.** AAAI, 2026. https://doi.org/10.1609/aaai.v40i12.37951

[3] H. Yu, W. Yang, J. Zhong, et al. **End-to-End Autonomous Driving through V2X Cooperation.** AAAI, 2025. https://arxiv.org/abs/2404.00717

[4] Jiahao Wang, Zhongwei Jiang, Wenchao Sun, et al. **SparseCoop: Cooperative Perception with Kinematic-Grounded Queries.** AAAI, 2026. https://arxiv.org/abs/2512.06838

[5] Jiahao Wang, Zikun Xu, Yuner Zhang, et al. **Long-SCOPE: Fully Sparse Long-Range Cooperative 3D Perception.** CVPR, 2026. https://openaccess.thecvf.com/content/CVPR2026/html/Wang_Long-SCOPE_Fully_Sparse_Long-Range_Cooperative_3D_Perception_CVPR_2026_paper.html

[6] Jiaru Zhong, Jiahao Wang, Jiahui Xu, et al. **CoopTrack: Exploring End-to-End Learning for Efficient Cooperative Sequential Perception.** ICCV, 2025. https://arxiv.org/abs/2507.19239

[7] Roman Solovyev, Weimin Wang, and Tatiana Gabruseva. **Weighted Boxes Fusion: Ensembling Boxes from Different Object Detection Models.** Image and Vision Computing, 2021. https://arxiv.org/abs/1910.13302

[8] Y.-T. Chen, J. Shi, Z. Ye, et al. **Multimodal Object Detection via Probabilistic Ensembling.** ECCV, 2022. https://arxiv.org/abs/2104.02904

[9] Su Pang, Daniel Morris, and Hayder Radha. **CLOCs: Camera-LiDAR Object Candidates Fusion for 3D Object Detection.** IROS, 2020. https://arxiv.org/abs/2009.00784

[10] D. Tsai, J. S. Berrio, M. Shan, et al. **MS3D: Leveraging Multiple Detectors for Unsupervised Domain Adaptation in 3D Object Detection.** ITSC, 2023. https://arxiv.org/abs/2304.02431

[11] Yiming Cui, Liang Li, Haibing Yin, et al. **Expert-Teacher-Student Collaborative Learning for Domain Adaptive Object Detection.** CVPR, 2026. https://openaccess.thecvf.com/content/CVPR2026/html/Cui_Expert-Teacher-Student_Collaborative_Learning_for_Domain_Adaptive_Object_Detection_CVPR_2026_paper.html

[12] Haochen Yang, Baolu Li, Lei Li, et al. **Unsupervised Multi-agent and Single-agent Perception from Cooperative Views.** CVPR, 2026. https://openaccess.thecvf.com/content/CVPR2026/html/Yang_Unsupervised_Multi-agent_and_Single-agent_Perception_from_Cooperative_Views_CVPR_2026_paper.html

[13] Xinshuo Weng, Jianren Wang, David Held, and Kris Kitani. **3D Multi-Object Tracking: A Baseline and New Evaluation Metrics.** IROS, 2020. https://arxiv.org/abs/1907.03961

## Appendix A. Implementation Details and Result Identities

### A.1 Underlying Networks and Candidate Processing

The shared front end uses an association threshold $D_{vc}=\min(2.0,\max(0.8,\tfrac12\min(\ell_v,\ell_c)))$. Valid pairs require $d_{vc}\leq D_{vc}$, a height difference no greater than the larger box height, and size ratios no greater than 2 in every dimension. Let $r_j=\max(s_j^v/s_j^c,s_j^c/s_j^v)$. The pairing cost is

$$
\begin{aligned}
C_{vc}={}&\frac{d_{vc}}{D_{vc}}+\frac{0.20}{3}\sum_{j=1}^{3}\log r_j\\
&+0.15(1-|\cos(\theta_v-\theta_c)|).
\end{aligned}
$$

Invalid associations are discarded after Hungarian assignment. Matched boxes average centers, sizes, and velocities with $\omega_v=p_v^2/(p_v^2+p_c^2)$ and $\omega_c=1-\omega_v$. Unmatched boxes retain original geometry. Letting $m=\max(p_v,p_c)$, the shared base score is

$$
s_0=\begin{cases}
\min(0.999,m+\beta(1-m)\sqrt{p_vp_c}), & b\in\mathcal M,\\
\gamma p, & b\in\mathcal U^v\cup\mathcal U^c,
\end{cases}
$$

with $\beta=0.10$ and $\gamma=0.85$.

The Control cooperative branch is initialized from official 55 m weights and fine-tuned for four epochs over 5,960 training frames, totaling 23,840 frame steps. We use AdamW with base learning rate $2\times10^{-5}$, weight decay 0.01, one-GPU micro-batch size 1, gradient accumulation over eight steps, and seed 3407. The image backbone and neck, BEV encoding and embeddings, temporal query interactions, memory bank, initial queries, and reference points are frozen. Updates primarily affect the detection decoder, classification and regression heads, and cooperative fusion components. The new ranker does not retrain these parameters.

Candidate filtering removes nonfinite values and nonpositive sizes. The minimum score is 0.005, and the minimum score for pairing is 0.03. For matched rotations, normalized quaternions satisfying $|\mathbf q_v^\top\mathbf q_c|\geq\cos(\pi/4)$ are aligned to the same hemisphere, weighted, and normalized. Otherwise, the higher-scoring parent's rotation is used. For same-class candidates with center distance below 0.65 m and height difference below 1 m, the lower-scoring candidate is suppressed. At most 500 boxes are output. This is center-distance deduplication, not standard IoU NMS.

The basic tracker uses a planar constant-velocity Kalman state and same-class Hungarian association. For vehicles, the base association threshold is 3 m, the candidate-association and track-birth score threshold is 0.20, confirmation requires two hits, the score threshold for immediate output is 0.65, and maximum retention is 0.50 s. The tracker resets at scene boundaries. All complete-pipeline controls share this configuration.

### A.2 Scene Splits

Internal-validation fitting scenes are `scene_14`, `scene_17`, `scene_19`, `scene_21`, and `scene_3`. Held-out scenes are `scene_36`, `scene_39`, `scene_4`, `scene_45`, and `scene_8`. Explicit fixed-candidate rules and learned ranking share this 5/5 split but differ in parameter selection and training.

The train8 fitting scenes are `scene_0`, `scene_1`, `scene_2`, `scene_5`, `scene_6`, and `scene_7`; held-out scenes are `scene_9` and `scene_10`. The ranker fits only on the first six scenes, and feature standardization is estimated on the fitting set alone.

### A.3 Original System versus Controlled Baseline

The historical original UniV2X cooperative system achieves vehicle AP / AMOTA of 32.1785 / 35.0525, close to but not numerically identical to Griffin's reported 32.3 / 34.9. The 31.9480 / 35.2971 values referred to in the source draft's local comparison come from Control cooperative predictions with the common basic tracker, a different system configuration. Control belongs to the UniV2X framework and must not be described as reported or reproduced CoopTrack. The main comparison distinguishes literature performance from local controlled gains.

Base fusion improves AP / AMOTA over the historical original system by approximately +7.0850 / +9.9655, and over the controlled cooperative baseline by +7.3155 / +9.7209. These differences are not interchangeable.

## Appendix B. Differences between train8 Offline Evaluations

This appendix supports internal reproducibility review and explains the two saved train8 result sets. Neither script provides new AMOTA conclusions.

| Item | `train8/rank` | `train8/rank_eval` |
|---|---|---|
| Held-out vehicle AP | 91.1242 to **93.3845** | 50.9277 to **52.3256** |
| Held-out gain | **+2.2603** | **+1.3979** |
| GT filtering | `num_lidar_pts > 0`; horizontal GT distance below 50 m | Neither filter applied |
| Label tolerance | 2 m | 1 m |
| Label assignment | One-to-one greedy by distance | Greedy in base-score order |
| Normalized-distance feature | Included | Excluded |
| Consistency with official prediction-range filtering | Not yet verified | Not yet verified |

Different GT sets change the recall denominator and are an important reason for the large absolute AP difference. The lower-scoring version cannot therefore be called a stricter official result. Table 7 retains `rank` as an explicitly identified pilot; neither replaces official validation results. Next, the same model and candidates should be frozen and evaluated with unified official GT and prediction filtering, resolving protocol consistency before interpreting performance differences.

## Appendix C. Supplementary Controls and Parameter Sensitivity

### C.1 Neighboring Rules and Geometry Selection

**Table C1. Supplementary controls using the same two-branch 55 m caches and tracker, with base and subsequent higher-AP results.**

| Rule | Vehicle AP | Vehicle AMOTA |
|---|---:|---:|
| Direct merge and deduplication | 36.6080 | 38.1437 |
| Scale all vehicle-source scores by 0.85 | 34.9434 | 36.2631 |
| Confidence filtering + source discount [1]: threshold 0.30, vehicle factor 0.90 | 34.1737 | 36.7087 |
| Confidence filtering + source discount [1]: threshold 0.30, vehicle factor 0.80 | 34.1098 | 36.2947 |
| Cooperative-parent geometry after matching, base scores | 38.1582 | 41.7356 |
| Vehicle-parent geometry after matching, base scores | 38.9710 | 44.6594 |
| Higher-scoring-parent geometry after matching, base scores | 38.6412 | 44.0547 |
| Base fusion (scoring reference) | 39.2635 | 45.0180 |
| GeoRank explicit linear disagreement | **39.8568** | 44.6052 |
| GeoRank explicit multiplicative disagreement | **39.8746** | 44.6770 |

The two filtering-and-discounting rules are inspired by [1] and adapted to current independent receiver-vehicle outputs and common center-distance deduplication. They are local rule controls, not a Griffin reproduction of that paper's complete method.

Geometric averaging adds 0.2925 AP over choosing vehicle-parent geometry, while added explicit scoring improves the base reference by another **0.5933 / 0.6111 AP**. Geometry fusion and geometric relationship scoring are different operations, and their contributions are compared separately.

### C.2 Upstream Predictions and Tracking Configurations

**Table C2(a). Sequential upstream controls and subsequent scoring. The first three rows share the basic tracker and vary upstream predictions. Rows 4–5 are tracking references; the final rows add geometry scoring with fixed Control inputs.**

| Setting | Vehicle AP | Vehicle AMOTA | Three-class mAP | Three-class AMOTA |
|---|---:|---:|---:|---:|
| Original official model + same fusion and basic tracking | 39.0399 | 42.9624 | 15.0011 | 15.3831 |
| Coordinate correction, no fine-tuning + same fusion and basic tracking | 38.9889 | 44.2231 | 15.1313 | 16.7000 |
| Control + complete base fusion and basic tracking | 39.2635 | 45.0180 | 15.2182 | 17.4278 |
| Control + complete base fusion and complex tracking reference | 39.2634 | 44.5660 | 15.2191 | 15.6024 |
| Control + complete base fusion, no additional tracking | 39.2635 | — | 15.2182 | — |
| Control + GeoRank explicit linear disagreement and basic tracking | **39.8568** | 44.6052 | **15.3967** | 17.2492 |
| Control + GeoRank explicit multiplicative disagreement and basic tracking | **39.8746** | 44.6770 | **15.4067** | 17.2731 |

Base AP with original weights, corrected but unfine-tuned weights, and Control is 39.0399, 38.9889, and 39.2635, respectively. Added disagreement raises AP to **39.8568 / 39.8746**. Upstream changes are sequential controls; additional scoring is compared with fixed Control inputs.

The complex-tracking reference achieves 44.5660 vehicle AMOTA, below the basic configuration's 45.0180. More complex tracking does not further improve this metric here. This comparison explains the choice of the basic configuration and is not a new tracking contribution.

**Table C2(b). Historical complex-tracker breakdown over all 1,490 frames. The reference is Control + base candidate fusion + historical complex tracking. None of these conditions uses subsequent GeoRank disagreement scoring.**

| Historical tracking configuration | Vehicle AP | Vehicle AMOTA | Three-class mAP | Three-class AMOTA |
|---|---:|---:|---:|---:|
| Complete historical complex tracker | 39.2634 | 44.5660 | 15.2191 | 15.6024 |
| Without secondary association of weak detections | 39.2631 | 43.6091 | 15.2197 | 17.1499 |
| Without short-term prediction-based gap filling | 39.2634 | 44.5840 | 15.2191 | 15.6973 |
| Without temporal score bonuses | 39.2635 | 44.5506 | 15.2182 | 15.5973 |
| Replace with basic motion tracking | 39.2635 | 45.0180 | 15.2182 | 17.4278 |

Removing secondary association for weak detections lowers vehicle AMOTA, while short-term gap filling and temporal score bonuses have smaller effects. The complete complex tracker does not outperform the basic configuration. This table supports tracker selection; it is not the same experiment as the base-tracker front-end ablations in Table 5(d), and tracking changes must not be attributed to geometric scoring.

An existing ungated control also shows that, under the same training budget, gating improves cooperative-network AP / AMOTA by 0.4680 / 1.1479 points, but reduces both by 0.0242 / 0.2363 points after adding identical fusion and historical tracking. Final scoring experiments therefore fix the ungated Control upstream model. This is a single-seed comparison, and network-output and complete-system results are considered separately.

### C.3 Base-Fusion Parameter Sensitivity

With fixed predictions on the same 55 m validation set, 16 unique parameter configurations cover four one-factor sweeps. Each changes one parameter while keeping others at defaults. The sweeps share the default configuration, so their condition counts cannot simply be added.

**Table C3. Parameter sweeps and vehicle metric spans. A span is the maximum minus minimum along one sweep, in percentage points.**

| Parameter | Default | Values | Vehicle AP span | Vehicle AMOTA span |
|---|---|---|---:|---:|
| Maximum pairing distance (m) | 2.0 | 1.0, 1.5, 2.0, 2.5, 3.0 | 0.2073 | 1.8847 |
| Single-branch scaling $\gamma$ | 0.85 | 0.70, 0.80, 0.85, 0.90, 1.00 | 1.3413 | 1.9155 |
| Matching bonus $\beta$ | 0.10 | 0, 0.05, 0.10, 0.15, 0.20 | 0.0959 | 0.2682 |
| Geometry weighting exponent | 2 | 1, 1.5, 2, 3 | 0.0794 | 0.2521 |

Within the tested ranges, vehicle AP varies relatively little with the matching bonus and geometry exponent and is more sensitive to single-branch scaling. Vehicle AMOTA varies more with pairing distance and single-branch scaling. Pairing distance is additionally bounded by candidate length, so a flat curve alone does not imply that the threshold is ineffective. Class behavior also differs: bicycle AMOTA spans 6.0430 points along the single-branch scaling sweep.

This is completed development-set parameter sensitivity analysis. We retain the original defaults rather than replace the main result with the highest AP or AMOTA from a sweep. It is not evidence of multi-seed stability. All 16 settings and three-class results remain available through the internal source records.

### C.4 Real Cases and Parent-Box Errors

In a successful supplementation case, base fusion retains a target detected by the independent vehicle branch but missed by the cooperative branch in the same 55 m sample. This illustrates candidate supplementation using existing predictions and GT; it does not show learned rescoring correcting box positions.

In a failure case, the cooperative parent has center error approximately 1.821 m, which increases to approximately 2.013 m after fusion, crossing the 2 m matching tolerance. The fused score nevertheless remains approximately 0.969. Neither high confidence nor geometric fusion guarantees a correct match, motivating separate analysis of geometry processing and quality ranking.

Among actual paired vehicle parents that individually match the same GT, the vehicle parent has the smaller center error in 50.30% of cases. This conditional-subset analysis is neither a full-dataset accuracy estimate nor an estimate of causal improvement.
