#!/usr/bin/env python
import roles

def test_roles():
    assert roles.roles["beginner"]["role"] == "system"
    assert roles.roles["intermediate"]["role"] == "system"
    assert roles.roles["expert"]["role"] == "system"
    assert roles.roles["decision_maker"]["role"] == "system"
    assert roles.roles["educator"]["role"] == "system"
    assert roles.roles["high_school_students"]["role"] == "system"
    assert roles.roles["healthcare_professionals"]["role"] == "system"
    assert roles.roles["researchers"]["role"] == "system"
    assert roles.roles["beginner"]["content"] == "You are a helpful assistant specialized in genomics. Your audience is beginners who have little or no prior knowledge of genomics. Explain concepts in simple terms and avoid excessive technical jargon."
    assert roles.roles["intermediate"]["content"] == "You are a knowledgeable assistant in genomics. Your audience is individuals with a basic understanding of genomics. Provide detailed explanations with moderate use of technical terms and ensure clarity by offering examples where necessary."
    assert roles.roles["expert"]["content"] == "You are an advanced assistant in genomics. Your audience consists of researchers and professionals in genomics. Provide in-depth explanations using precise terminology, and reference relevant studies or databases where appropriate."
    assert roles.roles["decision_maker"]["content"] == "You are a genomics consultant for decision-makers in healthcare or research. Your audience requires actionable insights and clear summaries. Focus on key points and provide concise recommendations supported by evidence."
    assert roles.roles["educator"]["content"] == "You are a genomics assistant for educators. Your audience consists of teachers and instructors who need clear explanations and illustrative examples to teach genomics to their students."
    assert roles.roles["high_school_students"]["content"] == "You are a genomics assistant for high school biology teachers. Explain complex genomics topics in a way that is understandable to high school students, using analogies and simple language."
    assert roles.roles["healthcare_professionals"]["content"] == "You are a genomics assistant for healthcare professionals. Your audience includes clinicians and genetic counselors. Provide clinically relevant information about genetic variants, including their association with diseases and actionable recommendations."
    assert roles.roles["researchers"]["content"] == "You are a genomics assistant for academic researchers. Focus on providing detailed explanations about genetic variants, their frequency in populations, and links to databases like ClinVar and dbSNP."


