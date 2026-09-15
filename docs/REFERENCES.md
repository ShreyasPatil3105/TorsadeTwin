# References

Machine-readable register: `docs/REFERENCES.json` (rendered here).

| id | Source | DOI | Used for |
|---|---|---|---|
| ohara2011 | O'Hara T, Virag L, Varro A, Rudy Y. Simulation of the undiseased human cardiac ventricular action potential. PLoS Comput Biol 2011;7(5):e1002061 | 10.1371/journal.pcbi.1002061 | cell model physiology, control APD90 reference |
| dutta2017 | Dutta S, et al. Optimization of an in silico cardiac cell model for proarrhythmia risk assessment. Front Physiol 2017;8:616 | 10.3389/fphys.2017.00616 | conductance scaling, qNet definition, CL=2000ms protocol |
| li2017 | Li Z, et al. Circ Arrhythm Electrophysiol 2017;10:e004628 | 10.1161/CIRCEP.116.004628 | CiPA v1.0 model provenance (dynamic binding disabled, D1); IC50 table reproduction |
| li2019 | Li Z, et al. Clin Pharmacol Ther 2019;105:466-475 | 10.1002/cpt.1184 | qNet threshold reference band (non-comparable), free C_max, prior-art labels |
| crumb2016 | Crumb WJ Jr, et al. J Pharmacol Toxicol Methods 2016;81:251-262 | 10.1016/j.vascn.2016.03.009 | multichannel IC50 / Hill parameters |
| tisdale2013 | Tisdale JE, et al. Circ Cardiovasc Qual Outcomes 2013;6:479-487 | 10.1161/CIRCOUTCOMES.113.000152 | clinical score for the blind-spot audit |
| physiome_cipa | Physiome Model Repository exposure `ohara_rudy_cipa_v1_2017.cellml` | https://models.cellml.org/e/5a0 | the model artefact itself |
| fda_cipa | FDA/CiPA reference C implementation (GPL-3.0) | https://github.com/FDA/CiPA | independent numerical reference; **code not copied** |

CredibleMeds QT-risk lists are **not redistributed**; the optional `qt_risk_class_manual` field is user-entered locally only (§13.5).
