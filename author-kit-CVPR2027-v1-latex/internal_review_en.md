# Appendix D. Internal Review Plan and Evidence Index

This file translates the source draft's internal review appendix. It is excluded from the paper and supplementary LaTeX documents.

## D.1 Positioning after This Revision

The method is consistently named **GeoRank**, or geometry-disagreement-aware ranking. Explicit linear and multiplicative penalties and learned rescoring belong to the same line of work, demonstrating direct geometric intervention and joint relationship learning, respectively. The base candidate front end and base scores are shared references; complete formulas remain in Appendix A. Base-module, score-combination, and fixed-candidate ablations have been moved into main-text Tables 5(d–f), and the historical tracking breakdown is included in Table C2(b). Base scores are not presented separately as the method's best results.

The central argument is: **geometric disagreement scoring strengthens late supplementation and achieves vehicle performance on Griffin-55m above the benchmark's published intermediate-fusion methods; fixed-input, fixed-candidate, and scene-level experiments explain these gains.** The abstract, introduction, contributions, main results, and conclusion consistently emphasize this performance positioning while retaining the independent ranking effect of explicit geometry. Key GeoRank scores and gains are bold; historical versions and base references use regular weight. The source revision notes state that V1–V7 appear in Table 1(b), with remaining complete scores in the all-versions-and-ablations archive. **Translation audit: the supplied source actually contains no Table 1(b); no missing rows have been invented.**

The unchanged-remote-payload claim appears in the abstract, introduction, fourth contribution, Section 4.8, and conclusion. Evidence comes from the complete 55 m cache audit and identical-input protocols for subsequent ranking. The paper-formula rate of 69,763.76 B/s, four-field valid-object budget of 138,722.55 B/s, and unpruned-input equivalent of 18,750,722.55 B/s are all retained, preventing an effective budget from being described as actual network traffic.

Table 1(a) retains all seven Griffin Table 3 baselines and emphasizes published intermediate-fusion results. The explicit multiplicative variant's **39.87 AP / 44.68 AMOTA** exceeds reported CoopTrack by **3.47 / 4.48 points**. Early Fusion remains a separate high-communication-cost reference. Without a unified budget or cross-method communication measurements, this category comparison is not recast as unconditional state of the art or state of the art under a communication budget. Learned full-validation development **40.5008**, default internal holdout **40.1176**, 1 m-label holdout **40.2391**, reversed split **40.7097**, and train8 offline **93.3845** retain their respective configurations and evaluation scopes; they are not combined into one test result.

Related work briefly cites intermediate–late hybrid cooperation. The method contribution is stated as incorporating geometric disagreement between independent vehicle and already cooperative predictions into final scoring. Existing candidate fusion and geometric rescoring remain necessary background; the specific method, fixed-candidate evidence, and 55 m performance support the positioning.

Existing fixed-candidate interventions directly establish the independent ranking effect of explicit geometry; it would be inaccurate to say that geometry's independent contribution remains unproven. The gap between complete learned features and score-only features also involves source indicators, whose contributions can be further separated. Reused base trajectories are still not new tracking gains from learned ranking.

## D.2 Minimal Next Steps

| Priority | Work | Paper location | Issue resolved |
|---|---|---|---|
| 1 | Freeze the existing train8-fitted ranker and score the complete 55 m validation cache under the official protocol | Tables 3, 7; abstract | Separate ranker training from validation evaluation without expanding fitting to 40 scenes |
| 2 | Beyond the completed fixed-candidate geometry intervention, hold sources, scores, and training configuration constant and only add/remove geometric features in the learned model | Tables 3, 5(a) | Disaggregate joint learned gains while retaining established explicit-geometry evidence |
| 3 | Run and audit trajectories under the final detection/tracking score interface; explicitly disclose any reused trajectories | Sections 3.5, 4.3 | Determine the new module's actual AMOTA effect |
| 4 | Supplement the completed Table 3 literature comparison with same-setting reproductions of the most relevant methods | Tables 1(a), 1(b) in the source plan | Move from literature-value comparison toward common-protocol comparison |
| 5 | Measure cached postprocessing latency and peak memory; separately report independent-branch overhead | Sections 3.5, 4.8 | Turn low parameter count and output-level interfacing into verifiable cost claims |

These are options for subsequent work. The source revision completed manuscript rewriting, public-table auditing, and figure generation without starting new data extraction, training, inference, or model evaluation. This translation likewise does not run new perception experiments.

## D.3 Main-Text Compression and Figure Plan

