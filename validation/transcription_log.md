# Transcription log (§5.6, §15.2)
#
# EVERY IC50, Hill, C_max and Tisdale item/point value MUST be transcribed by a human from
# the cited source table, entered with source_table and source_doi, marked
# verification_status: VERIFIED, and double-entered by a second team member (reviewer).
# Until then rows stay PLACEHOLDER and the API returns E_PROVENANCE_INCOMPLETE.
#
# Primary sources:
#   - Crumb WJ Jr, Vicente J, Johannesen L, Strauss DG. J Pharmacol Toxicol Methods 2016;81:251-262.
#     doi:10.1016/j.vascn.2016.03.009  (multichannel IC50/Hill, Table 2)
#   - Li et al. 2019, Clin Pharmacol Ther 105:466-475, doi:10.1002/cpt.1184 (free C_max table)
#   - Tisdale JE et al. Circ Cardiovasc Qual Outcomes 2013;6:479-487, doi:10.1161/CIRCOUTCOMES.113.000152
#
# Format:
#   - id: <row id>
#     drug: <drug_id>
#     channel: <channel>
#     value: <value>
#     source_table: <table>
#     source_doi: <doi>
#     transcribed_by: <name>
#     transcribed_on: <date>
#     reviewer: <name>
#     reviewed_on: <date>
#     status: VERIFIED

status: PENDING
entries: []