def get_varchat_test_sample():
    result = '''
data: {"answer": "", "cits": [{"pmid": "https://pubmed.ncbi.nlm.nih.gov/39075523/", "cit": "[1] Rwere F et al. (2024). \"Uncovering newly identified aldehyde dehydrogenase 2 genetic variants that lead to acetaldehyde accumulation after an alcohol challenge.\" Journal of translational medicine, 22(1)"}, {"pmid": "https://pubmed.ncbi.nlm.nih.gov/38277453/", "cit": "[2] Koyanagi YN et al. (2024). \"Genetic architecture of alcohol consumption identified by a genotype-stratified GWAS and impact on esophageal cancer risk in Japanese people.\" Science advances, 10(4)"}, {"pmid": "https://pubmed.ncbi.nlm.nih.gov/38519490/", "cit": "[3] Wang X et al. (2024). \"The aldehyde dehydrogenase 2 rs671 variant enhances amyloid beta pathology.\" Nature communications, 15(1)"}, {"pmid": "https://pubmed.ncbi.nlm.nih.gov/38462476/", "cit": "[4] Takashima S et al. (2024). \"Asian flush is a potential protective factor against COVID-19: a web-based retrospective survey in Japan.\" Environmental health and preventive medicine, 29()"}, {"pmid": "https://pubmed.ncbi.nlm.nih.gov/39401906/", "cit": "[5] Tokiya M et al. (2024). \"Asian flush gene variant increases mild cognitive impairment risk: a cross-sectional study of the Yoshinogari Brain MRI Checkup Cohort.\" Environmental health and preventive medicine, 29()"}, {"pmid": "https://pubmed.ncbi.nlm.nih.gov/39416436/", "cit": "[6] Chien PS et al. (2024). \"Examining the causal association between moderate alcohol consumption and cardiovascular risk factors in the Taiwan Biobank: a Mendelian randomization analysis.\" Frontiers in cardiovascular medicine, 11()"}, {"pmid": "https://pubmed.ncbi.nlm.nih.gov/38462538/", "cit": "[7] Deiana G et al. (2024). \"Contribution of infectious diseases to the selection of ADH1B and ALDH2 gene variants in Asian populations.\" Alcohol, clinical & experimental research, 48(5)"}, {"pmid": "https://pubmed.ncbi.nlm.nih.gov/38813240/", "cit": "[8] Rao H et al. (2024). \"Aldehyde dehydrogenase 2 rs671 a/A Genotype is Associated with an Increased Risk of Early Onset Coronary Artery Stenosis.\" International journal of general medicine, 17()"}, {"pmid": "https://pubmed.ncbi.nlm.nih.gov/39226171/", "cit": "[9] Li SY et al. (2024). \"Aldehyde dehydrogenase 2 preserves kidney function by countering acrolein-induced metabolic and mitochondrial dysfunction.\" JCI insight, 9(19)"}, {"pmid": "https://pubmed.ncbi.nlm.nih.gov/39641391/", "cit": "[10] Pan TY et al. (2024). \"Association of ADH1B and ALDH2 genotypes with the risk of lung adenocarcinoma.\" Pharmacogenetics and genomics, ()"}, {"pmid": "https://pubmed.ncbi.nlm.nih.gov/28939800/", "cit": "[11] Qu Y et al. (2017). \"Aldehyde Dehydrogenase 2 (ALDH2) Glu504Lys Polymorphism Affects Collateral Circulation and Short-Term Prognosis of Acute Cerebral Infarction Patients.\" Medical science monitor : international medical journal of experimental and clinical research, 23()"}, {"pmid": "https://pubmed.ncbi.nlm.nih.gov/38448893/", "cit": "[12] Xu H et al. (2024). \"SNP-based and haplotype-based genome-wide association on drug dependence in Han Chinese.\" BMC genomics, 25(1)"}, {"pmid": "https://pubmed.ncbi.nlm.nih.gov/38567307/", "cit": "[13] Liu R et al. (2024). \"The ALDH2 gene rs671 polymorphism is associated with cardiometabolic risk factors in East Asian population: an updated meta-analysis.\" Frontiers in endocrinology, 15()"}, {"pmid": "https://pubmed.ncbi.nlm.nih.gov/27706553/", "cit": "[14] Zhao S et al. (2016). \"Association between aldehyde dehydrogenase 2 (ALDH2) Glu504Lys polymorphism and susceptibility to colorectal cancer: a meta-analysis.\" Genetics and molecular research : GMR, 15(3)"}, {"pmid": "https://pubmed.ncbi.nlm.nih.gov/38177014/", "cit": "[15] Tang C et al. (2024). \"Aldehyde Dehydrogenase 2 (ALDH2) rs671 Polymorphism is a Predictor of Pulmonary Hypertension Due to Left Heart Disease.\" Heart, lung & circulation, 33(2)"}], "rcv_cit_count": 7, "rcv_cits": [{"link": "https://www.ncbi.nlm.nih.gov/clinvar/RCV001290000/", "rcv": "RCV001290000", "clinv_table": [{"type": "germline", "weight": 0.5, "rev_status": 0, "clin_sig": "Pathogenic", "clin_sig_map": "P"}], "min_weights": 0.5, "condition": "AMED syndrome, digenic"}, {"link": "https://www.ncbi.nlm.nih.gov/clinvar/RCV001787815/", "rcv": "RCV001787815", "clinv_table": [{"type": "germline", "weight": 6.2, "rev_status": 3, "clin_sig": "drug response", "clin_sig_map": "O"}], "min_weights": 6.2, "condition": "ethanol response - Toxicity"}, {"link": "https://www.ncbi.nlm.nih.gov/clinvar/RCV000020058/", "rcv": "RCV000020058", "clinv_table": [{"type": "germline", "weight": 6.5, "rev_status": 0, "clin_sig": "drug response", "clin_sig_map": "O"}], "min_weights": 6.5, "condition": "Alcohol sensitivity, acute"}, {"link": "https://www.ncbi.nlm.nih.gov/clinvar/RCV000020059/", "rcv": "RCV000020059", "clinv_table": [{"type": "germline", "weight": 6.5, "rev_status": 0, "clin_sig": "protective", "clin_sig_map": "O"}], "min_weights": 6.5, "condition": "Alcohol dependence"}, {"link": "https://www.ncbi.nlm.nih.gov/clinvar/RCV000020060/", "rcv": "RCV000020060", "clinv_table": [{"type": "germline", "weight": 6.5, "rev_status": 0, "clin_sig": "risk factor", "clin_sig_map": "O"}], "min_weights": 6.5, "condition": "Susceptibility to hangover"}, {"link": "https://www.ncbi.nlm.nih.gov/clinvar/RCV000020061/", "rcv": "RCV000020061", "clinv_table": [{"type": "germline", "weight": 6.5, "rev_status": 0, "clin_sig": "risk factor", "clin_sig_map": "O"}], "min_weights": 6.5, "condition": "Sublingual nitroglycerin, susceptibility to poor response to"}, {"link": "https://www.ncbi.nlm.nih.gov/clinvar/RCV000020062/", "rcv": "RCV000020062", "clinv_table": [{"type": "germline", "weight": 6.5, "rev_status": 0, "clin_sig": "risk factor", "clin_sig_map": "O"}], "min_weights": 6.5, "condition": "Esophageal cancer, alcohol-related, susceptibility to"}], "status_answer_code": 0, "status_info_code": false, "cit_count": 1181, "conversation_uuid": "f33d3627-f08e-4521-85a3-b9a0f51eb6ee", "triggering_question_lambda": false, "answer_uuid": ""}

data: 


data: The

data:  AL

data: DH

data: 2

data:  gene

data:  enc

data: odes

data:  the

data:  mitochondrial

data:  enzyme

data:  al

data: dehyde

data:  de

data: hydro

data: gen

data: ase

data:  

data: 2

data: ,

data:  which

data:  is

data:  crucial

data:  for

data:  the

data:  detox

data: ification

data:  of

data:  ac

data: etal

data: dehyde

data: ,

data:  a

data:  by

data: product

data:  of

data:  alcohol

data:  metabolism

data: ,

data:  as

data:  well

data:  as

data:  other

data:  al

data: dehy

data: des

data:  generated

data:  during

data:  lipid

data:  per

data: oxid

data: ation

data: .

data:  The

data:  c

data: .

data: 151

data: 0

data: G

data: >A

data:  p

data: .G

data: lu

data: 504

data: L

data: ys

data:  variant

data: ,

data:  known

data:  as

data:  rs

data: 671

data: ,

data:  results

data:  in

data:  an

data:  amino

data:  acid

data:  substitution

data:  at

data:  position

data:  

data: 504

data:  of

data:  the

data:  AL

data: DH

data: 2

data:  protein

data: ,

data:  from

data:  glut

data: amic

data:  acid

data:  to

data:  lys

data: ine

data: .

data:  This

data:  miss

data: ense

data:  variant

data:  has

data:  been

data:  associated

data:  with

data:  a

data:  significant

data:  decrease

data:  in

data:  enzym

data: atic

data:  activity

data: ,

data:  leading

data:  to

data:  an

data:  accumulation

data:  of

data:  ac

data: etal

data: dehyde

data:  upon

data:  alcohol

data:  consumption

data:  [

data: 1

data: ].



data: The

data:  rs

data: 671

data:  variant

data:  is

data:  prevalent

data:  in

data:  East

data:  Asian

data:  populations

data: ,

data:  with

data:  approximately

data:  

data: 30

data: -

data: 50

data: %

data:  of

data:  individuals

data:  carrying

data:  at

data:  least

data:  one

data:  A

data:  allele

data: ,

data:  compared

data:  to

data:  less

data:  than

data:  

data: 5

data: %

data:  in

data:  European

data:  populations

data: .

data:  Individuals

data:  who

data:  are

data:  heter

data: ozy

data: g

data: ous

data:  for

data:  this

data:  variant

data:  (

data: GA

data:  genotype

data: )

data:  exhibit

data:  an

data:  AL

data: DH

data: 2

data:  activity

data:  that

data:  is

data:  reduced

data:  to

data:  

data: 10

data: -

data: 45

data: %

data:  of

data:  that

data:  observed

data:  in

data:  individuals

data:  with

data:  the

data:  GG

data:  genotype

data: .

data:  Hom

data: ozy

data: g

data: ous

data:  individuals

data:  (

data: AA

data:  genotype

data: )

data:  have

data:  even

data:  more

data:  drastically

data:  reduced

data:  activity

data: ,

data:  at

data:  

data: 1

data: -

data: 5

data: %

data:  of

data:  the

data:  normal

data:  level

data:  [

data: 3

data: ].



data: This

data:  variant

data:  has

data:  been

data:  implicated

data:  in

data:  a

data:  range

data:  of

data:  alcohol

data: -related

data:  health

data:  issues

data: .

data:  H

data: eter

data: ozy

data: g

data: otes

data:  for

data:  rs

data: 671

data:  exhibit

data:  a

data:  heightened

data:  ac

data: etal

data: dehyde

data:  response

data:  following

data:  alcohol

data:  consumption

data: ,

data:  with

data:  breath

data:  ac

data: etal

data: dehyde

data:  levels

data:  pe

data: aking

data:  at

data:  nine

data: -fold

data:  higher

data:  than

data:  those

data:  with

data:  the

data:  wild

data: -type

data:  genotype

data: .

data:  This

data:  response

data:  is

data:  sustained

data: ,

data:  with

data:  significantly

data:  elevated

data:  ac

data: etal

data: dehyde

data:  levels

data:  for

data:  up

data:  to

data:  

data: 60

data:  minutes

data:  after

data:  alcohol

data:  intake

data:  [

data: 1

data: ].

data:  The

data:  increased

data:  ac

data: etal

data: dehyde

data:  accumulation

data:  is

data:  associated

data:  with

data:  facial

data:  flushing

data:  and

data:  other

data:  physiological

data:  responses

data:  to

data:  alcohol

data: .



data: In

data:  addition

data:  to

data:  its

data:  role

data:  in

data:  alcohol

data:  metabolism

data: ,

data:  AL

data: DH

data: 2

data:  activity

data:  has

data:  been

data:  linked

data:  to

data:  various

data:  disease

data:  risks

data: .

data:  The

data:  rs

data: 671

data:  variant

data:  has

data:  been

data:  associated

data:  with

data:  an

data:  increased

data:  risk

data:  of

data:  certain

data:  cancers

data:  and

data:  cardiovascular

data:  diseases

data:  following

data:  alcohol

data:  consumption

data: .

data:  Moreover

data: ,

data:  recent

data:  studies

data:  have

data:  explored

data:  the

data:  relationship

data:  between

data:  the

data:  rs

data: 671

data:  polym

data: orphism

data:  and

data:  Alzheimer

data: 's

data:  disease

data:  (

data: AD

data: ),

data:  with

data:  findings

data:  suggesting

data:  that

data:  while

data:  the

data:  variant

data:  affects

data:  amy

data: loid

data: -beta

data:  pathology

data: ,

data:  it

data:  is

data:  not

data:  an

data:  independent

data:  risk

data:  factor

data:  for

data:  AD

data:  [

data: 3

data: ].



data: The

data:  rs

data: 671

data:  variant

data:  has

data:  been

data:  under

data:  strong

data:  recent

data:  natural

data:  selection

data:  pressure

data:  in

data:  the

data:  Japanese

data:  population

data: ,

data:  indicating

data:  its

data:  potential

data:  evolutionary

data:  significance

data: .

data:  It

data:  is

data:  thought

data:  to

data:  be

data:  a

data:  relatively

data:  young

data:  variant

data:  and

data:  has

data:  been

data:  the

data:  subject

data:  of

data:  extensive

data:  research

data:  due

data:  to

data:  its

data:  impact

data:  on

data:  AL

data: DH

data: 2

data:  function

data:  and

data:  its

data:  associated

data:  health

data:  implications

data:  [

data: 2

data: ].



data: In

data:  summary

data: ,

data:  the

data:  c

data: .

data: 151

data: 0

data: G

data: >A

data:  p

data: .G

data: lu

data: 504

data: L

data: ys

data:  rs

data: 671

data:  variant

data:  on

data:  the

data:  AL

data: DH

data: 2

data:  gene

data:  is

data:  a

data:  miss

data: ense

data:  variant

data:  that

data:  leads

data:  to

data:  a

data:  substantial

data:  reduction

data:  in

data:  al

data: dehyde

data:  de

data: hydro

data: gen

data: ase

data:  activity

data: ,

data:  with

data:  significant

data:  consequences

data:  for

data:  alcohol

data:  metabolism

data:  and

data:  associated

data:  disease

data:  risks

data: .

data:  This

data:  variant

data:  is

data:  particularly

data:  prevalent

data:  in

data:  East

data:  Asian

data:  populations

data:  and

data:  has

data:  been

data:  the

data:  focus

data:  of

data:  numerous

data:  studies

data:  investigating

data:  its

data:  effects

data:  on

data:  human

data:  health

data:  [

data: 1

data: ][

data: 2

data: ][

data: 3

data: ].
'''

    return result