The current manuscript is a complete-content draft. The source plan allocates approximately 1.25 pages to the introduction, 0.75 to related work, 2 to methods, 3.5 to experiments, and 0.25 to the conclusion in CVPR two-column format. Abstract, tables, figures, and whitespace must be adjusted together according to the target-year template. References and supplementary material are arranged separately. This translation preserves content rather than claiming compliance with the final main-paper page limit.

The source embeds five main figures: concept, pipeline, grouped additional gains from explicit and learned scoring, ranking and feature comparisons, and object-level motivation. Key GeoRank scores and gains are bold in Figures 3 and 4. Appendix figures cover parameter sensitivity, success/failure cases, and parent errors. Their index and review PDF remain in the existing figure directory. Per the current request, no images are embedded in the English template; translated captions are stored separately.

Visual organization draws on Long-SCOPE's grouped pipeline and local expansions and SparseCoop's sequential modules and training/inference distinction. All graphics and data were redrawn for this project. AP–AMOTA bubble plots in those references also encode communication cost; this project lacks measurements on a common basis and therefore does not copy their bubble-size encoding. SparseCoop is listed as AAAI 2026 and Long-SCOPE as CVPR 2026.

For eventual two-column compression, prioritize the GeoRank result overview, learned ablations in Table 3, independent geometry intervention in Table 5(a), base-module ablation in Table 5(d), and payload Table 8. The review draft retains score breakdowns in Tables 5(e–f); final placement follows page-layout editing. Front-end formulas and historical tracking breakdowns remain in the appendix. Table 4 and Figure 4, and detailed object statistics and Figure 5, can be combined to reduce duplication.

## D.4 Evidence Index

The original local paths and hyperlinks are preserved in the Chinese source's Appendix D.4. The following English index maps the translated content to the same records; paths remain local review material rather than paper citations.

| Content | Original record |
|---|---|
| All published baselines in Table 1(a) | Griffin Table 3, PDF page 6; literature/griffin_table3_audit_zh.md; figure-directory griffin_table3_55m.csv |
| No additional remote inputs from receiver-side supplementation | griffin55m_main_method_20261026/communication_results.md |
| Table 8 and input reuse | communication_results.json; complete_55m/55m/protocol.json; complete_55m_multiplicative/55m/protocol.json; logistic_variant_official/variant_protocol.json |
| Historical V1–V7, Control, and complete score archive | Existing all-experiment summary and all-versions-and-ablations score document |
| Base reference and front-end controls | griffin55m_main_method_20261026/accuracy_results.md |
| Historical tracker and gating controls | griffin55m_control_ablation_20261025/results.md; griffin55m_control_20261025/results.md |
| Base parameters and score combinations | griffin55m_sensitivity_20261101/results.md; base-pipeline accuracy_results.md |
| GeoRank overview and subset gains | Separate explicit, learned, full-validation development, and train8 metric files listed below |
| Table 2, explicit complete pipeline | griffin_disagreement_rank/report_zh.md; complete_55m/results.md |
| Table 2, multiplicative rule | complete_55m_multiplicative/results.md |
| Tables 3–4 and 5/5 split | logistic_pilot/metrics.json; logistic_pilot_ablation/ablation.csv |
| Full-validation 40.5008 and trajectory identity | logistic_variant_official/complete.json; variant_protocol.json |
| Full-validation 40.3838 and trajectory identity | logistic_variant_1m_no_norm_official/complete.json; variant_protocol.json |
| Independent geometry interventions and nine formulas | fixed_ap/score_summary.csv; fixed_ap/ap_by_distance.csv; adaptive_scan/selected.json |
| Label tolerance and reversed split | logistic_label_threshold_scan/threshold_summary.csv; logistic_reverse_split/reverse_summary.csv |
| Table 5(c), 1 m-label scene results | logistic_per_scene.csv; logistic_per_scene.py |
| Table 5(f), base-score interventions and recall | Existing ranking/README_纯排序实验结果.md |
| Table 6 and object-level examples | Existing object-level complementarity/fusion-error report and deep-mechanism report |
| Figures 1–5, S1, and case exports | Existing figure-directory README.md, generation scripts, and source records |
| Table 7 | train8/rank/metrics.json; train8/run_rank_train8.py |
| Alternative evaluation in Appendix B | train8/rank_eval/metrics.json; train8/train8_rank_eval.py |
| Table C1 | Existing baseline/results.md in the mechanism-and-neighbor-control directory |
| Related-work positioning | Existing geometry-disagreement-ranking novelty and literature-search note |

These records are for local review. Anonymous submission should remove internal paths, development logs, and identity information and organize necessary implementation and evaluation protocols as anonymous supplementary material.
